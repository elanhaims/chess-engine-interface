import io

import chess, chess.engine
import numpy as np

import screenshot_converter
import time
from io import BytesIO
import os
import pyttsx3
import cv2 as cv

tts_engine = pyttsx3.init()

engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish")

#f = BytesIO()


class Chess_Game():
    def __init__(self, screenshot_util: screenshot_converter):
        self.screenshot_util = screenshot_util
        self.player_color = "white"
        self.current_player = "white"
        self.moves = 0
        self.board_fen = None
        self.previous_board_fen = None
        self.fen = None
        self.board_array = None
        self.previous_board_array = None
        self.previous_piece_locations = None
        self.piece_locations = None
        self.white_can_castle = True
        self.black_can_castle = True
        self.black_king_moved = False
        self.white_king_moved = False
        self.black_a_rook_moved = False
        self.white_a_rook_moved = False
        self.black_h_rook_moved = False
        self.white_h_rook_moved = False

    def fetch_updated_board_position(self, screenshot):
        board_fen, chess_board_array_representation, piece_locations = self.screenshot_util.generate_fen_from_image(screenshot)
        if board_fen != self.board_fen:
            if self.board_fen:
                self.moves += 1
            self.previous_board_fen = self.board_fen
            self.previous_board_array = self.board_array
            self.previous_piece_locations = self.piece_locations
            self.board_fen = board_fen
            self.board_array = chess_board_array_representation
            self.piece_locations = piece_locations
            self.current_player = "white" if self.moves % 2 == 0 else "black"
            return board_fen, chess_board_array_representation, piece_locations

    def generate_second_half_of_fen(self):
        second_half = " "
        if self.moves % 2 == 0:
            second_half += "w "
        else:
            second_half += "b "

        castling = ""
        if not self.white_can_castle and not self.black_can_castle:
            castling = "- "
        else:
            if not self.white_a_rook_moved:
                castling += 'Q'
            if not self.white_h_rook_moved:
                castling += 'K'
            if not self.black_a_rook_moved:
                castling += 'q'
            if not self.black_h_rook_moved:
                castling += 'k'
            castling += " "

        second_half += castling
        en_passant = self.find_en_passant()
        second_half += "- 0 " if en_passant is None else en_passant + " 0 "
        second_half += str(self.moves // 2)
        return second_half

    def check_castling_rights(self):
        piece_locations = self.piece_locations
        if self.white_can_castle:
            if "e1" not in piece_locations["white_king"]:
                self.white_king_moved = True
                self.white_can_castle = False
            if "white_rook" in piece_locations and "a1" not in piece_locations["white_rook"]:
                self.white_a_rook_moved = True
            if "white_rook" in piece_locations and "h1" not in piece_locations["white_rook"]:
                self.white_h_rook_moved = True
            if "white_rook" in piece_locations and "a1" not in piece_locations["white_rook"] and "h1" not in \
                    piece_locations["white_rook"]:
                self.white_can_castle = False
        if self.black_can_castle:
            if "e8" not in piece_locations["black_king"]:
                self.black_king_moved = True
                self.black_can_castle = False
            if "black_rook" in piece_locations and "a8" not in piece_locations["black_rook"]:
                self.black_a_rook_moved = True
            if "black_rook" in piece_locations and "h8" not in piece_locations["black_rook"]:
                self.black_h_rook_moved = True
            if "black_rook" in piece_locations and "a8" not in piece_locations["black_rook"] and "h8" not in \
                    piece_locations["black_rook"]:
                self.black_can_castle = False

    def find_en_passant(self):
        previous_piece_locations = self.previous_piece_locations
        current_piece_locations = self.piece_locations
        if not previous_piece_locations is None:
            for white_pawn in previous_piece_locations["white_pawn"]:
                if white_pawn[1] == str(2) and white_pawn not in current_piece_locations["white_pawn"] and (white_pawn[0] + str(4)) \
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
        while True:
            current_screenshot = self.screenshot_util.screenshot_chess_board()
            # print(np.array_equal(previous_screenshot, current_screenshot))
            ssim = 1
            if previous_screenshot is not None:
                ssim = self.screenshot_util.compare_images(current_screenshot, previous_screenshot)
                if ssim != 1:
                    time.sleep(.4)
                    current_screenshot = self.screenshot_util.screenshot_chess_board()
                    ssim = self.screenshot_util.compare_images(current_screenshot, previous_screenshot)
                    print("2nd: " + str(ssim))
            if ssim < .95:
                tts_engine.say("Board is obstructed")
                tts_engine.runAndWait()
            if ssim < .9999 or first_loop is False:
                first_loop = True
                previous_screenshot = current_screenshot
                board_fen, board_array, piece_locations = self.fetch_updated_board_position(current_screenshot)
                if board_fen != previous_fen:
                    print(self.current_player)
                    previous_fen = board_fen
                    second_fen = self.generate_second_half_of_fen()
                    self.fen = self.board_fen + second_fen
                    board = chess.Board(self.fen)
                    if self.current_player == self.player_color:
                        result = engine.play(board, chess.engine.Limit(time=1))
                        print(result.move)
                        tts_engine.say(str(result.move))
                        tts_engine.runAndWait()
                    else:
                        tts_engine.say("Waiting on black to move")
                        tts_engine.runAndWait()
                else:
                    print("testing")
            #time.sleep(2)



    #
    # def run(self):
    #     previous_fen = self.board_fen
    #     previous_screenshot = None
    #     while True:
    #         current_screenshot = self.screenshot_util.screenshot_chess_board()
    #         # print(np.array_equal(previous_screenshot, current_screenshot))
    #         if not np.array_equal(previous_screenshot, current_screenshot):
    #             previous_screenshot = current_screenshot
    #             self.fetch_updated_board_position()
    #             if self.board_fen != previous_fen:
    #                 print(self.current_player)
    #                 previous_fen = self.board_fen
    #                 second_fen = self.generate_second_half_of_fen()
    #                 self.fen = self.board_fen + second_fen
    #                 board = chess.Board(self.fen)
    #                 if self.current_player == self.player_color:
    #                     result = engine.play(board, chess.engine.Limit(time=1))
    #                     print(result.move)
    #                     tts_engine.say(str(result.move))
    #                     tts_engine.runAndWait()
    #                 else:
    #                     tts_engine.say("Waiting on black to move")
    #                     tts_engine.runAndWait()
    #             else:
    #                 print("testing")
    #         #time.sleep(2)
