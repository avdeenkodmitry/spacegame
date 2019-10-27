import time
import random
import curses
import asyncio
import curses_tools as ctools


async def animate_spaceship(canvas, row, column, frames):
    max_row, max_column = canvas.getmaxyx()
    frame_rows, frame_columns = ctools.get_frame_size(frames[0])
    while True:
        row_d, column_d, _ = ctools.read_controls(canvas)
        row = min(max(row + row_d, 0), max_row - frame_rows)
        column = min(max(column + column_d, 0), max_column - frame_columns)
        for frame in frames:
            ctools.draw_frame(canvas, row, column, frame)
            for _ in range(1):
                await asyncio.sleep(0)
            ctools.draw_frame(canvas, row, column, frame, True)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(random.randint(0, 2) * 10):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3,
               columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

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
    max_row, max_column = rows, columns

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def get_text(file_name):
    with open('resources/{}'.format(file_name), 'r') as file_frame:
        frame = file_frame.read()
        return frame


def draw(canvas):
    screen = curses.initscr()
    screen.nodelay(True)
    max_row, max_column = screen.getmaxyx()
    frames = [get_text('rocket_frame_1.txt'),
              get_text('rocket_frame_2.txt'), ]

    curses.curs_set(False)
    coroutines = []
    for i in range(200):
        row = random.randint(0, max_row - 1)
        column = random.randint(0, max_column - 1)
        coroutine = blink(canvas,
                          row,
                          column,
                          symbol=ctools.SYMS[random.randint(0, 3)])
        coroutines.append(coroutine)
    coroutine_spaceship = animate_spaceship(canvas,
                                            max_row // 2,
                                            max_column // 2,
                                            frames)
    coroutine_fire = fire(canvas, max_row // 2, max_column // 2)
    coroutines.extend([coroutine_spaceship, coroutine_fire])
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(ctools.TIC_TIMEOUT)
        if len(coroutines) == 0:
            break


if __name__ == '__main__':
    while True:
        curses.update_lines_cols()
        curses.wrapper(draw)
