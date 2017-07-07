import cv2
import numpy as np

image = cv2.imread('MyPic.png')

image[0, 0] = 255
cv2.imshow("w1", image)

subim=image[100:200,100:200]
image[0:100,0:100]=subim
cv2.imshow("w2", image)

image[100:200, 100:200, 0] = 255
cv2.imshow("w3", image)

image[:, :, 0] = 255
cv2.imshow("w4", image)

cv2.waitKey()
cv2.destroyAllWindows()
