import cv2
import matplotlib.pyplot as plt

# 读取本地图片（注意路径）
img = cv2.imread("/home/chenpuuuu/ai-robot-chenpuchang/作业/week10/image.png")

# 显示彩色图
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.show()

# 转灰度图
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 显示灰度图
plt.imshow(img_gray, cmap="gray")
plt.axis("off")
plt.show()