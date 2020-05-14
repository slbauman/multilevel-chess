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

## Todo
* Add all rules beyond basic moving/taking.
* Add multiplayer over network capability using websockets.

## Notes
* So far this has only been tested and working with [Alacritty](https://github.com/alacritty/alacritty) and [kitty](https://github.com/kovidgoyal/kitty) terminal emulators on an Arch Linux machine.
