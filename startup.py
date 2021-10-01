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
    """
    monitor = {
        "top": mon["top"],
        "left": mon["left"],
        "width": 1920,
        "height": 1080,
        "mon": monitor_number,
    }
    sct_img = sct.grab(monitor)
    img = np.array(sct.grab(monitor))
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imshow("Gray", gray)
    cv.waitKey(0)
    template = cv.imread(f"Chess Pieces/cropped_board.PNG", 0)
    template2 = cv.imread("Chess Pieces/empty_board.PNG", 0)
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
    print(rectangles[0])
    x, y, w, h = rectangles[0]
    print(x)
    for (x, y, w, h) in rectangles:
        print(f"x:{x}, y:{y}, w:{w}, h:{h}")
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
    cv.imshow("image", img)
    cv.waitKey(0)
    #cv.destroyAllWindows()
    #time.sleep(5)
    #take_screenshot()
"""
    x = 377
    y = 172
    w = 740
    h = 740
    monitor2 = {
        "top": mon["top"] + y,
        "left": mon["left"] + x,
        "width": w,
        "height": h,
        "mon": 1,
    }

    #sct_img = sct.grab(monitor2)
    img2 = np.array(sct.grab(monitor2))

    gray = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    gray = cv.resize(gray, (736, 736), interpolation=cv.INTER_LINEAR)

    # cv.imshow("new shot", gray)
    # cv.waitKey(0)

    for k in range(8):
        black = gray[0:92, k*92:k*92 + 92]
        cv.imwrite(f"chess_pieces/black_{pieces[k]}_{square[k%2]}.png", black)
        white = gray[736-92:736, k*92:k*92 + 92]
        cv.imwrite(f"chess_pieces/white_{pieces[k]}_{square[(k+1)%2]}.png", white)

    black_king_dark = gray[0:92, 368:460]
    cv.imwrite("chess_pieces/black_king_dark.png", black_king_dark)
    white_king_light = gray[644:736, 368:460]
    cv.imwrite("chess_pieces/white_king_light.png", white_king_light)
    black_queen_light = gray[0:92, 276:368]
    cv.imwrite("chess_pieces/black_queen_light.png", black_queen_light)
    white_queen_dark = gray[644:736, 276:368]
    cv.imwrite("chess_pieces/white_queen_dark.png", white_queen_dark)
    black_pawn_dark = gray[92:184, 0:92]
    cv.imwrite("chess_pieces/black_pawn_dark.png", black_pawn_dark)
    black_pawn_light = gray[92:184, 92:184]
    cv.imwrite("chess_pieces/black_pawn_light.png", black_pawn_light)
    white_pawn_light = gray[552:644, 0:92]
    cv.imwrite("chess_pieces/white_pawn_light.png", white_pawn_light)
    white_pawn_dark = gray[552:644, 92:184]
    cv.imwrite("chess_pieces/white_pawn_dark.png", white_pawn_dark)

    return(x, y, w, h)



if __name__ == "__main__":
     take_screenshot()