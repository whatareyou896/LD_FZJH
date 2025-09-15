import os
import time
import cv2
import numpy as np
import subprocess
import logging
from typing import Tuple, Optional, List, Dict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("jianghu_auto.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("JiangHuAuto")


class JiangHuAuto:
    def __init__(self, emulator_index: int = 0, template_dir: str = "templates"):
        """
        初始化自动化脚本

        Args:
            emulator_index: 模拟器索引（多开时使用）
            template_dir: 模板图片目录
        """
        self.emulator_index = emulator_index
        self.template_dir = template_dir
        self.screenshot_path = "screenshot.png"

        # 预加载模板图片
        self.templates = self._load_templates()

        logger.info(f"初始化自动化脚本，模拟器索引: {emulator_index}")

    def _load_templates(self) -> Dict[str, np.ndarray]:
        """加载所有模板图片"""
        templates = {}
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            logger.warning(f"模板目录 {self.template_dir} 不存在，已创建空目录")
            return templates

        for filename in os.listdir(self.template_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                name = os.path.splitext(filename)[0]
                template_path = os.path.join(self.template_dir, filename)
                templates[name] = cv2.imread(template_path, 0)  # 以灰度模式读取
                logger.debug(f"加载模板: {name}")

        logger.info(f"已加载 {len(templates)} 个模板图片")
        return templates

    def take_screenshot(self) -> bool:
        """
        截取模拟器屏幕

        Returns:
            bool: 是否成功截屏
        """
        try:
            # 使用雷电控制台命令截屏
            cmd = f"dnconsole.exe screenshot --index {self.emulator_index} --file {self.screenshot_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0 and os.path.exists(self.screenshot_path):
                logger.debug("截屏成功")
                return True
            else:
                logger.error(f"截屏失败: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"截屏异常: {str(e)}")
            return False

    def find_template(self, template_name: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        在屏幕中查找模板匹配的位置

        Args:
            template_name: 模板名称
            threshold: 匹配阈值

        Returns:
            Optional[Tuple[int, int]]: 匹配位置的坐标 (x, y)，未找到返回 None
        """
        if template_name not in self.templates:
            logger.error(f"模板 '{template_name}' 未找到")
            return None

        # 读取屏幕截图
        screenshot = cv2.imread(self.screenshot_path, 0)
        if screenshot is None:
            logger.error("无法读取截图文件")
            return None

        template = self.templates[template_name]

        # 模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # 计算中心点坐标
            h, w = template.shape
            x, y = max_loc
            center_x = x + w // 2
            center_y = y + h // 2
            logger.debug(f"找到模板 '{template_name}'，置信度: {max_val:.2f}, 位置: ({center_x}, {center_y})")
            return (center_x, center_y)
        else:
            logger.debug(f"未找到模板 '{template_name}'，最高置信度: {max_val:.2f}")
            return None

    def click(self, x: int, y: int, delay: float = 0.5):
        """
        点击指定坐标

        Args:
            x: 横坐标
            y: 纵坐标
            delay: 点击后的延迟时间（秒）
        """
        try:
            cmd = f"dnconsole.exe action --index {self.emulator_index} --key call.touch --value {x},{y}"
            subprocess.run(cmd, shell=True, capture_output=True)
            logger.debug(f"点击位置: ({x}, {y})")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"点击操作异常: {str(e)}")

    def click_template(self, template_name: str, threshold: float = 0.8) -> bool:
        """
        查找并点击模板

        Args:
            template_name: 模板名称
            threshold: 匹配阈值

        Returns:
            bool: 是否成功点击
        """
        if not self.take_screenshot():
            return False

        position = self.find_template(template_name, threshold)
        if position:
            x, y = position
            self.click(x, y)
            return True
        return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300, delay: float = 1.0):
        """
        滑动操作

        Args:
            x1, y1: 起始坐标
            x2, y2: 结束坐标
            duration: 滑动持续时间（毫秒）
            delay: 滑动后的延迟时间（秒）
        """
        try:
            cmd = f"dnconsole.exe action --index {self.emulator_index} --key call.swipe --value {x1},{y1},{x2},{y2},{duration}"
            subprocess.run(cmd, shell=True, capture_output=True)
            logger.debug(f"滑动: ({x1}, {y1}) -> ({x2}, {y2})")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"滑动操作异常: {str(e)}")

    def wait_for_template(self, template_name: str, timeout: int = 30, interval: float = 1.0,
                          threshold: float = 0.8) -> bool:
        """
        等待直到特定模板出现

        Args:
            template_name: 模板名称
            timeout: 超时时间（秒）
            interval: 检查间隔（秒）
            threshold: 匹配阈值

        Returns:
            bool: 是否在超时前找到模板
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.take_screenshot():
                position = self.find_template(template_name, threshold)
                if position:
                    logger.info(f"找到模板 '{template_name}'")
                    return True
            time.sleep(interval)

        logger.warning(f"等待模板 '{template_name}' 超时")
        return False

    def run_daily_tasks(self):
        """执行日常任务"""
        logger.info("开始执行日常任务")

        # 示例任务流程
        # 1. 检查并点击任务按钮
        if self.click_template("task_button"):
            logger.info("已点击任务按钮")
            time.sleep(2)

            # 2. 等待任务界面加载
            if self.wait_for_template("task_interface", timeout=10):
                # 3. 点击日常任务
                if self.click_template("daily_task"):
                    logger.info("已选择日常任务")
                    time.sleep(2)

                    # 4. 领取已完成的任务奖励
                    if self.click_template("claim_reward"):
                        logger.info("已领取任务奖励")
                        time.sleep(2)

        # 5. 返回主界面
        self.click(50, 50)  # 假设左上角有返回按钮

        logger.info("日常任务执行完成")

    def main_loop(self, interval: int = 300):
        """
        主循环

        Args:
            interval: 循环间隔时间（秒）
        """
        logger.info("启动主循环")

        try:
            while True:
                # 执行日常任务
                self.run_daily_tasks()

                # 执行其他任务...

                logger.info(f"等待 {interval} 秒后继续...")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("用户中断程序")
        except Exception as e:
            logger.error(f"主循环异常: {str(e)}")

        logger.info("主循环结束")


# 使用示例
if __name__ == "__main__":
    # 初始化自动化脚本
    auto = JiangHuAuto(emulator_index=0, template_dir="templates")

    # 启动主循环（每5分钟执行一次）
    auto.main_loop(interval=300)
