import cv2 as cv
import sys
import numpy as np
import pyautogui


img = cv.imread("Chess Pieces/test_board2.PNG")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

template = cv.imread(f"Chess Pieces/board.PNG", 0)

res1 = cv.matchTemplate(gray, template, cv.TM_CCOEFF_NORMED)

threshold = 0.75

w, h = template.shape[::-1]

loc1 = np.where(res1 >= threshold)
yloc1, xloc1 = loc1

rectangles = []
for (x, y) in zip(xloc1, yloc1):
    rectangles.append([int(x), int(y), int(w), int(h)])
    rectangles.append([int(x), int(y), int(w), int(h)])

# print(len(rectangles))
rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)
# print(len(rectangles))

for (x, y, w, h) in rectangles:
    cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)

cv.imshow("image", img)
cv.waitKey(0)
