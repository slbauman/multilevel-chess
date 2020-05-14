#!/usr/bin/env python3

import curses, curses.panel
import mlchess

os_y = 3
os_x = 2

piece = {
        'utf8': ['♚','♛','♜','♞','♝','♟',''],
        'ascii': ['K','Q','R','N','B','P','']
        }

def main():
    try:
        stdscr = curses.initscr()

        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(2, 255, 249)
        curses.init_pair(3, 255, 130)
        curses.init_pair(4, 232, 249)
        curses.init_pair(5, 232, 130)

        curses.init_pair(6, 184, 232)

        curses.init_pair(7, 232, -1)
        curses.init_pair(8, 232, 232)

        curses.init_pair(9, 22, 249)
        curses.init_pair(10, 34, 130)
        curses.init_pair(11, 160, 232)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        stdscr.keypad(1)
        #rows, columns = stdscr.getmaxyx()

        panel = curses.panel.new_panel(stdscr)
        #panel.window().border()
        game = mlchess.MultilevelChess()

        stdscr.refresh()
        while 1:
            select_pos = game.get_select_pos()
            for z in range(3):
                for y in range(8):
                    for x in range(8):
                        board_data = game.get_board_at(x,y,z)
                        p_id = board_data[1]
                        color_P = ((x + y) % 2) + 2 + (board_data[0] * 2)
                        if select_pos == [x,y,z]: color_P = 6

                        if board_data[1] >= 0:
                            text = "{:2}".format(piece['utf8'][p_id] + " ")
                            if board_data[2] == 1:
                                color_P = 11
                        elif board_data[2] == 1:
                            text = "⬤ "
                            color_P += 7
                        else:
                            text = "  "

                        panel.window().addstr(
                                y+os_y-z,
                                (x*2)+os_x+(z*18),
                                text,
                                curses.color_pair(color_P))
                        #if x == 0 and y > 0:
                        #    panel.window().addstr(
                        #        y+os_y-z,
                        #        (x*2)+os_x+(z*18)-1,
                        #        " ", curses.color_pair(8))
                        #    if y == 7:
                        #        panel.window().addstr(
                        #            y+os_y-z + 1,
                        #            (x*2)+os_x+(z*18)-1,
                        #            "▀", curses.color_pair(7))
                        #elif y == 7:
                        #    panel.window().addstr(
                        #        y+os_y-z + 1,
                        #        (x*2)+os_x+(z*18)-2,
                        #        "▀▀", curses.color_pair(7))
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
            elif c == curses.KEY_RESIZE:
                y, x = stdscr.getmaxyx()
                curses.resizeterm(y, x)
                stdscr.refresh()
            #panel.window().addstr(12,2,
            #                      str(len(game.board.masks)),
            #                      curses.color_pair(6))

            curses.panel.update_panels(); #stdscr.refresh()
            #panel.window().addstr(0,0,str(c))
            #panel.window().addstr(11,2,game.debug_msg)

    finally:
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

if __name__ == '__main__':
    main()
