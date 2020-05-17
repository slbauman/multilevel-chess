"""

tmlchess.py
Muli-level chess terminal client
Samuel Bauman 2020

"""

import socket
import curses, curses.panel
import mlchess

import sys
from time import sleep
import errno

# Offset values for drawing to the terminal
os_y = 3
os_x = 2

DEFAULT_PORT = "51239"

# Defines the symbols to be used in the terminal
piece = {
        'utf8': ['♚','♛','♜','♞','♝','♟',''],
        'ascii': ['K','Q','R','N','B','P','']
        }

def menu_input(stdscr, r, c, prompt_string):
    stdscr.clear()
    curses.echo()
    stdscr.addstr(r, c, prompt_string)
    stdscr.refresh()
    user_in = stdscr.getstr(r + 1, c, 20)
    user_in = user_in.decode().replace(' ', '')
    stdscr.clear()
    return user_in

def display_msg(stdscr, msg):
    #stdscr.clear()
    stdscr.addstr(1, 1, msg)
    stdscr.refresh()

def main():
    try:
        stdscr = curses.initscr()

        game_type = ''
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

        curses.init_pair(12, 135, 232)

        while game_type not in ['h', 's', 'c']:
            game_type = menu_input(stdscr, 2, 3, "Select game type; (h)otseat, (s)erver, or (c)lient?")

        if game_type == "s":
            HOST = menu_input(stdscr, 2, 3, "Enter address (default 0.0.0.0): ")
            PORT = menu_input(stdscr, 2, 3, "Enter port to listen on (default %s): " % DEFAULT_PORT)
            HOST = "0.0.0.0" if HOST == "" else HOST
            PORT = DEFAULT_PORT if PORT == "" else PORT

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST,int(PORT)))
            s.listen()

            display_msg(stdscr, "Waiting for a client to connect...")

            conn,addr = s.accept()

            player_sides = [mlchess.Piece.WHITE]
            stdscr.clear()

        elif game_type == "c":
            HOST = menu_input(stdscr, 2, 3, "Enter server address: ")
            PORT = menu_input(stdscr, 2, 3, "Enter server port (default %s): " % DEFAULT_PORT)
            PORT = DEFAULT_PORT if PORT == "" else PORT

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST,int(PORT)))
            player_sides = [mlchess.Piece.BLACK]
            stdscr.clear()
        else:
            player_sides = [mlchess.Piece.BLACK, mlchess.Piece.WHITE]


        # Set up curses environment
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        stdscr.keypad(1)
        curses.mousemask(1)

        panel = curses.panel.new_panel(stdscr)
        game = mlchess.MultilevelChess(player_sides)

        dmsg = ""

        click_select = False

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
                        if select_pos == [x,y,z]:
                            color_P = 6

                        if game.old_select_pos == [x,y,z] and game.selected:
                            color_P = 12


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
                        stdscr.addstr(
                                pos_y,
                                pos_x,
                                text,
                                curses.color_pair(color_P))

                        # Optional: Draws a shadow below the boards for 3D effect.
                        if x == 0 or y in range(7-z,8):
                            stdscr.addstr(
                                pos_y + z + 1,
                                pos_x - 1,
                                "  " if y in range(7-z,8) else " ",
                                curses.color_pair(7))

            stdscr.addstr(0, 2, "Turn: " + ("W" if game.board.turn == mlchess.Piece.WHITE else "B"))
            w_king = "WK " + str((game.board.get_info(game.board.king[mlchess.Piece.WHITE])["state"].name).ljust(15))
            b_king = "BK " + str((game.board.get_info(game.board.king[mlchess.Piece.BLACK])["state"].name).ljust(15))
            stdscr.addstr(1, 2, w_king)
            stdscr.addstr(2, 2, b_king)

            if game.is_my_turn():
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
                elif c == curses.KEY_MOUSE:
                    try:
                        _, mx, my, _, _ = curses.getmouse()
                        board_x = ((mx - os_x) % 18) // 2
                        board_y = (my - os_y) + ((mx - os_x) // 18)
                        board_z = ((mx - os_x) // 18)
                        game.set_select_pos([board_x, board_y, board_z])
                        game.set_select(True)
                    except:
                        pass

            # Checks if the client is currently running as (s)erver or (c)lient and either waits for opponent move or
            # waits for a local move then sends the last local move to the opponenet then waits.
            stdscr.refresh()
            if game_type == "s":

                if not game.is_my_turn() and not game.turn_done:
                    try:
                        stdscr.addstr(0,18,"Waiting for opponent . . .")
                        stdscr.refresh()
                        data = conn.recv(6)
                    except socket.error as e:
                        err = e.args[0]
                        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                            display_msg(stdscr, "No data available")
                            sleep(2)
                            continue
                        else:
                            display_msg(stdscr, str(e))
                            sleep(2)
                            sys.exit(1)
                    else:
                        stdscr.addstr(0,18,"                           ")
                        stdscr.refresh()
                        game.opponent_move(data.decode())

                elif game.turn_done:
                    conn.sendall(game.my_move().encode())
                    game.turn_done = False

            elif game_type == "c":
                if not game.is_my_turn() and not game.turn_done:
                    try:
                        stdscr.addstr(0,18,"Waiting for opponent . . .")
                        stdscr.refresh()
                        data = s.recv(6)
                    except socket.error as e:
                        err = e.args[0]
                        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                            display_msg(stdscr, "No data available")
                            sleep(2)
                            continue
                        else:
                            display_msg(stdscr, str(e))
                            sleep(2)
                            sys.exit(1)
                    else:
                        stdscr.addstr(0,18,"                           ")
                        stdscr.refresh()
                        game.opponent_move(data.decode())

                elif game.turn_done:
                    s.sendall(game.my_move().encode())
                    game.turn_done = False

    finally:
        # Clean up and exit
        if game_type == "s":
            s.close()
            conn.close()
        elif game_type == "c":
            s.close()
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

if __name__ == '__main__':
    main()
