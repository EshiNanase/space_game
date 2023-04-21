import time
import asyncio
import curses
import random
import itertools
from tools import (
    draw_frame,
    read_controls,
    get_frame_size,
)

TIC = 0.1
OFFSET_TICS = 5
SYMBOLS = ['+', '*', '.', ':']
COROUTINES = []


def fetch_spaceship_frames():
    with open('animations/rocket_frame_1.txt') as file1:
        frame1 = file1.read()
    with open('animations/rocket_frame_2.txt') as file2:
        frame2 = file2.read()
    return [frame1, frame2]


async def blink(canvas, coord, symbol='*'):
    row, column = coord
    for _ in range(OFFSET_TICS):
        await asyncio.sleep(0)
    while True:
        for _ in range(20):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)
        for _ in range(3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)
        for _ in range(5):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)
        for _ in range(3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):

    row, column = start_row, start_column
    for _ in range(3):
        canvas.addstr(round(row), round(column), '*')
        await asyncio.sleep(0)
    for _ in range(3):
        canvas.addstr(round(row), round(column), 'O')
        await asyncio.sleep(0)
    for _ in range(2):
        canvas.addstr(round(row), round(column), ' ')
        await asyncio.sleep(0)

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


def gen_frame(frames):
    for i in itertools.cycle([0, 0, 1, 1]):
        yield frames[i]


def gen_random_coordinates(value):
    return random.randint(1, value - 1)


def gen_random_symbol():
    return random.choice(SYMBOLS)


def fetch_next_coords(current_row, current_column, delta_row, delta_column, max_coords, frame_size):
    frame_rows, frame_columns = frame_size
    max_row, max_column = max_coords
    next_row = min(max(1, current_row + delta_row), min(current_row + delta_row, max_row - frame_rows - 1))
    next_column = min(max(1, current_column + delta_column), min(current_column + delta_column, max_column - frame_columns - 1))
    return next_row, next_column


async def run_spaceship(canvas, row, column, frame):

    canvas_height, canvas_width = canvas.getmaxyx()

    while True:

        spaceship_frame = next(frame)

        frame_height, frame_width = get_frame_size(spaceship_frame)
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        row_number = min(
            row + rows_direction,
            canvas_height - frame_height - 1,
        )
        column_number = min(
            column + columns_direction,
            canvas_width - frame_width - 1,
        )

        row = max(row_number, 1)
        column = max(column_number, 1)
        if space_pressed:
            for _ in range(1, 4):
                COROUTINES.append(fire(canvas, row - 1, column + _))

        draw_frame(canvas, row, column, spaceship_frame)
        last_frame = spaceship_frame

        await asyncio.sleep(0)
        draw_frame(canvas, row, column, last_frame, negative=True)


def draw(canvas):
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    frames = fetch_spaceship_frames()
    frame = gen_frame(frames)
    canvas_height, canvas_width = canvas.getmaxyx()
    center_row_of_canvas, center_column_of_canvas = (
        canvas_height // 2, canvas_width // 2
    )

    y, x = canvas.getmaxyx()
    COROUTINES.extend([blink(canvas, coord=(gen_random_coordinates(y), gen_random_coordinates(x)), symbol=gen_random_symbol()) for _ in range(1, 450)])
    COROUTINES.append(run_spaceship(canvas, center_row_of_canvas, center_column_of_canvas, frame))

    while True:
        for coroutine in COROUTINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
