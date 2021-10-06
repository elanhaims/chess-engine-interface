import sys
from enum import Enum

import chess.engine

import time

import chess
import chess.engine
import pyttsx3

import screenshot_converter
#from gui import is_game_running

tts_engine = pyttsx3.init()

engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish")

class Castling(Enum):
    CAN_CASTLE = 0
    CAN_KINGSIDE_CASTLE = 1
    CAN_QUEENSIDE_CASTLE = 2
    CANNOT_CASTLE = 3


CASTLING_DICT = {Castling.CAN_CASTLE: "KQ", Castling.CAN_KINGSIDE_CASTLE: "K", Castling.CAN_QUEENSIDE_CASTLE: "Q", 
                 Castling.CANNOT_CASTLE: ""}
PIECE_MISSING = -10000

STARTING_BOARD_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


class Chess_Game:
    def __init__(self, screenshot_util: screenshot_converter, white_pixel_color):
        self.screenshot_util = screenshot_util
        self.game_running = True
        self.player_color = "white"
        self.current_player = "white"
        self.moves = 0
        self.white_pixel_color = white_pixel_color
        self.first_move = True

        self.previous_board_fen = None
        self.previous_board_array = None
        self.previous_piece_locations = None
        self.board_fen = None
        self.board_array = None
        self.piece_locations = None

        self.white_castling_rights = Castling.CAN_CASTLE
        self.black_castling_rights = Castling.CAN_CASTLE

    def new_game(self):
        self.game_running = True
        self.player_color = "white"
        self.current_player = "white"
        self.moves = 0

        self.previous_board_fen = None
        self.previous_board_array = None
        self.previous_piece_locations = None
        self.board_fen = None
        self.board_array = None
        self.piece_locations = None

        self.white_castling_rights = Castling.CAN_CASTLE
        self.black_castling_rights = Castling.CAN_CASTLE

    def stop_game(self):
        self.game_running = False

    def get_player_color(self, board_screenshot):
        queen_pixel_color = self.screenshot_util.get_player_color(board_screenshot)
        print(f"queen_pixel_color: {queen_pixel_color}")
        if queen_pixel_color != self.white_pixel_color:
            self.player_color = "black"
        print(f"player color: {self.player_color}")

    def fetch_updated_board_position(self, screenshot):
        board_fen, chess_board_array_representation, piece_locations = self.screenshot_util.generate_fen_from_image(
            screenshot, self.player_color)
        if board_fen != self.board_fen:
            moves = self.find_number_of_moves(chess_board_array_representation, board_fen)
            if moves == PIECE_MISSING:
                return self.board_fen, self.board_array, self.piece_locations
            elif self.check_if_castling_occurred(moves, piece_locations):
                moves -= 1
            if self.board_fen or (board_fen != STARTING_BOARD_FEN and self.player_color == "black" and self.first_move):
                self.moves += moves
                self.first_move = False
            self.previous_board_fen = self.board_fen
            self.previous_board_array = self.board_array
            self.previous_piece_locations = self.piece_locations
            self.board_fen = board_fen
            self.board_array = chess_board_array_representation
            self.piece_locations = piece_locations
            self.current_player = "white" if self.moves % 2 == 0 else "black"

            # Update castling rights
            self.check_castling_rights()
            return board_fen, chess_board_array_representation, piece_locations

    def find_number_of_moves(self, new_board_array, board_fen):
        if self.board_array is None:
            return 1
        else:
            moves = 0
            for row in range(8):
                for col in range(8):
                    if not self.board_array[row][col] == new_board_array[row][col]:
                        moves += 1
            if moves == 1:
                print("PIECE MISSING")
                return PIECE_MISSING
            moves = round(moves / 2)
            return moves

    def check_if_castling_occurred(self, moves, new_piece_locations):
        moves /= 1
        if moves == 1:
            return False
        if "e1" in self.piece_locations["white_king"] and ("c1" in new_piece_locations["white_king"] or
                                                           "g1" in new_piece_locations["white_king"]):
            return True
        elif "e8" in self.piece_locations["black_king"] and ("c8" in new_piece_locations["black_king"] or
                                                             "g8" in new_piece_locations["black_king"]):
            return True
        else:
            return False

    def generate_second_half_of_fen(self):
        current_player = " w " if self.moves % 2 == 0 else " b "

        castling = ""
        if self.white_castling_rights == Castling.CANNOT_CASTLE and \
                self.black_castling_rights == Castling.CANNOT_CASTLE:
            castling = "- "
        else:
            castling += CASTLING_DICT[self.white_castling_rights] + CASTLING_DICT[self.black_castling_rights].lower() \
                        + " "

        en_passant = self.find_en_passant()
        en_passant_target = "- " if en_passant is None else en_passant + " "

        # Not currently finding half-moves
        move_number = "0 " + str(self.moves // 2)

        second_half_of_fen = current_player + castling + en_passant_target + move_number
        return second_half_of_fen

    def check_castling_rights(self):
        piece_locations = self.piece_locations
        if not self.white_castling_rights == Castling.CANNOT_CASTLE:
            if "e1" not in piece_locations["white_king"]:
                self.white_castling_rights = Castling.CANNOT_CASTLE
            else:
                if self.white_castling_rights == Castling.CAN_CASTLE:
                    if "white_rook" in piece_locations and "a1" not in piece_locations["white_rook"]:
                        self.white_castling_rights = Castling.CAN_KINGSIDE_CASTLE
                    if "white_rook" in piece_locations and "h1" not in piece_locations["white_rook"]:
                        self.white_castling_rights = Castling.CAN_QUEENSIDE_CASTLE
                elif self.white_castling_rights == Castling.CAN_QUEENSIDE_CASTLE and "white_rook" in piece_locations \
                        and "a1" not in \
                        piece_locations["white_rook"]:
                    self.white_castling_rights = Castling.CANNOT_CASTLE
                elif self.white_castling_rights == Castling.CAN_KINGSIDE_CASTLE and "white_rook" in piece_locations \
                        and "h1" not in \
                        piece_locations["white_rook"]:
                    self.white_castling_rights = Castling.CANNOT_CASTLE
        if not self.black_castling_rights == Castling.CANNOT_CASTLE:
            if "e8" not in piece_locations["black_king"]:
                self.black_castling_rights = Castling.CANNOT_CASTLE
            else:
                if self.black_castling_rights == Castling.CAN_CASTLE:
                    if "black_rook" in piece_locations and "a8" not in piece_locations["black_rook"]:
                        self.black_castling_rights = Castling.CAN_KINGSIDE_CASTLE
                    if "black_rook" in piece_locations and "h8" not in piece_locations["black_rook"]:
                        self.black_castling_rights = Castling.CAN_QUEENSIDE_CASTLE
                elif self.black_castling_rights == Castling.CAN_QUEENSIDE_CASTLE and "black_rook" in piece_locations \
                        and "a8" not in \
                        piece_locations["black_rook"]:
                    self.black_castling_rights = Castling.CANNOT_CASTLE
                elif self.black_castling_rights == Castling.CAN_KINGSIDE_CASTLE and "black_rook" in piece_locations \
                        and "h8" not in \
                        piece_locations["black_rook"]:
                    self.black_castling_rights = Castling.CANNOT_CASTLE

    def find_en_passant(self):
        previous_piece_locations = self.previous_piece_locations
        current_piece_locations = self.piece_locations
        if previous_piece_locations is not None:
            for white_pawn in previous_piece_locations["white_pawn"]:
                if white_pawn[1] == str(2) and white_pawn not in current_piece_locations["white_pawn"] and (
                        white_pawn[0] + str(4)) \
                        in current_piece_locations["white_pawn"]:
                    return white_pawn[0] + str(3)
            for black_pawn in previous_piece_locations["black_pawn"]:
                if black_pawn[1] == str(7) and black_pawn not in current_piece_locations["black_pawn"] and (
                        black_pawn[0] + str(5)) \
                        in current_piece_locations["black_pawn"]:
                    return black_pawn[0] + str(6)

    def run(self):
        previous_fen = None
        previous_screenshot = None
        first_loop = False
        while self.game_running:
            current_screenshot = self.screenshot_util.screenshot_chess_board()
            if first_loop is False:
                self.get_player_color(current_screenshot)
            mse = 0
            if previous_screenshot is not None:
                mse = self.screenshot_util.compare_images_mse(current_screenshot, previous_screenshot)
                if mse > 0:
                    time.sleep(.2)
                    current_screenshot = self.screenshot_util.screenshot_chess_board()
                    mse = self.screenshot_util.compare_images_mse(current_screenshot, previous_screenshot)

            if mse > 700:
                print("mse:" + str(mse))
                tts_engine.say("Board is obstructed")
                tts_engine.runAndWait()
            elif mse > 20 or first_loop is False:
                first_loop = True
                board_fen, board_array, piece_locations = self.fetch_updated_board_position(current_screenshot)
                if board_fen != previous_fen:
                    previous_screenshot = current_screenshot
                    print(board_fen)
                    print(self.current_player)
                    previous_fen = board_fen
                    second_fen = self.generate_second_half_of_fen()
                    fen = self.board_fen + second_fen
                    print(fen)
                    board = chess.Board(fen)

                    if self.player_color == "black":
                        print(board.transform(chess.flip_vertical))
                    else:
                        print(board)
                    if self.current_player == self.player_color:
                        try:
                            result = engine.play(board, chess.engine.Limit(time=1))
                            tts_engine.say(str(result.move))
                            tts_engine.runAndWait()
                            print(result.move)
                        except:
                            e = sys.exc_info()[0]
                            print(e)
                            print(board)
                            tts_engine.say("error occurred")
                            tts_engine.runAndWait()

                    else:
                        tts_engine.say("Waiting on opponent to move")
                        print("waiting on opponent to move")
                        tts_engine.runAndWait()
                else:
                    print("Something went wrong")
