#!/usr/bin/env python3

# TMLChess.py
# Terminal Muli-level Chess
# Samuel Bauman 2020

import curses, curses.panel
import mlchess

# Offset values for drawing to the terminal
os_y = 3
os_x = 2

# Defines the symbols to be used in the terminal
piece = {
        'utf8': ['♚','♛','♜','♞','♝','♟',''],
        'ascii': ['K','Q','R','N','B','P','']
        }

def main():
    try:
        stdscr = curses.initscr()

        curses.start_color()
        curses.use_default_colors()

        # Set up all of the colors pairs (FG, BG) to be used
        curses.init_pair(2, 255, 179)
        curses.init_pair(3, 255, 130)
        curses.init_pair(4, 232, 179)
        curses.init_pair(5, 232, 130)

        curses.init_pair(6, 184, 232)

        curses.init_pair(7, 232, 234)
        curses.init_pair(8, 232, -1)

        curses.init_pair(9, 22, 179)
        curses.init_pair(10, 34, 130)
        curses.init_pair(11, 160, 232)

        # Set up curses environment
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        stdscr.keypad(1)

        panel = curses.panel.new_panel(stdscr)
        game = mlchess.MultilevelChess()

        stdscr.refresh()

        # Game loop
        while 1:
            # Gets the currently selected grid position
            select_pos = game.get_select_pos()

            # Draw all three boards
            for z in range(3):
                for y in range(8):
                    for x in range(8):

                        # Gets information about current X,Y,Z grid from the board.
                        board_data = game.get_board_at(x,y,z)

                        # Piece ID  Used for selecting corresponding UTF-8 symbol.
                        p_id = board_data[1]

                        # Sets the color pair to be used for the board and any piece.
                        color_P = ((x + y) % 2) + 2 + (board_data[0] * 2)

                        # Sets the screen X and Y position
                        pos_y = os_y + y - z
                        pos_x = os_x + (x * 2) + (z * 18)

                        # Highligts current square if it currently selected
                        if select_pos == [x,y,z]: color_P = 6


                        # This sets the text to be drawn for the current grid position 
                        # based on board_data[1], which is the piece rank. 
                        # Also, based on board_data[2], it draws a green circle if the 
                        # current grid position is a valid move position in the 
                        # movement mask, or highlights opponent pieces red.

                        if board_data[1] >= 0:
                            text = "{:2}".format(piece['utf8'][p_id] + " ")
                            if board_data[2] == 1:
                                color_P = 11
                        elif board_data[2] == 1:
                            text = "⬤ "
                            color_P += 7
                        else:
                            text = "  "

                        # Performs the drawing to the curses panel
                        panel.window().addstr(
                                pos_y,
                                pos_x,
                                text,
                                curses.color_pair(color_P))

                        # Optional: Draws a shadow below the boards for 3D effect.
                        if x == 0 or y in range(7-z,8):
                            panel.window().addstr(
                                pos_y + z + 1,
                                pos_x - 1,
                                "  " if y in range(7-z,8) else " ",
                                curses.color_pair(7))

            # Handle keyboard input from the player
            c = stdscr.getch()
            if c == ord("q"):
                break
            elif c == 260:
                game.set_select_pos([select_pos[0]-1,select_pos[1],select_pos[2]])
            elif c == 259:
                game.set_select_pos([select_pos[0],select_pos[1]-1,select_pos[2]])
            elif c == 261:
                game.set_select_pos([select_pos[0]+1,select_pos[1],select_pos[2]])
            elif c == 258:
                game.set_select_pos([select_pos[0],select_pos[1]+1,select_pos[2]])
            elif c == ord("."):
                game.set_select_pos([select_pos[0],select_pos[1],select_pos[2]+1])
            elif c == ord(","):
                game.set_select_pos([select_pos[0],select_pos[1],select_pos[2]-1])
            elif c == 10:
                game.set_select(True)
            #elif c == curses.KEY_RESIZE:
            #   # This should resize the terminal, but only seems to only lock up the program
            #   # when the terminal is resized. Disabling for now.
            #    y, x = stdscr.getmaxyx()
            #    curses.resizeterm(y, x)
            #    stdscr.refresh()

            curses.panel.update_panels(); #stdscr.refresh()

    finally:
        # Clean up and exit
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

if __name__ == '__main__':
    main()
