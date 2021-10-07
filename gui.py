import tkinter as tk
import chess_game
import setup

from threading import *

import pyttsx3

tts_engine = pyttsx3.init()


# Creates the gui window
window = tk.Tk()
window.geometry("500x500")

# Initializes the setup instance
session = setup.Setup()

# Used to store the screenshot converter instance 
converter = None

# Used to store the chess game instance
game = None

# Used to determine if the setup has been done
setup_performed = tk.BooleanVar(window, False)


def perform_setup():
    """Method connected to a gui button that performs the setup."""
    setup_performed.set(True)
    screenshot_converter = session.perform_setup()
    global converter
    converter = screenshot_converter


def create_and_run_chess_game():
    """Method connected to a gui button that creates and runs a chess game as long as the setup has been done"""
    if not setup_performed.get():
        print("Must perform setup first")
        tts_engine.say("Must perform setup first")
        tts_engine.runAndWait()
        return
    global game
    game = chess_game.Chess_Game(converter)
    game.run()


def threading():
    """Runs the 'create_and_run_chess_game' method as a separate thread to prevent blocking because it runs as an
    infinite loop."""
    t1 = Thread(target=create_and_run_chess_game)
    t1.start()


def stop_game():
    """Stops the game loop so the user can start a new game."""
    game.game_running = False


# Setup button connected to the 'perform_setup()' method
setup_button = tk.Button(window, text="Perform Setup", command=perform_setup)
setup_button.pack()

# Start game button connected to the 'threading()' method
start_game_button = tk.Button(window, text="Start Chess Game", command=threading)
start_game_button.pack()

# Stop game button connected to the 'stop_game()' method
stop_game_button = tk.Button(window, text="Stop Chess Game", command=stop_game)
stop_game_button.pack()

# Starts the gui event loop
window.mainloop()
