#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Just another 2048 ncurses game."""

import time
import random
import curses
from curses import ascii
from curses.textpad import rectangle


def transposed(matrix):
    """Transpose a matrix."""
    return [
        list(row) for row in zip(*matrix)
    ]

def y_mirrored(matrix):
    """Mirror a matrix on y-axis."""
    return [
        row[::-1] for row in matrix
    ]


def curses_draw_table(screen, y_pos, x_pos, height, width, cell_height, cell_width):
    """Draw a table to the screen."""
    screen.addstr(
        y_pos, x_pos,
        '┌%s┐' % ('┬').join(['─' * (cell_width-2)]*width),
    )
    screen.addstr(
        y_pos + height * (cell_height-1), x_pos,
        '└%s┘' % ('┴').join(['─' * (cell_width-2)]*width),
    )
    for x in range(width+1):
        for sy in range(1, cell_height-1):
            screen.addstr(
                y_pos + sy, x_pos + x*(cell_width-1),
                '│',
            )

    for y in range(1, height):
        screen.addstr(
            y_pos + y*(cell_height-1), x_pos,
            '├%s┤' % ('┼').join(['─' * (cell_width-2)]*width),
        )
        for x in range(width+1):
            for sy in range(1, cell_height-1):
                screen.addstr(
                    y_pos + y*(cell_height-1) + sy, x_pos + x*(cell_width-1),
                    '│',
                )


class Game(object):
    """A 2048 game"""

    SIZE = 4
    MAX = 16276
    SCR_FIELD_SIZE = len(str(MAX)) + 2
    COLORS = {
        0: curses.COLOR_WHITE,
        2: curses.COLOR_WHITE,
        4: curses.COLOR_CYAN,
        8: curses.COLOR_CYAN,
        16: curses.COLOR_MAGENTA,
        32: curses.COLOR_MAGENTA,
        64: curses.COLOR_YELLOW,
        128: curses.COLOR_YELLOW,
        256: curses.COLOR_GREEN,
        512: curses.COLOR_GREEN,
        1024: curses.COLOR_RED,
        2048: curses.COLOR_RED,
        4096: curses.COLOR_BLACK,
        8192: curses.COLOR_BLACK,
    }

    def __init__(self):
        self.area = list((
            list((
                0 for _ in range(Game.SIZE)
            )) for _ in range(Game.SIZE)
        ))  # the game numbers are stored here
        self.moves = 0
        self.scr = curses.initscr()
        curses.start_color()
        self.area_pad = curses.newpad(
            1 + 2 * Game.SIZE,
            1 + (Game.SCR_FIELD_SIZE+1) * Game.SIZE + 1,  # +1 bug??
        )
        curses_draw_table(
            self.area_pad, 0, 0,
            Game.SIZE, Game.SIZE,
            3, Game.SCR_FIELD_SIZE + 2,
        )

    def start(self):
        """Start a Game"""
        self.place_number()
        self.place_number()
        self.render()

        while True:
            c = self.scr.getch()
            if c in [ord('q'), ascii.ESC]:
                self.quit()
            elif c in [ord('h'), curses.KEY_LEFT]:
                self.move('left')
            elif c in [ord('j'), curses.KEY_DOWN]:
                self.move('down')
            elif c in [ord('k'), curses.KEY_UP]:
                self.move('up')
            elif c in [ord('l'), curses.KEY_RIGHT]:
                self.move('right')

    def render(self):
        self.scr.addstr(
            0, 0, "Just another 2048 game".center(self.scr.getmaxyx()[1]),
            curses.A_BOLD+curses.A_UNDERLINE
        )
        self.scr.addstr(
            1, 0, "Moves: %i" % self.moves, curses.A_BOLD
        )
        for y, row in enumerate(self.area):
            for x, v in enumerate(row):
                self.area_pad.addstr(
                    1 + 2 * y, 1 + (Game.SCR_FIELD_SIZE+1) * x,
                    str(v if v else '').center(Game.SCR_FIELD_SIZE-2),
                    Game.COLORS[v]
                )

        self.area_pad.refresh(
            0, 0,  # upper left corner of pad area
            5+int((self.scr.getmaxyx()[0]-5-self.area_pad.getmaxyx()[0])/2),  # y
            int((self.scr.getmaxyx()[1]-self.area_pad.getmaxyx()[1])/2),  # x
            self.scr.getmaxyx()[0]-1, self.scr.getmaxyx()[1]-1  # lower right corner of window
        )
        self.scr.refresh()

    def place_number(self):
        """Place a random number on a random free field."""
        number = random.choice([2] * 9 + [4])
        while True:
            pos_y = random.randint(0, Game.SIZE - 1)
            pos_x = random.randint(0, Game.SIZE - 1)
            if not self.area[pos_y][pos_x]:
                self.area[pos_y][pos_x] = number
                return

    def is_lost(self):
        """Return True if the game is lost."""
        for area in (self.area, transposed(self.area)):
            for row in area:
                old_v = -1
                for v in row:
                    if v == 0 or v == old_v:
                        return False  # there is a chance

        return True  # lost

    @staticmethod
    def _move_left(area):
        """Do a left move."""
        for row in area:
            ptr = -1
            for i, v in enumerate(row):
                if not v:
                    continue

                if ptr >= 0 and row[ptr] == v:
                    # merge
                    row[ptr] += v
                    row[i] = 0
                else:
                    # move
                    ptr += 1
                    row[i] = 0
                    row[ptr] = v

    @staticmethod
    def _transform(area, direction):
        """Transform to make a simple left move."""
        if direction == 'left':
            return area
        elif direction == 'right':
            return y_mirrored(area)
        elif direction == 'up':
            return transposed(area)
        elif direction == 'down':
            return transposed(y_mirrored(area))

    def move(self, direction):
        """Make a move in direction."""
        self.moves += 1

        area = Game._transform(self.area, direction)
        Game._move_left(area)
        self.area = Game._transform(area, direction)

        if not self.is_lost():
            self.place_number()
            self.render()

        if self.is_lost():
            time.sleep(1)
            curses.endwin()
            print("You Lost!!!")
            self.quit()

    def quit(self):
        """Quit the Game."""
        exit(0)


def main(_):
    GAME = Game()
    GAME.start()

if __name__ == '__main__':
    curses.wrapper(main)
