import cv2 as cv
import sys
import numpy as np
import pyautogui

pieces = ["black_pawn", "black_rook", "black_bishop", "black_knight", "black_queen", "black_king", "white_pawn",
          "white_rook", "white_bishop", "white_knight", "white_queen", "white_king"]

button_location = pyautogui.locateOnScreen("Chess Pieces/chesscom_profile_name.png")
print(button_location)


image = pyautogui.screenshot()
image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)

cv.imshow("screenshot", image)
cv.waitKey(0)

chess_board = np.zeros((8, 8))
print(chess_board)
img = cv.imread("Chess Pieces/chess_board4.PNG")
img = cv.resize(img, (880, 880), interpolation=cv.INTER_LINEAR)
color = img[20, 120]
color2 = img[0, 0]
print(f"color2: {color2}")
print(color)
# img[np.where((img==[210,238,238]).all(axis=2))] = [86, 150, 118]
cv.imshow("img", img)
cv.waitKey(0)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
for piece in pieces:

    template1 = cv.imread(f"Chess Pieces/{piece}_light.PNG", 0)
    template1 = cv.resize(template1, (110, 110), interpolation=cv.INTER_LINEAR)

    template2 = cv.imread(f"Chess Pieces/{piece}_dark.PNG", 0)
    template2 = cv.resize(template2, (110, 110), interpolation=cv.INTER_LINEAR)

    w, h = template1.shape[::-1]
    print(f"w: {w} h: {h}")

    res1 = cv.matchTemplate(gray, template1, cv.TM_CCOEFF_NORMED)
    res2 = cv.matchTemplate(gray, template2, cv.TM_CCOEFF_NORMED)

    threshold = 0.75

    loc1 = np.where(res1 >= threshold)
    yloc1, xloc1 = loc1

    loc2 = np.where(res2 >= threshold)
    yloc2, xloc2 = loc2
    print(len(xloc1))

    # Draw a rectangle around the matched region.
    # for pt in zip(*loc[::-1]):
    #     print(pt)
    #     cv.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)

    # cv.imshow('Detected', img)
    # k = cv.waitKey(0)

    rectangles = []
    for (x, y) in zip(xloc1, yloc1):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    for (x, y) in zip(xloc2, yloc2):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    # print(len(rectangles))
    rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)
    # print(len(rectangles))

    for (x, y, w, h) in rectangles:
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)

    # cv.imshow('Detected', img)
    # k = cv.waitKey(0)
    # print(rectangles)

    centers = []
    for (x, y, w, h) in rectangles:
        x_cord = x + w // 2
        y_cord = y + h // 2
        centers.append([int(x_cord), int(y_cord)])
        cv.circle(img, (x_cord, y_cord), radius=1, color=(0, 0, 255), thickness=1)
    # print(centers)
    # cv.imshow('Detected', img)
    # k = cv.waitKey(0)

    chess_coords = []
    for (x, y) in centers:
        # print(chr(((x + 100) // 100 - 1) + 97))
        chess_file = chr(((x + 100) // 110 - 1) + 97)
        chess_rank = 9 - ((y + 100) // 110)
        print(piece + ":" + chess_file + str(chess_rank))
        chess_coords.append([chess_file, chess_rank])

    # print(chess_coords)
    cv.imshow('Detected', img)
    k = cv.waitKey(0)

cv.imshow("marked image", img)
cv.waitKey(0)
