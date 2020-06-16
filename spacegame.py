import time
import random
import curses
import asyncio
import curses_tools as ctools
import space_garbage as sg
from physics import update_speed
from itertools import cycle
from game_scenario import get_garbage_delay_tics, PHRASES


spaceship_frame = ""
coroutines = []
obstacles = []
obstacles_in_last_collisions = []
year = 1957
event_loop = asyncio.get_event_loop()


def get_text(file_name):
    with open(file_name, 'r') as file_frame:
        frame = file_frame.read()
        return frame


def get_all_garbage():
    garbage_names = ['duck.txt', 'hubble.txt', 'lamp.txt', 'trash_large.txt',
                     'trash_small.txt', 'trash_xl.txt']
    garbage_frames = []
    for name in garbage_names:
        garbage_frames.append(get_text('resources/{}'.format(name)))
    return garbage_frames


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def refresh_frame(canvas):
    while True:
        canvas.refresh()
        time.sleep(ctools.TIC_TIMEOUT)
        await sleep(1)


async def increase_year():
    global year
    while True:
        await sleep(10)
        year += 1


async def fill_orbit_with_garbage(canvas):
    screen = curses.initscr()
    _, max_column = screen.getmaxyx()
    garbage_frames = get_all_garbage()
    uid = 0
    while True:
        column = random.randint(0, max_column - 1)
        frame = garbage_frames[random.randint(0, len(garbage_frames)-1)]
        event_loop.create_task(sg.fly_garbage(canvas,
                                              column,
                                              frame,
                                              uid,
                                              obstacles,
                                              obstacles_in_last_collisions))
        uid += 1
        await sleep(get_garbage_delay_tics(year))


async def show_gameover(canvas):
    label_frame = get_text('resources/gameover.txt')
    max_row, max_column = canvas.getmaxyx()
    frame_rows, frame_columns = ctools.get_frame_size(label_frame)
    label_row = (max_row - frame_rows) // 2
    label_column = (max_column - frame_columns) // 2
    while True:
        ctools.draw_frame(canvas, label_row, label_column, label_frame)
        await sleep(1)


async def show_stats():
    global year
    screen = curses.initscr()
    max_row, max_column = screen.getmaxyx()
    while True:
        label = 'Year: {}'.format(str(year))
        if year in PHRASES:
            label = '{} {}'.format(label, PHRASES[year])
        stat_screen = screen.derwin(2,
                                    len(label) + 2,
                                    max_row - 2,
                                    max_column // 2)
        ctools.draw_frame(stat_screen, 1, 1, label)
        await sleep(1)
        ctools.draw_frame(stat_screen, 1, 1, label, True)


async def run_spaceship(canvas, row, column):
    global spaceship_frame, year
    row_speed = column_speed = 0
    max_row, max_column = canvas.getmaxyx()
    frame_rows, frame_columns = ctools.get_frame_size(spaceship_frame)
    while True:
        row_d, column_d, space_pressed = ctools.read_controls(canvas)
        row_speed, column_speed = update_speed(row_speed,
                                               column_speed,
                                               row_d,
                                               column_d)

        row = min(max(row + row_speed, 0), max_row - frame_rows)
        column = min(max(column + column_speed, 0), max_column - frame_columns)
        sh_frame = spaceship_frame
        ctools.draw_frame(canvas, row, column, sh_frame)
        await sleep(1)
        ctools.draw_frame(canvas, row, column, sh_frame, True)
        if space_pressed and year > 2020:
            event_loop.create_task(fire(canvas,
                                        row - 1,
                                        column + frame_columns // 2))

        for obstacle in obstacles:
            if obstacle.has_collision(row, column, frame_rows, frame_columns):
                await show_gameover(canvas)
                return


async def animate_spaceship(frames):
    global spaceship_frame
    for frame in cycle(frames):
        spaceship_frame = frame
        await sleep(1)


async def blink(canvas, row, column, offset_tics, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(offset_tics)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


async def fire(canvas, start_row, start_column, rows_speed=-1,
               columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await sleep(1)

    canvas.addstr(round(row), round(column), 'O')
    await sleep(1)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows, columns

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await sleep(1)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return


def draw(canvas):
    screen = curses.initscr()
    screen.nodelay(True)
    max_row, max_column = screen.getmaxyx()
    spaceship_frames = [get_text('resources/rocket_frame_1.txt'),
                        get_text('resources/rocket_frame_2.txt'), ]
    curses.curs_set(False)

    for i in range(200):
        row = random.randint(0, max_row - 1)
        column = random.randint(0, max_column - 1)
        coroutine = blink(canvas,
                          row,
                          column,
                          offset_tics=random.randint(0, 2) * 10,
                          symbol=ctools.SYMS[random.randint(0, 3)])
        coroutines.append(coroutine)
    coroutine_run_spaceship = run_spaceship(canvas,
                                            max_row // 2,
                                            max_column // 2,)
    coroutine_animate_spaceship = animate_spaceship(spaceship_frames)

    coroutine_fill_garbage = fill_orbit_with_garbage(canvas)
    coroutine_refresh = refresh_frame(canvas)
    coroutine_show_stats = show_stats()
    coroutine_increase_year = increase_year()
    coroutines.extend([coroutine_animate_spaceship,
                       coroutine_run_spaceship,
                       coroutine_fill_garbage,
                       coroutine_refresh,
                       coroutine_show_stats,
                       coroutine_increase_year])
    for coroutine in coroutines:
        event_loop.create_task(coroutine)
    event_loop.run_forever()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
