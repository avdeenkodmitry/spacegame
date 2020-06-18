import math


def _limit(value, min_value, max_value):
    """Limit value by min_value and max_value.

    Args:
        value (double): received value
        min_value (double): minimum value, that we return if value < min_value
        max_value (double): minimum value, that we return if value < min_value

    Returns:
        double: return limit value
    """

    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def _apply_acceleration(speed, speed_limit, forward=True):
    """Change speed — accelerate or brake — according to force direction.

    Args:
        speed (double): current speed of the spaceship
        speed_limit (double): max speed of the spaceship
        forward (bool): increase or decrease speed flag

    Returns:

    """

    speed_limit = abs(speed_limit)

    speed_fraction = speed / speed_limit

    # если корабль стоит на месте, дергаем резко
    # если корабль уже летит быстро, прибавляем медленно
    delta = math.cos(speed_fraction) * 0.75

    if forward:
        result_speed = speed + delta
    else:
        result_speed = speed - delta

    result_speed = _limit(result_speed, -speed_limit, speed_limit)

    # если скорость близка к нулю, то останавливаем корабль
    if abs(result_speed) < 0.1:
        result_speed = 0

    return result_speed


def update_speed(row_speed, column_speed, rows_direction, columns_direction,
                 row_speed_limit=2, column_speed_limit=2, fading=0.8):
    """Update speed smootly to make control handy for player.

    rows_direction — is a force direction by rows axis. Possible values:
       -1 — if force pulls up
       0  — if force has no effect
       1  — if force pulls down
    columns_direction — is a force direction by colums axis. Possible values:
       -1 — if force pulls left
       0  — if force has no effect
       1  — if force pulls right

    Args:
        row_speed (double): number of rows a sh flies over a time period
        column_speed (double): number of columns a sh flies over a time period
        rows_direction (double): direction of horizontal move
        columns_direction (double): direction of vertical move
        row_speed_limit (double): limit of rows sh flies over a time period
        column_speed_limit (double): limit of cols sh flies over a time period
        fading (double): coefficient to stop the spaceship

    Returns:
        list: [(int), (int)] list of row and column speed
    """
    if rows_direction not in (-1, 0, 1):
        raise ValueError(f'Wrong rows_direction value {rows_direction}.'
                         f' Expects -1, 0 or 1.')

    if columns_direction not in (-1, 0, 1):
        raise ValueError(f'Wrong columns_direction value {columns_direction}.'
                         f' Expects -1, 0 or 1.')

    if fading < 0 or fading > 1:
        raise ValueError(f'Wrong columns_direction value {fading}.'
                         f' Expects float between 0 and 1.')

    row_speed *= fading
    column_speed *= fading

    row_speed_limit, column_speed_limit = abs(row_speed_limit), abs(
        column_speed_limit)

    if rows_direction != 0:
        row_speed = _apply_acceleration(row_speed, row_speed_limit,
                                        rows_direction > 0)

    if columns_direction != 0:
        column_speed = _apply_acceleration(column_speed, column_speed_limit,
                                           columns_direction > 0)

    return row_speed, column_speed
