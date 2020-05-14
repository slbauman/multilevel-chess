# TMLChess
Terminal multi-level chess

![Alt text](image/tmlchess_example.png?raw=true "Example Game")

TMLChess is a multi-level chess client that runs in a terminal.

The design and rules are based on [Millenium 3D chess](https://en.wikipedia.org/wiki/Millennium_3D_chess).

## Required Python Libraries
* curses
* bitarray

## Usage
To run the client:

`python3 tmlchess.py`

Arrow keys move the cursor around.

Enter key selects or moves a piece.

`,` and `.` move the cursor along the Z-axis.

`q` quits the game.

## Todo
* Add all rules beyond basic moving/taking.
* Add multiplayer over network capability using websockets.
* Add saving and loading of games.

## Notes
* So far this has only been tested and working with [Alacritty](https://github.com/alacritty/alacritty) and [kitty](https://github.com/kovidgoyal/kitty) terminal emulators on an Arch Linux machine.
