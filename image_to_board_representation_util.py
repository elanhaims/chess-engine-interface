import numpy as np
import cv2 as cv
from chess_session import PIECES


def locate_piece(piece, board_screenshot):
    template1 = cv.imread(f"chess_pieces/{piece}_light.PNG", 0)
    template2 = cv.imread(f"chess_pieces/{piece}_dark.PNG", 0)

    w, h = template1.shape[::-1]

    res1 = cv.matchTemplate(board_screenshot, template1, cv.TM_CCOEFF_NORMED)
    res2 = cv.matchTemplate(board_screenshot, template2, cv.TM_CCOEFF_NORMED)

    threshold = 0.8

    loc1 = np.where(res1 >= threshold)
    yloc1, xloc1 = loc1

    loc2 = np.where(res2 >= threshold)
    yloc2, xloc2 = loc2

    rectangles = []
    for (x, y) in zip(xloc1, yloc1):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    for (x, y) in zip(xloc2, yloc2):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def find_centers(rectangles):
    centers = []
    for (x, y, w, h) in rectangles:
        x_cord = x + w // 2
        y_cord = y + h // 2
        centers.append([int(x_cord), int(y_cord)])
    return centers


def add_pieces_to_board(piece, board, piece_locations, centers):
    chess_board = board
    locations = piece_locations
    if centers:
        for (x, y) in centers:
            chess_file = chr(((x + 100) // 92 - 1) + 97)
            chess_rank = 9 - ((y + 100) // 92)
            if piece not in locations.keys():
                locations[piece] = [chess_file + str(chess_rank)]
            else:
                locations[piece].append(chess_file + str(chess_rank))
            chess_board[chess_rank - 1][(x + 100) // 92 - 1] = PIECES[piece]

        locations[piece] = sorted(locations[piece], key=lambda Z: (Z[0], Z[1]))
    return chess_board, locations
