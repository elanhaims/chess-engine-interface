#import chess_game
import startup
import mss
import screenshot_converter

PIECES = {"black_pawn": 'p', "black_rook": "r", "black_bishop": "b", "black_knight": "n", "black_king": "k",
          "black_queen": "q", "white_pawn": "P", "white_rook": "R", "white_bishop": "B", "white_knight": "N",
          "white_queen": "Q", "white_king": "K"}


class Chess_Session:
    def __init__(self):
        self.sct = mss.mss()
        self.x_coord = 377
        self.y_coord = 172
        self.width = 740
        self.height = 740
        self.monitor_number = 1
        self.monitor = None
        self.white_pixel_color = 248
        self.screenshot_converter = None

    def perform_startup_process(self):
        (x, y, w, h, white_pixel_color) = startup.take_screenshot(self.sct)
        self.x_coord = x
        self.y_coord = y
        self.width = w
        self.height = h
        self.white_pixel_color = white_pixel_color

        screenshot_info_dict = self.create_sct_dict()
        self.screenshot_converter = screenshot_converter.Converter(screenshot_info_dict)

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

    # def create_and_run_chess_game(self):
    #     game = chess_game.Chess_Game(self.screenshot_converter, self.white_pixel_color)
    #     game.run()


if __name__ == "__main__":
    session = Chess_Session()
    session.perform_startup_process()
    screenshot_info = session.create_sct_dict()
    screenshot_converter = screenshot_converter.Converter(screenshot_info)

    #chess_game = chess_game.Chess_Game(screenshot_converter, session.white_pixel_color)
    #chess_game.run()
