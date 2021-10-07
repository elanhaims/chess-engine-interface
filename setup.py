import cv2 as cv
import numpy as np
import mss
from screenshot_converter import Converter
import pyttsx3

tts_engine = pyttsx3.init()

PIECES = {0: "rook", 1: "knight", 2: "bishop", 3: "queen", 4: "king", 5: "bishop", 6: "knight", 7: "rook"}
SQUARE = {0: "light", 1: "dark"}


class Setup:
    """Class that performs all of the initial setup.

     Contains methods that find the region of the board on the monitor and creates images of all of the pieces on the
     board to use in template matching. Initializes an instance of the Converter class from screenshot_converter.py
     that is used for screenshotting the chess board and turning that screenshot into a chess board data
     representation"""
    def __init__(self):
        """Initializes the Setup instance"""
        with mss.mss() as sct:
            # The tool used to take screenshots
            self.sct = sct

            # Parameters used for taking screenshots
            self.monitor_number = 1
            self.mon = sct.monitors[self.monitor_number]

    def perform_setup(self) -> Converter:
        """Calls two methods that perform the setup

        :return: An instance of the Converter class
        """
        # Obtain the board dimensions as pixel values
        x, y, w, h, = self.find_board_dimensions(self.sct)
        # Creates images of all of the chess pieces and gets a pixel value from the white Queen
        white_pixel_value, monitor = self.create_piece_screenshots(x, y, w, h, self.sct)
        print("Startup completed")
        tts_engine.say("Startup completed")
        tts_engine.runAndWait()
        return Converter(self.sct, monitor, w, white_pixel_value)

    def find_board_dimensions(self, sct: mss.mss) -> (float, float, float, float):
        """Obtains the dimensions of the chess board as pixel values

        :param sct: tool used for taking screenshots
        :return: A tuple of floats containing the starting x coordinate, starting y coordinate, width, and height for
        the region of the chessboard on the monitor
        """
        mon = self.mon
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": 1920,
            "height": 1080,
            "mon": self.monitor_number,
        }

        # Take a screenshot of the entire monitor
        img = np.array(sct.grab(monitor))
        # Convert the image to grayscale for image processing
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Performs opencv template matching with the starting template to find the chess board in the screenshot
        template = cv.imread("starting_templates/starting_position.png", 0)
        res1 = cv.matchTemplate(gray, template, cv.TM_CCOEFF_NORMED)

        threshold = 0.75
        w, h = template.shape[::-1]
        loc = np.where(res1 >= threshold)
        yloc, xloc = loc

        rectangles = []
        for (x, y) in zip(xloc, yloc):
            rectangles.append([int(x), int(y), int(w), int(h)])
            rectangles.append([int(x), int(y), int(w), int(h)])

        rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)

        # If there are no rectangles, that means the chess board could not have been detected
        if len(rectangles) == 0:
            raise Exception("Could not detect a chess board")

        # There should only be one value in rectangle so we can take the values from the first index
        x, y, w, h = rectangles[0]
        return x, y, w, h

    def create_piece_screenshots(self, x: float, y: float, w: float, h: float, sct: mss.mss) -> (int, dict):
        """Creates screenshots of every chess piece on the board to use for template matching

            :param x: The starting x coordinate of the board as a pixel position
            :param y: The starting y coordinate of the board as a pixel position
            :param w: The width of the board in pixels
            :param h: The height of the board in pixels, this should be the same value as the width
            :param sct: Tool used to take screenshots
            :return white_pixel_value: A pixel color value of the white players Queen which is used to determine which
            color pieces the user is playing as
            :return board_monitor: A dictionary which is used as a parameter for taking screenshots
        """
        mon = self.mon
        board_monitor = {
            "top": mon["top"] + int(y),
            "left": mon["left"] + int(x),
            "width": int(w),
            "height": int(h),
            "mon": self.monitor_number,
        }

        # Screenshot of the chess board
        img = np.array(sct.grab(board_monitor))

        # Convert the image to grayscale for image processing
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Resizes the board screenshot to make it perfectly divisible by 8 so that it can be split up into an 8x8 grid
        # of squares
        board_width = (w // 8) * 8
        gray = cv.resize(gray, (board_width, board_width), interpolation=cv.INTER_LINEAR)

        # Gets the width of each chess square
        square_width = board_width // 8

        # Takes a screenshot of every piece on a light and dark square except for pawns
        for k in range(8):
            black = gray[0:square_width, k * square_width:k * square_width + square_width]
            cv.imwrite(f"chess_pieces/black_{PIECES[k]}_{SQUARE[k % 2]}.png", black)
            white = gray[board_width - square_width:board_width, k * square_width:k * square_width + square_width]
            cv.imwrite(f"chess_pieces/white_{PIECES[k]}_{SQUARE[(k + 1) % 2]}.png", white)

        # Duplicates the screenshots for the King and Queen for both players because there is only one of each
        black_king_dark = gray[0:square_width, 4 * square_width:5 * square_width]
        cv.imwrite("chess_pieces/black_king_dark.png", black_king_dark)
        white_king_light = gray[7 * square_width:board_width, 4 * square_width:5 * square_width]
        cv.imwrite("chess_pieces/white_king_light.png", white_king_light)
        black_queen_light = gray[0:square_width, 3 * square_width:4 * square_width]
        cv.imwrite("chess_pieces/black_queen_light.png", black_queen_light)
        white_queen_dark = gray[7 * square_width:board_width, 3 * square_width:4 * square_width]
        cv.imwrite("chess_pieces/white_queen_dark.png", white_queen_dark)

        # Takes a screenshot of the pawns on a light and dark square
        black_pawn_dark = gray[square_width:2 * square_width, 0:square_width]
        cv.imwrite("chess_pieces/black_pawn_dark.png", black_pawn_dark)
        black_pawn_light = gray[square_width:2 * square_width, square_width:2 * square_width]
        cv.imwrite("chess_pieces/black_pawn_light.png", black_pawn_light)
        white_pawn_light = gray[6 * square_width:7 * square_width, 0:square_width]
        cv.imwrite("chess_pieces/white_pawn_light.png", white_pawn_light)
        white_pawn_dark = gray[6 * square_width:7 * square_width, square_width:2 * square_width]
        cv.imwrite("chess_pieces/white_pawn_dark.png", white_pawn_dark)

        # Obtains a pixel value from the white_queen which is used to determining the color of the pieces the user is
        # playing as
        white_queen = gray[7 * square_width:board_width, 3 * square_width:4 * square_width]
        white_pixel_value = white_queen[square_width // 2, square_width // 2]

        return white_pixel_value, board_monitor
