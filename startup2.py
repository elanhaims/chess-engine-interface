import cv2 as cv
import sys
import numpy as np
import pyautogui


img = pyautogui.screenshot(region=(376, 173, 741, 741))
img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
cv.imshow("image", img)
cv.waitKey(0)
print(img.shape)
windowsize_r = 92
windowsize_c = 92

for r in range(0, img.shape[0] - windowsize_r, windowsize_r):
    for c in range(0, img.shape[1] - windowsize_c, windowsize_c):
        window = img[r:r+windowsize_r, c:c+windowsize_c]
        wind = cv.cvtColor(np.array(window), cv.COLOR_RGB2BGR)
        cv.imshow("window", wind)
        cv.waitKey(0)

roi = img[0:92, 0:92]
roi = cv.cvtColor(np.array(roi), cv.COLOR_RGB2BGR)
cv.imshow("roi", roi)
cv.waitKey(0)