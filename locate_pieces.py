import cv2 as cv
import sys
import numpy as np
import pyautogui
import mss
import time
import startup
from io import StringIO
import chess

#(x, y, w, h, sct) = startup.take_screenshot()


def convert_array_to_FEN(chess_board_array):
    s = StringIO()
    for row in chess_board_array:
        empty = 0
        for cell in row:
            if cell == "":
                empty += 1
            else:
                if empty > 0:
                    s.write(str(empty))
                    empty = 0
                s.write(cell)
        if empty > 0:
            s.write(str(empty))
        s.write('/')
    s.seek(s.tell() - 1)
    return s.getvalue()


pieces = {"black_pawn": 'p', "black_rook": "r", "black_bishop": "b", "black_knight": "n", "black_king": "k",
          "black_queen": "q", "white_pawn": "P", "white_rook": "R", "white_bishop": "B", "white_knight": "N",
          "white_queen": "Q", "white_king": "K"}



x = 377
y = 172
w = 740
h = 740
with mss.mss() as sct:
    monitor_number = 1
    mon = sct.monitors[monitor_number]
    monitor2 = {
        "top": mon["top"] + y,
        "left": mon["left"] + x,
        "width": w,
        "height": h,
        "mon": monitor_number,
    }

    sct_img = sct.grab(monitor2)
    img = np.array(sct.grab(monitor2))

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = cv.resize(gray, (736, 736), interpolation=cv.INTER_LINEAR)

#cv.imshow("new board", gray)
#cv.waitKey(0)

chess_board = np.zeros((8, 8), dtype='U2')
chess_board = np.flip(chess_board, axis=1)

for piece in pieces.keys():
    template1 = cv.imread(f"new_pieces/{piece}_light.PNG", 0)
    template2 = cv.imread(f"new_pieces/{piece}_dark.PNG", 0)

    w, h = template1.shape[::-1]
    print(f"w: {w} h: {h}")

    res1 = cv.matchTemplate(gray, template1, cv.TM_CCOEFF_NORMED)
    res2 = cv.matchTemplate(gray, template2, cv.TM_CCOEFF_NORMED)

    threshold = 0.8

    loc1 = np.where(res1 >= threshold)
    yloc1, xloc1 = loc1

    loc2 = np.where(res2 >= threshold)
    yloc2, xloc2 = loc2
    print(len(xloc1))


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
        chess_file = chr(((x + 100) // 92 - 1) + 97)
        chess_rank = 9 - ((y + 100) // 92)
        print(f"{piece}" + ":" + chess_file + str(chess_rank))
        chess_coords.append([chess_file, chess_rank])
        pce = piece.split("_")
        chess_board[chess_rank - 1][(x + 100) // 92 - 1] = pieces[piece]

    # print(chess_coords)
    cv.imshow('Detected', img)
    k = cv.waitKey(0)

    print(np.flip(chess_board, axis=0))
FEN = convert_array_to_FEN(np.flip(chess_board, axis=0))[:-1]
FEN = FEN + ' w KQkq - 0 1'
print(FEN)

board = chess.Board(FEN)
print(board)