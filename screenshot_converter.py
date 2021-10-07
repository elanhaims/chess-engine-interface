import numpy as np
import cv2 as cv
from io import StringIO
import mss

# Dictionary to convert piece names to their FEN representation
PIECES = {"black_pawn": 'p', "black_rook": "r", "black_bishop": "b", "black_knight": "n", "black_king": "k",
          "black_queen": "q", "white_pawn": "P", "white_rook": "R", "white_bishop": "B", "white_knight": "N",
          "white_queen": "Q", "white_king": "K"}

# Dictionary to construct the board position when the user is playing as black. This is used to flip the board. Will
# try to find a better way to do this
WHITE_TO_BLACK_SQUARES = {"1": "8", "2": "7", "3": "6", "4": "5", "5": "4", "6": "3", "7": "2", "8": "1",
                          "a": "h", "b": "g", "c": "f", "d": "e", "e": "d", "f": "c", "g": "b", "h": "a"}


class Converter:
    """Handles screenshotting and converting the chessboard into data structures that store the board position"""
    def __init__(self, sct: mss.mss, monitor: dict, board_width: int, white_pixel_value: int):
        """Initializes the Converter instance

        :param sct: tool used to take screenshots of the user's monitor
        :param monitor: dictionary used as a parameter for taking the screenshot
        :param board_width: the width of the chessboard in pixels
        :param white_pixel_value: the pixel color value of the white Queen
        """
        self.sct = sct
        self.monitor = monitor
        self.board_width = board_width
        self.white_pixel_value = white_pixel_value

    def screenshot_chess_board(self) -> np.ndarray:
        """Takes a screenshot of the chess board"""
        # The screenshot gets stored as a numpy array of pixel values
        img = np.array(self.sct.grab(self.monitor))
        # Converts the image to grayscale for image processing
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # Resizes the image to make the width and height perfectly divisible by 8 so the screenshot can be divided
        # up into an 8x8 grid of the chess squares
        gray = cv.resize(gray, (self.board_width, self.board_width), interpolation=cv.INTER_LINEAR)
        return gray

    def get_player_color(self, board_screenshot: np.ndarray) -> str:
        """Returns the color of the pieces the user is playing as"""
        square_width = (self.board_width // 8)
        # Crops the board screenshot to get an image of just the user's Queen
        queen = board_screenshot[7 * square_width:self.board_width, 3 * square_width:4 * square_width]
        # Gets the pixel value from the center of the user's queen
        queen_pixel_value = int(queen[square_width // 2, square_width // 2])

        # If the pixel value of the user's queen is equal to the pixel value of the white queen then the user is white
        if queen_pixel_value == self.white_pixel_value:
            return "white"
        # Otherwise the user is playing as black
        else:
            return "black"

    def convert_screenshot_to_chess_board_array(self, board_screenshot: np.ndarray, player_color: str) -> (np.ndarray,
                                                                                                           dict):
        """Builds the array and dictionary representation of the chess board using opencv template matching

        :param board_screenshot: screenshot of the chess board
        :param player_color: the color of the pieces the user is playing as
        :return chess_board: 2d array representation of the chess board
        :return piece_locations: dictionary representation of the chess board
        """
        chess_board = np.zeros((8, 8), dtype='U2')
        piece_locations = {}
        # Iterates over every piece
        for piece in PIECES.keys():
            # Builds a rectangle around each occurrence of the piece on the board
            rectangles = locate_piece(piece, board_screenshot)
            # Gets the center pixel coordinate for each rectangle
            centers = find_centers(rectangles)
            # Adds the piece to the array and dictionary
            chess_board, piece_locations = add_pieces_to_board_array(piece, chess_board, piece_locations,
                                                                     centers, player_color, (self.board_width // 8))
        return chess_board, piece_locations

    def generate_fen_from_image(self, board_screenshot: np.ndarray, player_color: str) -> (str, np.ndarray, dict):
        """Builds a FEN string representing the chess board position from the board screenshot

        :param board_screenshot: a screenshot of the chess board
        :param player_color: the color of the pieces the user is playing as
        :return board_fen: FEN string of the board position
        :return chess_board_array: 2d array representation of the chess position
        :return piece_locations: dictionary representation of the chess position
        """
        chess_board_array, piece_locations = \
            self.convert_screenshot_to_chess_board_array(board_screenshot, player_color)
        board_fen = convert_array_to_FEN(np.flip(chess_board_array, axis=0), player_color)
        return board_fen, chess_board_array, piece_locations


def locate_piece(piece: str, board_screenshot: np.ndarray) -> list:
    """Returns a list of rectangles around all occurrences of the piece on the board.

     :param piece: a string of the chess piece. Piece can be any value from the PIECES dict keys.
     :param board_screenshot: a screenshot of the chess board

     Uses opencv template matching to locate all occurrences of the piece on the chess board. Returns a list of rectangles
     around all occurrences of the piece for further processing.
     """

    # The templates to use for template matching. Use two templates, one for the light square and one for the dark
    # square of a piece to make it easier for the piece to be detected.
    template1 = cv.imread(f"chess_pieces/{piece}_light.PNG", 0)
    template2 = cv.imread(f"chess_pieces/{piece}_dark.PNG", 0)

    # Retrieve the width and height of the template. Should be the same value
    w, h = template1.shape[::-1]

    # Performs the template matching on both of the templates
    res1 = cv.matchTemplate(board_screenshot, template1, cv.TM_CCOEFF_NORMED)
    res2 = cv.matchTemplate(board_screenshot, template2, cv.TM_CCOEFF_NORMED)

    # Threshold value used in template matching
    threshold = 0.8

    # Only keep the values where the result is greater than the threshold
    loc1 = np.where(res1 >= threshold)
    yloc1, xloc1 = loc1

    loc2 = np.where(res2 >= threshold)
    yloc2, xloc2 = loc2

    # Finds all of the rectangles for the first template
    rectangles = []
    for (x, y) in zip(xloc1, yloc1):
        rectangles.append([int(x), int(y), int(w), int(h)])
        # Add the same rectangle to the list twice for grouping the rectangles
        rectangles.append([int(x), int(y), int(w), int(h)])

    # Finds all of the rectangles for the second template
    for (x, y) in zip(xloc2, yloc2):
        rectangles.append([int(x), int(y), int(w), int(h)])
        # Add the same rectangle to the list twice for grouping the rectangles
        rectangles.append([int(x), int(y), int(w), int(h)])

    # Call the opencv groupRectangles function to remove duplicate rectangles around pieces
    rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def find_centers(rectangles: list) -> list:
    """Iterate through all of the rectangles and find the center pixel coordinate for each one.

    :param rectangles: List of tuples containing the x and y coordinates and the width and height of each rectangle
    """
    centers = []
    for (x, y, w, h) in rectangles:
        x_cord = x + w // 2
        y_cord = y + h // 2
        centers.append([int(x_cord), int(y_cord)])
    return centers


def add_pieces_to_board_array(piece: str, board: np.ndarray, piece_locations: dict, centers: list, player_color: str,
                              square_size: int) -> (np.ndarray, dict):
    """
    Fills in the chess board array and dictionary representations with the chess pieces.

    A white rook on A1 will be stored as 'R' in chess_board[0][0] in the array and {"white_rook":["A1"]} in the
    dictionary

    :param piece: The name of the chess piece e.g. 'white_pawn'
    :param board: 2d array representation of the chess board
    :param piece_locations: Dictionary with the piece names as keys and the square location for each piece as the value
    :param centers: List of pixel coordinates for each piece
    :param player_color: The color of the pieces the user is playing as
    :param square_size: The size of the chess squares in pixel units
    :return: The chess board array and dictionary with the piece parameter filled in
    """
    chess_board = board
    locations = piece_locations
    if centers:
        # Iterate over all of the values in centers
        for (x, y) in centers:
            # Convert the x coordinate value to a chess file e.g. 'a'
            chess_file = chr(((x + 100) // square_size - 1) + 97)
            # Convert the y coordinate value to a chess rank e.g. '1'
            chess_rank = str(9 - ((y + 100) // square_size))

            # If the user is playing as the black pieces, flip the file and rank values e.g. 'a' -> 'h'
            if player_color == "black":
                chess_file = WHITE_TO_BLACK_SQUARES[chess_file]
                chess_rank = WHITE_TO_BLACK_SQUARES[chess_rank]
            # Add the piece to the piece location dictionary if it is not in it
            if piece not in locations.keys():
                locations[piece] = [chess_file + chess_rank]
            # Add the chess file and rank to the dictionary for the piece
            else:
                locations[piece].append(chess_file + chess_rank)
            # Add the piece to the 2d array representation of the board
            chess_board[int(chess_rank) - 1][(x + 100) // square_size - 1] = PIECES[piece]
        # Sort the piece locations, this is just for ease of use when testing and printing
        locations[piece] = sorted(locations[piece], key=lambda Z: (Z[0], Z[1]))
    return chess_board, locations


def convert_array_to_FEN(chess_board_array: np.ndarray, player_color: str) -> str:
    """Builds the FEN string of the position from the board array
    
    :param chess_board_array: 2d array representation of the chess board
    :param player_color: the color of the pieces the user is playing as
    :return: FEN string of the position
    """
    # Use StringIO for faster string building
    s = StringIO()
    # Iterate over every row in the board array
    for row in chess_board_array:
        empty = 0
        # If the user is playing as black, reverse the row because the FEN string always starts at the first file
        if player_color == "black":
            row = np.flip(row, 0)
        # Iterate over every square in the row
        for cell in row:
            if cell == "":
                empty += 1
            else:
                # Add the number of empty squares in a row
                if empty > 0:
                    s.write(str(empty))
                    empty = 0
                # Add the piece to the FEN string
                s.write(cell)
        if empty > 0:
            s.write(str(empty))
        # Each row of the board is separated by a '/'
        s.write('/')
    s.seek(s.tell() - 1)
    fen_string = s.getvalue()
    return fen_string[:-1]


def compare_images_mse(previous_image: np.ndarray, new_image: np.ndarray) -> float:
    """Compares two images using the Mean Squared Error algorithm
    
    :param previous_image: the old image
    :param new_image: the new image to compare with
    :return: A float value of the Mean Square Error of the images. A low value means the images are similar. A high
    value means the images are very different. A value of zero means the images are the same
    """
    err = np.sum((previous_image.astype("float") - new_image.astype("float")) ** 2)
    err /= float(previous_image.shape[0] * previous_image.shape[1])

    return float(err)
