import random
import time
import curses
import asyncio
from itertools import cycle
from functools import partial
from controls import read_controls


def draw(canvas, rocket_frame_1, rocket_frame_2):

    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    y, x = canvas.getmaxyx()

    symbols = ['+', '*', '.', ':']
    frames = cycle(
            [
                animate_spaceship(canvas, start_row=15, start_column=60, text=rocket_frame_1),
                animate_spaceship(canvas, start_row=15, start_column=60, text=rocket_frame_1, negative=True),
                animate_spaceship(canvas, start_row=15, start_column=60, text=rocket_frame_2),
                animate_spaceship(canvas, start_row=15, start_column=60, text=rocket_frame_2, negative=True),
            ]
    )
    blinks = cycle([blink(canvas, row=random.randint(5, y-1), column=random.randint(5, x-1), symbol=random.choice(symbols)) for index in range(100)])

    while True:
        next(blinks).send(None)
        canvas.refresh()
        next(blinks).send(None)
        canvas.refresh()
        next(frames).send(None)
        canvas.refresh()


async def animate_spaceship(canvas, start_row, start_column, text, negative=False):

    while True:

        time.sleep(0.00001)

        rows_number, columns_number = canvas.getmaxyx()
        rows_direction, columns_direction = read_controls(canvas)

        for row, line in enumerate(text.splitlines(), round(start_row)):
            if row < 0:
                continue

            if row >= rows_number:
                break

            for column, symbol in enumerate(line, round(start_column)):
                if column < 0:
                    continue

                if column >= columns_number:
                    break

                if symbol == ' ':
                    continue

                if row == rows_number - 1 and column == columns_number - 1:
                    continue

                symbol = symbol if not negative else ' '
                canvas.addch(row + rows_direction, column + columns_direction, symbol)

        start_row += rows_direction
        start_column += columns_direction
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):

    while True:
        time.sleep(0.00001)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        time.sleep(0.00001)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        time.sleep(0.00001)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        time.sleep(0.00001)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=0.3, columns_speed=0):

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def main() -> None:

    with open('animations/rocket_frame_1.txt', 'r') as file:
        rocket_frame_1 = file.read()
    with open('animations/rocket_frame_2.txt', 'r') as file:
        rocket_frame_2 = file.read()

    draw_art = partial(draw, rocket_frame_1=rocket_frame_1, rocket_frame_2=rocket_frame_2)

    curses.update_lines_cols()
    curses.wrapper(draw_art)


if __name__ == '__main__':
    main()
