from curses_tools import draw_frame, get_frame_size
import asyncio
from obstacles import Obstacle
from explosion import explode


async def fly_garbage(canvas, column, garbage_frame, uid, obstacles,
                      obstacles_in_last_collisions, speed=0.5):
    """Animate garbage, flying from top to bottom.
       Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    rows_size, columns_size = get_frame_size(garbage_frame)

    obstacle = Obstacle(row, column, rows_size, columns_size, uid)
    obstacles.append(obstacle)

    while obstacle.row < rows_number:
        draw_frame(canvas, obstacle.row, obstacle.column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, obstacle.row, obstacle.column, garbage_frame,
                   negative=True)
        obstacle.row += speed
        if obstacle in obstacles_in_last_collisions:
            center_row = obstacle.row + obstacle.rows_size // 2
            center_column = obstacle.column + obstacle.columns_size // 2
            await explode(canvas, center_row, center_column)
            break
    try:
        obstacles.remove(obstacle)
        obstacles_in_last_collisions.remove(obstacle)
    finally:
        return
