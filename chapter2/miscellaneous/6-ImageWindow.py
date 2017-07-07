import cv2
import numpy as np

image = cv2.imread('MyPic.png')
image[0, 0] = 255
cv2.imshow("w1", image)
image[:, :, 0] = 255
cv2.imshow("w2", image)
cv2.waitKey()
cv2.destroyAllWindows()
