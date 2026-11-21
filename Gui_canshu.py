import pyautogui
screenWidth, screenHeight = pyautogui.size()
print(f"屏幕宽度: {screenWidth}, 屏幕高度: {screenHeight}")
# 获取当前鼠标位置
currentX, currentY = pyautogui.position()
print(f"当前鼠标位置: X={currentX}, Y={currentY}")
'''
移动的四个点
中点 X=2110, Y=668
左点 X=1813, Y=661
右点 X=2314, Y=651
下点 X=2082, Y=768
上点 X=2090, Y=552

左上点 X=1748, Y=87

右上点 X=2438, Y=85
退出：X=2078, Y=1011

人物对话
分别有1 2 3 4 5个框，对应的参数，y轴间距80
X=2314, Y=569
X=2310, Y=616
X=2315, Y=667

X=2083, Y=704
X=2085, Y=761

X=2081, Y=703
X=2084, Y=781
X=2085, Y=861
X=2084, Y=943

X=2084, Y=700

X=2083, Y=703
X=2085, Y=780
X=2083, Y=858
X=2087, Y=946
X=2083, Y=1026

底部框
可能存在1 2 3 4 5 6框
第一行三个框
X=2157, Y=693
X=2312, Y=695
X=2465, Y=682
第二行三个框
X=1830, Y=982
X=2085, Y=983


'''

#pyautogui.click(x=2070, y=910, clicks=1, interval=0.25, button='left')