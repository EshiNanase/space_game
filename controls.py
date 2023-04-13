def read_controls(canvas):

    up = 259
    left = 260
    right = 261
    down = 258

    rows_direction = columns_direction = 0

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == up:
            rows_direction = -1

        if pressed_key_code == down:
            rows_direction = 1

        if pressed_key_code == right:
            columns_direction = 1

        if pressed_key_code == left:
            columns_direction = -1

    return rows_direction, columns_direction
