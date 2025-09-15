import os
import time
import cv2
import numpy as np
import logging
from typing import Tuple, Optional, List, Dict

# 引入底层模拟器控制
from Moni_Leidian import Dnconsole

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
        self.emulator_index = emulator_index
        self.template_dir = template_dir
        self.screenshot_path = os.path.join(Dnconsole.share_path, "apk_scr.png")
        self.templates = self._load_templates()
        logger.info(f"初始化自动化脚本，模拟器索引: {emulator_index}")

    def _load_templates(self) -> Dict[str, np.ndarray]:
        templates = {}
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            logger.warning(f"模板目录 {self.template_dir} 不存在，已创建空目录")
            return templates
        for filename in os.listdir(self.template_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                name = os.path.splitext(filename)[0]
                template_path = os.path.join(self.template_dir, filename)
                templates[name] = cv2.imread(template_path, 0)
                logger.debug(f"加载模板: {name}")
        logger.info(f"已加载 {len(templates)} 个模板图片")
        return templates

    def take_screenshot(self) -> bool:
        try:
            # 用Dnconsole截屏
            Dnconsole.dnld(self.emulator_index, 'screencap -p /sdcard/Pictures/apk_scr.png')
            time.sleep(1)
            if os.path.exists(self.screenshot_path):
                logger.debug("截屏成功")
                return True
            else:
                logger.error("截屏文件不存在")
                return False
        except Exception as e:
            logger.error(f"截屏异常: {str(e)}")
            return False

    def find_template(self, template_name: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        if template_name not in self.templates:
            logger.error(f"模板 '{template_name}' 未找到")
            return None
        screenshot = cv2.imread(self.screenshot_path, 0)
        if screenshot is None:
            logger.error("无法读取截图文件")
            return None
        template = self.templates[template_name]
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
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
        try:
            Dnconsole.touch(self.emulator_index, x, y)
            logger.debug(f"点击位置: ({x}, {y})")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"点击操作异常: {str(e)}")

    def click_template(self, template_name: str, threshold: float = 0.8) -> bool:
        if not self.take_screenshot():
            return False
        position = self.find_template(template_name, threshold)
        if position:
            x, y = position
            self.click(x, y)
            return True
        return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300, delay: float = 1.0):
        try:
            Dnconsole.swipe(self.emulator_index, (x1, y1), (x2, y2), duration)
            logger.debug(f"滑动: ({x1}, {y1}) -> ({x2}, {y2})")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"滑动操作异常: {str(e)}")

    def wait_for_template(self, template_name: str, timeout: int = 30, interval: float = 1.0, threshold: float = 0.8) -> bool:
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
        logger.info("开始执行日常任务")
        if self.click_template("task_button"):
            logger.info("已点击任务按钮")
            time.sleep(2)
            if self.wait_for_template("task_interface", timeout=10):
                if self.click_template("daily_task"):
                    logger.info("已选择日常任务")
                    time.sleep(2)
                    if self.click_template("claim_reward"):
                        logger.info("已领取任务奖励")
                        time.sleep(2)
        self.click(50, 50)
        logger.info("日常任务执行完成")

    def main_loop(self, interval: int = 300):
        logger.info("启动主循环")
        try:
            while True:
                self.run_daily_tasks()
                logger.info(f"等待 {interval} 秒后继续...")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("用户中断程序")
        except Exception as e:
            logger.error(f"主循环异常: {str(e)}")
        logger.info("主循环结束")

if __name__ == "__main__":
    # 启动模拟器并打开APP
    index = 0
    package_name = "com.xhtt.app.fzjh"
    print("启动模拟器...")
    Dnconsole.launch(index)
    print("模拟器实例数量:", len(Dnconsole.get_list()))
    while not Dnconsole.is_running(index):
        print("等待模拟器启动...")
        time.sleep(15)
    print("模拟器已启动")
    print("启动APP...")
    Dnconsole.invokeapp(index, package_name)
    print("APP已启动")

    # 初始化自动化脚本
    auto = JiangHuAuto(emulator_index=index, template_dir="E:/leidian/start")
    #auto.main_loop(interval=300)

    if auto.click_template('qq'):
        logger.info("已点击开始游戏")
    else:
        logger.warning("未识别到开始游戏按钮")

    time.sleep(30)
    if auto.click_template('jianghu'):
        logger.info("已点击江湖")
    else:
        logger.warning("未识别到江湖按钮")