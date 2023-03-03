import random
import time
import curses
import asyncio


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    y, x = curses.window.getmaxyx(canvas)
    symbols = ['+', '*', '.', ':']

    coroutines = [blink(canvas, row=random.randint(5, y-5), column=random.randint(5, x-5), symbol=random.choice(symbols)) for index in range(5)]
    bullet = fire(canvas, 0, 0)

    for coroutine in coroutines:
        coroutine.send(None)
        canvas.refresh()

    while True:
        for coroutine in coroutines.copy():
            coroutine.send(None)
            canvas.refresh()
        time.sleep(2)

        for coroutine in coroutines.copy():
            coroutine.send(None)
            canvas.refresh()
        time.sleep(0.3)

        for coroutine in coroutines.copy():
            coroutine.send(None)
            canvas.refresh()
        time.sleep(0.5)

        for coroutine in coroutines.copy():
            coroutine.send(None)
            canvas.refresh()
        time.sleep(0.3)


async def blink(canvas, row, column, symbol='*'):

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        time.sleep(random.uniform(0.1, 0.5))
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        time.sleep(random.uniform(0.1, 0.5))
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        time.sleep(random.uniform(0.1, 0.5))
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        time.sleep(random.uniform(0.1, 0.5))
        await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):

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
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
