import cv2
import matplotlib.pyplot as plt

img = cv2.imread("下载.png")

plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.show()