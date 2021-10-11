import sys
from enum import Enum
import sentinels
import numpy

import chess.engine
import cv2

import time

import chess
import chess.engine
import pyttsx3

import screenshot_converter


tts_engine = pyttsx3.init()

engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish")


class Castling(Enum):
    """Enum that represents the different states of castling"""
    CAN_CASTLE = 0
    CAN_KINGSIDE_CASTLE = 1
    CAN_QUEENSIDE_CASTLE = 2
    CANNOT_CASTLE = 3


# Dictionary to convert the enum states to strings to aid in constructing the fen
CASTLING_DICT = {Castling.CAN_CASTLE: "KQ", Castling.CAN_KINGSIDE_CASTLE: "K", Castling.CAN_QUEENSIDE_CASTLE: "Q",
                 Castling.CANNOT_CASTLE: ""}

# Sentinel value that gets returned when a piece does not get registered from the screenshot. This happens when a
# screenshot gets taken while a piece is in the process of moving from one square to another
PIECE_MISSING = sentinels.Sentinel

# The board fen for the starting position of a chess game
STARTING_BOARD_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


class Chess_Game:
    """Class that contains the functionality  for building the FEN that is used to obtain the best move from the engine.

    The class has methods to find the player color, update the board position when a new screenshot is captured, find
    the number of moves that have occurred since the last time the position was updated, check if either players have
    castled, generates the second half of the FEN, and the main game loop that uses utility functions to screenshot
    the board and generate the new FEN repeatedly.
    """

    def __init__(self, screenshot_util: screenshot_converter):
        """Initializes the Chess_Game instance.

        :param screenshot_util: instance of the Converter class from screenshot_converter.py that is used to screenshot
        the board and convert the screenshot to a board state we can use. The Converter class builds three board states:
        a 2d array of the board, the board FEN for the position, and a dictionary containing the chess pieces as keys
        and arrays of the piece locations as the values.
        """
        # Instance of Converter class
        self.screenshot_util = screenshot_util
        # Used to stop the game loop if the user presses the "Stop Game" button in the gui
        self.game_running = True
        # Color of the pieces the user is playing as. Can be 'white' or 'black'.
        self.player_color = "white"
        # The color of the player whose turn it is to move
        self.current_player = "white"
        # The number of moves that have been made in the game
        self.moves = 0

        # Current state of the board stored as just the board fen. An example of this is:
        # 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
        self.board_fen = None
        # Current state of the board stored as the full fen. An example of this is:
        # 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.fen = None
        # Current state of the board stored as a 2d 8x8 numpy array. A piece on square A1 is stored at [0][0] and a
        # piece on square H8 is stored at [7][7]
        self.board_array = None
        # Current state of the board stored as a dictionary. The keys are the chess piece names and the values are
        # arrays containing the squares those pieces are located on. An example of this is:
        # {"white_pawn": ['a2','b2','c2'], {"black_knight": ['b8', 'f8']}
        self.piece_locations = None

        # Enum value that determines if a play can castle. The possible values are CAN_CASTLE which means the player can
        # castle both ways, CAN_QUEENSIDE_CASTLE, which means the player can only castle to the queenside,
        # CAN_KINGSIDE_CASTLE which means the player can only castle to the kingside, and CANNOT_CASTLE which means
        # the player cannot castle. Defaults to CAN_Castle.
        self.white_castling_rights = Castling.CAN_CASTLE
        self.black_castling_rights = Castling.CAN_CASTLE

    def stop_game(self):
        """Stops the game loop from running. Is called when the 'Stop Game' button is pressed in the gui"""
        self.game_running = False

    def fetch_updated_board_position(self, board_screenshot: cv2.cvtColor) -> (str, numpy.ndarray, dict):
        """Updates and returns the new board position

        :param: board_screenshot: a screenshot of the chess board
        """

        # Retrieves the new position by calling the screenshot utility function
        board_fen, chess_board_array_representation, piece_locations = self.screenshot_util.generate_fen_from_image(
            board_screenshot, self.player_color)

        # Check if the new board FEN is not equal to the currently stored board FEN
        if board_fen != self.board_fen:
            # Finds the number of moves that have been played since the last position was saved. This value is usually 1
            # but can be more if the opponent plays a move very quickly.
            moves = self.find_number_of_moves(chess_board_array_representation)
            # If a piece was not registered from the screenshot return the previous board state without updating
            if moves == PIECE_MISSING:
                return self.board_fen, self.board_array, self.piece_locations
            # If a player castles the 'find_number_of_moves' method will count that as two moves so we check if a
            # player castled on the previous move and subtract 1 from the moves if they have
            elif self.check_if_castling_occurred_last_move(moves, piece_locations):
                moves -= 1
            # Don't update the number of moves the first time the screenshot is converted to a board position. Sometimes
            # when the user is playing as black the player with the white pieces will make a move before the user can
            # press the start game button on the gui so we increase the move counter if this happens
            if self.board_fen or (board_fen != STARTING_BOARD_FEN and self.player_color == "black"
                                  and self.board_fen is None):
                self.moves += moves
            self.current_player = "white" if self.moves % 2 == 0 else "black"

            second_half_of_fen = self.generate_second_half_of_fen(piece_locations)

            # Update all of the instance variables
            self.board_fen = board_fen
            self.fen = board_fen + second_half_of_fen
            self.board_array = chess_board_array_representation
            self.piece_locations = piece_locations

            # Update castling rights
            self.check_castling_rights()
            return board_fen, chess_board_array_representation, piece_locations

    def find_number_of_moves(self, new_board_array: numpy.ndarray):
        """Find the number of moves that have occurred since the last stored position.

        :param new_board_array: a 2d array representation of the chess board
        """
        if self.board_array is None:
            return 1
        else:
            differences = 0
            # Iterate through the 2d arrays. Compare the previous array with the new array. If an element is different
            # between the two arrays, increment the move counter by one.
            for row in range(8):
                for col in range(8):
                    if not self.board_array[row][col] == new_board_array[row][col]:
                        differences += 1
            # If there is only one difference between the arrays, a piece must have not been registered when converting
            # the screenshot so we return the PIECE_MISSING sentinel so we ignore the new board position
            if differences == 1:
                print("PIECE MISSING")
                return PIECE_MISSING
            # Divide the differences by 2 to get the number of moves
            moves = round(differences / 2)
            return moves

    def check_if_castling_occurred_last_move(self, moves: int, new_piece_locations: dict) -> bool:
        """Check if either of the players castled on their previous turn

        :param moves: The number of moves that have occurred between the previous position and the new one.
        :param new_piece_locations: Board state dictionary representation
        """
        if moves == 1:
            return False
        if "e1" in self.piece_locations["white_king"] and ("c1" in new_piece_locations["white_king"] or
                                                           "g1" in new_piece_locations["white_king"]):
            return True
        elif "e8" in self.piece_locations["black_king"] and ("c8" in new_piece_locations["black_king"] or
                                                             "g8" in new_piece_locations["black_king"]):
            return True
        return False

    def generate_second_half_of_fen(self, piece_locations: dict) -> str:
        """Generates the rest of the FEN that comes after the board position"""

        # Will be ' w ' if the current player is white and ' b ' if the current player is black
        current_player = f" {self.current_player[0]} "

        castling = ""
        # Neither player can castle
        if self.white_castling_rights == Castling.CANNOT_CASTLE and \
                self.black_castling_rights == Castling.CANNOT_CASTLE:
            castling = "- "
        # Use the CASTLING_DICT to add a 'Q' to the castling string if the player can queenside castle and a 'K' to
        # the castling string if the player can kingside castle. The letters are uppercase for white and lowercase for
        # black
        else:
            castling += CASTLING_DICT[self.white_castling_rights] + CASTLING_DICT[self.black_castling_rights].lower() \
                        + " "

        # Find a possible en passant square
        en_passant = self.find_en_passant(piece_locations)
        en_passant_target = "- " if en_passant == "" else en_passant + " "

        # Half-move and move counter part of the FEN. Not currently finding half-moves so it is defaulted to 0
        move_number = "0 " + str(self.moves // 2)

        # Combine all of the parts of the FEN
        second_half_of_fen = current_player + castling + en_passant_target + move_number
        return second_half_of_fen

    def check_castling_for_player(self, color) -> Castling:
        """Checks a player's castling rights to see if it has changed.

        :param color: The color of the pieces for which to check the castling rights
        :return: Enum of the player's castling rights. Can be either CAN_CASTLE, CAN_KINGSIDE_CASTLE,
        CAN_QUEENSIDE_CASTLE, or CANNOT_CASTLE
        """
        rank = "1" if color == "white" else "8"
        piece_locations = self.piece_locations
        castling_rights = self.white_castling_rights if color == "white" else self.black_castling_rights
        if not castling_rights == Castling.CANNOT_CASTLE:
            # If king moves then player cannot castle either side
            if f"e{rank}" not in piece_locations[f"{color}_king"]:
                return Castling.CANNOT_CASTLE
            else:
                # If player can castle both sides
                if castling_rights == Castling.CAN_CASTLE:
                    # If the 'a' rook moves player can no longer queenside castle so they can only kingside castle
                    if f"{color}_rook" in piece_locations and f"a{rank}" not in piece_locations[f"{color}_rook"]:
                        return Castling.CAN_KINGSIDE_CASTLE
                    # If the 'h' rook moves player can no longer kingside castle so they can only queenside castle
                    if f"{color}_rook" in piece_locations and f"h{rank}" not in piece_locations[f"{color}_rook"]:
                        return Castling.CAN_QUEENSIDE_CASTLE
                # If player can only queenside castle and their 'a' rook moves then they can no longer castle
                elif castling_rights == Castling.CAN_QUEENSIDE_CASTLE and f"{color}_rook" in piece_locations \
                        and f"a{rank}" not in \
                        piece_locations[f"{color}_rook"]:
                    return Castling.CANNOT_CASTLE
                # If player can only kingside castle and their 'h' rook moves then they can no longer castle
                elif castling_rights == Castling.CAN_KINGSIDE_CASTLE and f"{color}_rook" in piece_locations \
                        and f"h{rank}" not in \
                        piece_locations[f"{color}_rook"]:
                    return Castling.CANNOT_CASTLE
        # Return the original castling rights if the player's castling status has not changed
        return castling_rights

    def check_castling_rights(self):
        """Updates the players' castling rights."""
        # If white already cannot castle do nothing
        if not self.white_castling_rights == Castling.CANNOT_CASTLE:
            self.white_castling_rights = self.check_castling_for_player("white")
        # If black already cannot castle do nothing
        if not self.black_castling_rights == Castling.CANNOT_CASTLE:
            self.black_castling_rights = self.check_castling_for_player("black")

    def find_en_passant(self, piece_locations: dict) -> str:
        """Finds any possible en passant squares. Returns a string of the square position if the en passant square
        exists. An example of this is 'e3'"""
        previous_piece_locations = self.piece_locations
        current_piece_locations = piece_locations
        if previous_piece_locations is not None:
            # Iterate over all of the white pawns on the board in the previous board position
            for white_pawn in previous_piece_locations["white_pawn"]:
                # If a pawn was previously on the 2nd rank and is now on the 4th rank then its an en passant target
                if white_pawn[1] == str(2) and white_pawn not in current_piece_locations["white_pawn"] and (
                        white_pawn[0] + str(4)) \
                        in current_piece_locations["white_pawn"]:
                    return white_pawn[0] + str(3)
            # Iterate over all of the black pawns on the board in the previous board position
            for black_pawn in previous_piece_locations["black_pawn"]:
                # If a pawn was previously on the 7th rank and is now on the 5th rank then its an en passant target
                if black_pawn[1] == str(7) and black_pawn not in current_piece_locations["black_pawn"] and (
                        black_pawn[0] + str(5)) \
                        in current_piece_locations["black_pawn"]:
                    return black_pawn[0] + str(6)
        return ""

    def run(self):
        """The main game loop. Runs until the 'stop_game' method gets called.

        Every iteration of the loop we take a screenshot of the board. If it is the first iteration of the loop,
        get the color of the player. Compare the new screenshot with the previous screenshot to see if the board has
        changed at all. If the screenshot has changed, fetch the updated position and have the engine compute the next
        best move from that position if the user is the next player to move.
        """

        previous_fen = None
        previous_screenshot = None
        first_loop = False
        # Infinitely loop until the 'stop_game' method is called
        while self.game_running:
            # Get a screenshot of the chess board
            current_screenshot = self.screenshot_util.screenshot_chess_board()
            # Update the player color if it is the first iteration of the loop
            if first_loop is False:
                self.player_color = self.screenshot_util.get_player_color(current_screenshot)
            mse = 0
            # Use the Mean Squared Error to determine if the new screenshot is different from the previous screenshot.
            # This is a fast way to compare the screenshots.
            if previous_screenshot is not None:
                # Compute the MSE. This is a float value. A value of zero means there is no difference between the
                # images. A high value for the MSE means there is a large value.
                mse = screenshot_converter.compare_images_mse(current_screenshot, previous_screenshot)
                # If the images are different, sleep for a short period of time and then take another screenshot. This
                # is to hopefully make it so a screenshot does not get taken when a piece is in the process of moving
                # from one square to the other.
                if mse > 0:
                    time.sleep(.2)
                    current_screenshot = self.screenshot_util.screenshot_chess_board()
                    mse = screenshot_converter.compare_images_mse(current_screenshot, previous_screenshot)
            # If the MSE value is too large, this means the board is obstructed and we don't do anything
            if mse > 700:
                print("mse:" + str(mse))
                tts_engine.say("Board is obstructed")
                tts_engine.runAndWait()
            # If the screenshots are different that means the board position has changed
            elif mse > 20 or first_loop is False:
                first_loop = True
                # Updates the board position
                board_fen, board_array, piece_locations = self.fetch_updated_board_position(current_screenshot)
                if board_fen != previous_fen:
                    previous_screenshot = current_screenshot
                    previous_fen = board_fen

                    board = chess.Board(self.fen)
                    # Currently the board is only being printed from white's perspective
                    print(board)
                    # If the user is the next player to make a move
                    if self.current_player == self.player_color:
                        try:
                            # Compute the next best move from the chess engine
                            result = engine.play(board, chess.engine.Limit(time=1))
                            # Prints the move
                            print(result.move)
                            # Text to speech of the move
                            tts_engine.say(str(result.move))
                            tts_engine.runAndWait()

                        # In case of errors with the engine
                        except:
                            e = sys.exc_info()[0]
                            print(e)
                            print(board)
                            tts_engine.say("error occurred")
                            tts_engine.runAndWait()
                    # If it is the opponents turn to move
                    else:
                        # Text to speech
                        tts_engine.say("Waiting on opponent to move")
                        print("waiting on opponent to move")
                        tts_engine.runAndWait()
                else:
                    print("Something went wrong")
