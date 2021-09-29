import chess_game
import startup
import mss
import numpy as np
import cv2 as cv
import image_to_board_representation_util as util
import chess
import chess.engine
import time
import screenshot_converter

PIECES = {"black_pawn": 'p', "black_rook": "r", "black_bishop": "b", "black_knight": "n", "black_king": "k",
          "black_queen": "q", "white_pawn": "P", "white_rook": "R", "white_bishop": "B", "white_knight": "N",
          "white_queen": "Q", "white_king": "K"}

engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish")

class Chess_Session():
    def __init__(self):
        self.sct = mss.mss()
        self.x_coord = 377
        self.y_coord = 172
        self.width = 740
        self.height = 740
        self.monitor_number = 1
        self.monitor = None

    def perform_startup_process(self):
        (x, y, w, h) = startup.take_screenshot(self.sct)
        self.x_coord = x
        self.y_coord = y
        self.width = w
        self.height = h
        #print(x, y, w, h)

    def set_monitor(self):
        mon = self.sct.monitors[self.monitor_number]
        monitor = {
            "top": mon["top"] + self.y_coord,
            "left": mon["left"] + self.x_coord,
            "width": self.width,
            "height": self.height,
            "mon": self.monitor_number,
        }
        self.monitor = monitor

    def create_sct_dict(self):
        mon = self.sct.monitors[self.monitor_number]
        monitor = {
            "top": mon["top"] + self.y_coord,
            "left": mon["left"] + self.x_coord,
            "width": self.width,
            "height": self.height,
            "mon": self.monitor_number,
        }
        return {"sct": self.sct, "monitor": monitor, "width": self.width}

    # def screenshot_chess_board(self):
    #     mon = self.sct.monitors[self.monitor_number]
    #     monitor = {
    #         "top": mon["top"] + self.y_coord,
    #         "left": mon["left"] + self.x_coord,
    #         "width": self.width,
    #         "height": self.height,
    #         "mon": self.monitor_number,
    #     }
    #
    #     img = np.array(self.sct.grab(monitor))
    #
    #     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #     width = height = (self.width // 8) * 8
    #     gray = cv.resize(gray, (width, height), interpolation=cv.INTER_LINEAR)
    #     #cv.imshow("board rep", gray)
    #     #cv.waitKey(0)
    #     return gray
    #
    # def convert_screenshot_to_chess_board_array_representation(self, board_screenshot):
    #     chess_board = np.zeros((8, 8), dtype='U2')
    #     for piece in PIECES.keys():
    #         rectangles = util.locate_piece(piece, board_screenshot)
    #         centers = util.find_centers(rectangles)
    #         chess_board = util.add_pieces_to_board(piece, chess_board, centers)
    #     #print(np.flip(chess_board, axis=0))
    #     return chess_board

if __name__ == "__main__":
    session = Chess_Session()
    previous_FEN = None
    screenshot_info = session.create_sct_dict()
    screenshot_converter = screenshot_converter.Converter(screenshot_info)

    chess_game = chess_game.Chess_Game(screenshot_converter)
    chess_game.run()
    # while(True):
    #     chess_game.fetch_updated_board_position()
    #     second_fen = chess_game.generate_second_half_of_fen()
    #     full_fen = chess_game.board_fen + second_fen
    #     print(full_fen)
    #     board = chess.Board(full_fen)
    #     print(board)
    #     time.sleep(2)


        # board_fen, chess_board_array_representation, piece_locations = screenshot_converter.generate_fen_from_image()
        # chess_board_array = np.flip(chess_board_array_representation, axis=0)
        # if board_fen != previous_FEN:
        #     print(board_fen)
        #     board = chess.Board(board_fen)
        #     print(board)
        #     #result = engine.play(board, chess.engine.Limit(time=0.5))
        #     #print(result)
        #     #print(chess_board_array)
        #     print(piece_locations)
        # previous_FEN = board_fen

        #time.sleep(2)


        # #session.perform_startup_process()
        # board_screenshot = session.screenshot_chess_board()
        # chess_board_array = session.convert_screenshot_to_chess_board_array_representation(board_screenshot)
        # FEN = util.convert_array_to_FEN(np.flip(chess_board_array, axis=0))
        # if FEN != previous_FEN:
        #     print(FEN)
        #     board = chess.Board(FEN)
        #     print(board)
        #     result = engine.play(board, chess.engine.Limit(time=0.5))
        #     print(result)
        # previous_FEN = FEN
        #
        # time.sleep(2.5)