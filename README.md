# Computer Vision Assisted Chess Engine Interface for Chess.Com

## Introduction

This project uses python and opencv template matching to convert screenshots of a chess 
board into a FEN string. Then, the FEN string is passed into a chess engine which returns
the optimal move to play in the position.

## Disclaimer

Using a chess engine is against the Chess.com terms of service. I created this project
for learning purposes and not as a means to cheat in online rated chess matches. 
I have been given permission by the Chess.com staff to build and test this project. 
If you wish to test this project, you must do so in an unrated game against a 
user on your friends list. You must also get their written permission to use a
chess engine against them in the Chess.com game chat before the game begins. 
Failure to follow these rules can result in the termination of your Chess.com account.

## Installation
* Make sure you have python installed on your machine
* Clone the repository to a directory of your choosing
* Open a terminal window and navigate to the root directory of the project
* Run the command 'pip install -r requirements.txt' to install all the necessary python modules <br>
* If you do not wish to clone the repository with all the stockfish files:
    * Clone the repository from the branch 'without_stockfish'
    * Download your chess engine of choice
    * In line 20 of chess_game.py, replace "stockfish/stockfish" with the path to the chess engine executable:
  ```
      engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish")
    ```

## Chess.com Board Setup
For the best results when using this program, there are a few settings you must use for the chess board. <br>
First, make sure that your Chess.com window is opened on your main computer monitor. <br>
Then, copy the following settings under the Chess.com board settings:
![Settings](starting_templates/settings.PNG)

## Using the program
* To launch the program, open a terminal and navigate to the root directory of 
the project.
*  From there, run the command 'python gui.py'. This will 
launch a simple gui with three buttons. <br>
* Move the gui so that it does not cover the chess board at all. You may also want to move 
the terminal window to somewhere visible to see print statements. <br>
* Navigate to www.chess.com/play/online and make sure you are logged in to a chess.com account
  * Your window should look something like this:
    ![Example Window](starting_templates/example_window.png)

* Click the 'Perform Setup' button to initialize the project.
This may take a few seconds and only needs to be done once each time you run the program.
  * After you run the setup, make sure to not move or resize the chess window, or the program will not work.
* After the setup has completed, you can begin a game of chess. Once you are matched 
against an opponent, click the 'start game' button on the gui to begin getting the optimal chess moves.
  * The program works for playing as both the white and black pieces.
  * At any time, you can click the 'stop game' button to stop communication with the chess engine. 
    You can then start the engine again on a new game.
      * You must always press the 'start game' button from the starting chess position. 
        The only exception to this is when playing as the black pieces, 
        you can start the game after white has made their first move.
* When it is your turn to make a move in the game, the program will output the best move 
  to play to the console as well as text to speech audio output.
* When making moves, do not drag the piece you are moving to the new square. Instead, click 
on the piece you would like to move, and then click on the square you would like to move it to. This is to prevent the 
  image detection from incorrectly reading the board position.
* Instead of running the program on a live game, you can also run the program on a previously completed one
  by stepping through the game move by move using your keyboard's arrow keys.  
  
## Code Walk-through


## Future Plans for the project