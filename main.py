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
from physics import update_speed
from obstacles import Obstacle, show_obstacles
from explosion import explode
from game_scenario import PHRASES, get_garbage_delay_tics
import os

DEBUG = False

row_speed, column_speed = (0, 0)
game_over_phrase = ''
year = 1957
coroutines = []
obstacles = []
obstacles_in_last_collision = []

TIC = 0.1
BORDER_OFFSET = 1
OFFSET_TICS = 5
SYMBOLS = ['+', '*', '.', ':']


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def show_game_over(canvas):
    canvas_height, canvas_width = canvas.getmaxyx()
    center_row, center_column = (canvas_height // 4, (canvas_width // 4) - 20)
    while True:
        draw_frame(canvas, center_row, center_column, game_over_phrase)
        await asyncio.sleep(0)


def fetch_game_over_phrase():
    with open('game_over.txt') as file1:
        frame1 = file1.read()
    return frame1


def fetch_spaceship_frames():
    with open('spaceship_frames/rocket_frame_1.txt') as file1:
        frame1 = file1.read()
    with open('spaceship_frames/rocket_frame_2.txt') as file2:
        frame2 = file2.read()
    return [frame1, frame2]


def fetch_garbage_frames():
    filenames = []
    frames = []
    for (dirpath, dirnames, filenames) in os.walk('garbage_frames'):
        filenames.extend(filenames)
        break
    for filename in filenames:
        with open(f'garbage_frames/{filename}') as file:
            frames.append(file.read())
    return frames


async def blink(canvas, coord, symbol='*'):
    row, column = coord

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(1)

        canvas.addstr(row, column, symbol)
        await sleep(1)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(1)

        canvas.addstr(row, column, symbol)
        await sleep(1)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await sleep(3)

    canvas.addstr(round(row), round(column), 'O')
    await sleep(3)

    canvas.addstr(round(row), round(column), ' ')
    await sleep(3)

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - BORDER_OFFSET, columns - BORDER_OFFSET

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed

        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collision.append(obstacle)
                return


def gen_frame(frames):
    for i in itertools.cycle([0, 0, 1, 1]):
        yield frames[i]


def gen_random_coordinates(value):
    return random.randint(1, value - BORDER_OFFSET)


def gen_random_symbol():
    return random.choice(SYMBOLS)


def gen_random_garbage_frame(garbage_frames):
    return random.choice(garbage_frames)


def fetch_next_coords(current_row, current_column, delta_row, delta_column, max_coords, frame_size):
    frame_rows, frame_columns = frame_size
    max_row, max_column = max_coords
    next_row = min(max(1, current_row + delta_row), min(current_row + delta_row, max_row - frame_rows - BORDER_OFFSET))
    next_column = min(max(1, current_column + delta_column), min(current_column + delta_column, max_column - frame_columns - BORDER_OFFSET))
    return next_row, next_column


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - BORDER_OFFSET)

    row = 0

    frame_height, frame_width = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, frame_height, frame_width)
    obstacles.append(obstacle)

    while row < rows_number:

        if obstacle in obstacles_in_last_collision:
            obstacles.remove(obstacle)
            obstacles_in_last_collision.remove(obstacle)
            await explode(canvas, row, column)
            return

        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row += speed
    obstacles.remove(obstacle)


async def count_years():
    global year

    while True:
        year += 1
        await sleep(2)


async def display_info_about_the_current_year(canvas):
    global year

    while True:
        try:
            draw_frame(canvas, 0, 0, f'Year - {year}: {PHRASES[year]}')
        except KeyError:
            try:
                draw_frame(canvas, 0, 0, f'Year - {year - 1}: {PHRASES[year - 1]}', negative=True)
            except KeyError:
                pass
            draw_frame(canvas, 0, 0, f'Year - {year}')
        await asyncio.sleep(0)


async def fill_orbit_with_garbage(canvas, garbage_frames):
    global year

    canvas_height, canvas_width = canvas.getmaxyx()
    while True:
        garbage_delay = get_garbage_delay_tics(year)
        await asyncio.sleep(0)
        if not garbage_delay:
            continue

        random_frame = gen_random_garbage_frame(garbage_frames)
        _, frame_width = get_frame_size(random_frame)
        random_column = random.randint(1, canvas_width - frame_width - BORDER_OFFSET)
        coroutines.append(fly_garbage(canvas, random_column, random_frame))

        await sleep(garbage_delay)


async def run_spaceship(canvas, row, column, frame):

    global row_speed, column_speed, year

    canvas_height, canvas_width = canvas.getmaxyx()

    while True:

        spaceship_frame = next(frame)

        frame_height, frame_width = get_frame_size(spaceship_frame)
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)

        row_number = min(
            row + row_speed,
            canvas_height - frame_height - BORDER_OFFSET,
        )
        column_number = min(
            column + column_speed,
            canvas_width - frame_width - BORDER_OFFSET,
        )

        row = max(row_number, 1)
        column = max(column_number, 1)
        if space_pressed and year >= 2020:
            coroutines.append(fire(canvas, row, column))

        draw_frame(canvas, row, column, spaceship_frame)
        last_frame = spaceship_frame

        await asyncio.sleep(0)
        draw_frame(canvas, row, column, last_frame, negative=True)

        for obstacle in obstacles:
            if obstacle.has_collision(row, column, frame_height, frame_width):
                obstacles_in_last_collision.append(obstacle)
                await show_game_over(canvas)
                return


def draw(canvas):
    global game_over_phrase
    game_over_phrase = fetch_game_over_phrase()

    canvas.nodelay(True)
    curses.curs_set(False)
    frames = fetch_spaceship_frames()
    garbage_frames = fetch_garbage_frames()
    frame = gen_frame(frames)
    canvas_height, canvas_width = canvas.getmaxyx()
    center_row_of_canvas, center_column_of_canvas = (
        canvas_height // 2, canvas_width // 2
    )

    y, x = canvas.getmaxyx()
    coroutines.extend([blink(canvas, coord=(gen_random_coordinates(y), gen_random_coordinates(x)), symbol=gen_random_symbol()) for _ in range(1, 450)])
    coroutines.append(run_spaceship(canvas, center_row_of_canvas, center_column_of_canvas, frame))
    coroutines.append(fill_orbit_with_garbage(canvas, garbage_frames))
    coroutines.append(count_years())
    coroutines.append(display_info_about_the_current_year(canvas))

    if DEBUG:
        coroutines.append(show_obstacles(canvas, obstacles))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
