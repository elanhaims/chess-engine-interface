import numpy as np
import cv2 as cv
from skimage.metrics import structural_similarity as compute_ssim
import image_to_board_representation_util as util
from io import StringIO
from chess_session import PIECES



class Converter:
    def __init__(self, screenshot_info):
        self.screenshot_info = screenshot_info

    def screenshot_chess_board(self):
        sct = self.screenshot_info["sct"]
        monitor = self.screenshot_info["monitor"]
        width = self.screenshot_info["width"]

        img = np.array(sct.grab(monitor))
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        width = height = (width // 8) * 8
        gray = cv.resize(gray, (width, height), interpolation=cv.INTER_LINEAR)
        return gray

    def get_player_color(self, board_screenshot):
        board_width = (self.screenshot_info["width"] // 8) * 8
        square_width = (board_width // 8)
        queen = board_screenshot[7 * square_width:board_width, 3 * square_width:4 * square_width]
        queen_pixel_color = queen[square_width // 2, square_width // 2]
        return queen_pixel_color

    @staticmethod
    def convert_screenshot_to_chess_board_array_representation(board_screenshot):
        chess_board = np.zeros((8, 8), dtype='U2')
        piece_locations = {}
        for piece in PIECES.keys():
            rectangles = util.locate_piece(piece, board_screenshot)
            centers = util.find_centers(rectangles)
            chess_board, piece_locations = util.add_pieces_to_board(piece, chess_board, piece_locations, centers)
        return chess_board, piece_locations

    @staticmethod
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
        fen_string = s.getvalue()
        return fen_string[:-1]

    def generate_fen_from_image(self, screenshot):
        board_image = screenshot
        chess_board_array_representation, piece_locations = \
            self.convert_screenshot_to_chess_board_array_representation(board_image)
        board_fen = self.convert_array_to_FEN(np.flip(chess_board_array_representation, axis=0))
        return board_fen, chess_board_array_representation, piece_locations

    def screenshot_and_generate_fen(self):
        board_image = self.screenshot_chess_board()
        chess_board_array_representation, piece_locations = \
            self.convert_screenshot_to_chess_board_array_representation(board_image)
        board_fen = self.convert_array_to_FEN(np.flip(chess_board_array_representation, axis=0))
        return board_fen, chess_board_array_representation, piece_locations

    @staticmethod
    def compare_images(image1, image2):
        ssim = compute_ssim(image1, image2)
        return ssim

    @staticmethod
    def compare_images_mse(image1, image2):
        err = np.sum((image1.astype("float") - image2.astype("float")) ** 2)
        err /= float(image1.shape[0] * image1.shape[1])

        return err
