import cv2 as cv
import sys
import numpy as np
import pyautogui
import mss
import time


#image = pyautogui.screenshot()
#image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)

pieces = {0: "rook", 1: "knight", 2: "bishop", 3: "queen", 4: "king", 5:"bishop", 6: "knight", 7: "rook"}
square = {0: "light", 1: "dark"}

def take_screenshot(sct):
    monitor_number = 1
    mon = sct.monitors[monitor_number]

    monitor = {
        "top": mon["top"],
        "left": mon["left"],
        "width": 1920,
        "height": 1080,
        "mon": monitor_number,
    }
    img = np.array(sct.grab(monitor))
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #cv.imshow("Gray", gray)
    #cv.waitKey(0)
    template_white = cv.imread("starting_templates/starting_position_white.png", 0)
    template_black = cv.imread("starting_templates/starting_position_black.png", 0)
    res1 = cv.matchTemplate(gray, template_white, cv.TM_CCOEFF_NORMED)
    res2 = cv.matchTemplate(gray, template_black, cv.TM_CCOEFF_NORMED)

    threshold = 0.75
    w, h = template_white.shape[::-1]
    loc1 = np.where(res1 >= threshold)
    yloc1, xloc1 = loc1
    loc2 = np.where(res2 >= threshold)
    yloc2, xloc2 = loc2
    print(f"res1: {len(xloc1)} and {len((yloc1))}")
    print(f"res2: {len(xloc2)} and {len((yloc2))}")

    player_color = None
    xloc, yloc = None, None
    if len(xloc1) == 0 and len(xloc2) == 0:
        print("No template was matched")
        return
    if len(xloc1) != 0 and len(xloc2) != 0:
        print("Multiple templates matched")
        return
    if len(xloc1) != 0 and len(xloc2) == 0:
        xloc, yloc = xloc1, yloc1
        player_color = "white"
    elif len(xloc1) == 0 and len(xloc2) != 0:
        xloc, yloc = xloc2, yloc2
        player_color = "black"

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)

    x, y, w, h = rectangles[0]

    for (x, y, w, h) in rectangles:
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
    # cv.imshow("image", img)
    # cv.waitKey(0)

    monitor2 = {
        "top": mon["top"] + int(y),
        "left": mon["left"] + int(x),
        "width": int(w),
        "height": int(h),
        "mon": 1,
    }

    img2 = np.array(sct.grab(monitor2))

    board_width = board_height = int((w // 8) * 8)
    square_width = board_width // 8
    print(f"square: {square_width}")
    gray = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    gray = cv.resize(gray, (board_width, board_width), interpolation=cv.INTER_LINEAR)

    # cv.imshow("new shot", gray)
    # cv.waitKey(0)

    for k in range(8):
        black = gray[0:square_width, k * square_width:k*square_width + square_width]
        cv.imwrite(f"chess_pieces/black_{pieces[k]}_{square[k%2]}.png", black)
        white = gray[board_width-square_width:board_width, k*square_width:k*square_width + square_width]
        cv.imwrite(f"chess_pieces/white_{pieces[k]}_{square[(k+1)%2]}.png", white)

    black_king_dark = gray[0:square_width, 4 * square_width:5 * square_width]
    cv.imwrite("chess_pieces/black_king_dark.png", black_king_dark)
    white_king_light = gray[7 * square_width:board_width, 4 * square_width:5 * square_width]
    cv.imwrite("chess_pieces/white_king_light.png", white_king_light)
    black_queen_light = gray[0:square_width, 3 * square_width:4 * square_width]
    cv.imwrite("chess_pieces/black_queen_light.png", black_queen_light)
    white_queen_dark = gray[7 * square_width:board_width, 3 * square_width:4 * square_width]
    cv.imwrite("chess_pieces/white_queen_dark.png", white_queen_dark)
    black_pawn_dark = gray[square_width:2 * square_width, 0:square_width]
    cv.imwrite("chess_pieces/black_pawn_dark.png", black_pawn_dark)
    black_pawn_light = gray[square_width:2 * square_width, square_width:2 * square_width]
    cv.imwrite("chess_pieces/black_pawn_light.png", black_pawn_light)
    white_pawn_light = gray[6 * square_width:7 * square_width, 0:square_width]
    cv.imwrite("chess_pieces/white_pawn_light.png", white_pawn_light)
    white_pawn_dark = gray[6 * square_width:7 * square_width, square_width:2 * square_width]
    cv.imwrite("chess_pieces/white_pawn_dark.png", white_pawn_dark)

    white_queen = gray[7 * square_width:board_width, 3 * square_width:4 * square_width]
    #cv.imshow("qu", white_queen)
    white_pixel_color = int(white_queen[square_width // 2, square_width // 2])
    print(white_pixel_color)
    black_queen = gray[0:square_width, 3 * square_width:4 * square_width]
    black_pixel_color = black_queen[square_width // 2, square_width // 2]
    print(black_pixel_color)
    #cv.imshow("queen", white_queen_dark)
    #cv.waitKey(0)

    return x, y, board_width, board_height, white_pixel_color



if __name__ == "__main__":
     take_screenshot()