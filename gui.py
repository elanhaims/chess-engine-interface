import tkinter as tk
import chess_session
import chess_game
from threading import *

window = tk.Tk()
window.geometry("500x500")
session = chess_session.Chess_Session()

game_running = True

game = None

startup_performed = tk.BooleanVar(window, False)


def perform_startup():
    startup_performed.set(True)
    session.perform_startup_process()


def create_and_run_chess_game():
    global game
    game = chess_game.Chess_Game(session.screenshot_converter, session.white_pixel_color)
    game.run()


def threading():
    t1 = Thread(target=create_and_run_chess_game)
    t1.start()


def stop_game():
    game.game_running = False


startup_button = tk.Button(window, text="Perform Startup", command=perform_startup)
startup_button.pack()


start_game_button = tk.Button(window, text="Start Chess Game", command=threading)
start_game_button.pack()

stop_game_button = tk.Button(window, text="Stop Chess Game", command=stop_game)
stop_game_button.pack()



window.mainloop()