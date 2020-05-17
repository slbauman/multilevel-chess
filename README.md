# multilevel chess

![Alt text](tmlchess_example.png?raw=true "Example Game")

multilevel chess is a 3D chess variant client that runs in a terminal.

The design and rules are based on the [Millenium 3D chess](https://en.wikipedia.org/wiki/Millennium_3D_chess) variant.

## Required Nonstandard Python Modules
* bitarray

Install required modules with

`pip3 install bitarray`

## Usage
To run the client:

`python3 tmlchess.py`

Arrow keys move the cursor.

Enter key or left mouse button selects and moves a piece.

`,` and `.` move the cursor along the Z-axis.

`q` quits the game.

## To-do
- [x] Check and checkmate.
- [x] Castling.
- [x] Very basic multiplayer capability using TCP sockets.
- [ ] En passant.
- [ ] Promotion.
- [ ] Saving and loading of games in chess notation format.

## Notes
* I'm working on this project because it's a fun way to learn how to use sockets and practice coding. Do not expect extremely well written and structured code.
* So far this has only been tested with [alacritty](https://github.com/alacritty/alacritty) and [kitty](https://github.com/kovidgoyal/kitty) terminal emulators in Linux.
* You will likely need to increase your font size for a better experience. CTRL + increases font size in alacritty and CTRL-SHIFT + increases the font size in kitty.
