import numpy as np
import cv2 as cv

# Dictionary to convert piece names to their FEN representation
PIECES = {"black_pawn": 'p', "black_rook": "r", "black_bishop": "b", "black_knight": "n", "black_king": "k",
          "black_queen": "q", "white_pawn": "P", "white_rook": "R", "white_bishop": "B", "white_knight": "N",
          "white_queen": "Q", "white_king": "K"}

# Dictionary to construct the board position when the user is playing as black. This is used to flip the board. Will
# try to find a better way to do this
WHITE_TO_BLACK_SQUARES = {"1": "8", "2": "7", "3": "6", "4": "5", "5": "4", "6": "3", "7": "2", "8": "1",
                          "a": "h", "b": "g", "c": "f", "d": "e", "e": "d", "f": "c", "g": "b", "h": "a"}


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
    """Iterate through all of the rectangles and find the center pixel coordinate for each one."""
    centers = []
    for (x, y, w, h) in rectangles:
        x_cord = x + w // 2
        y_cord = y + h // 2
        centers.append([int(x_cord), int(y_cord)])
    return centers


def add_pieces_to_board(piece: str, board: np.ndarray, piece_locations: dict, centers: list, player_color: str,
                        square_size: int) -> (np.ndarray, dict):
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
