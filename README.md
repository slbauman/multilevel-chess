# multilevel chess

![Alt text](image/tmlchess_example.png?raw=true "Example Game")

multilevel chess is a 3D chess variant client that runs in a terminal.

The design and rules are based on the [Millenium 3D chess](https://en.wikipedia.org/wiki/Millennium_3D_chess) variant.

## Nonstandard Python Modules
* bitarray

## Usage
To run the client:

`python3 tmlchess.py`

Arrow keys move the cursor.

Enter key or left mouse button selects and moves a piece.

`,` and `.` move the cursor along the Z-axis.

`q` quits the game.

## TO DO
* Add all rules beyond basic moving/taking.
* Add multiplayer over network capability using websockets.
* Add saving and loading of games.

## Notes
* So far this has only been tested with [alacritty](https://github.com/alacritty/alacritty) and [kitty](https://github.com/kovidgoyal/kitty) terminal emulators in Linux.
* You will likely need to increase your font size for a better experience. CTRL + increases font size in alacritty and CTRL-SHIFT + increases the font size in kitty.
