import math
import argparse
import cv2
import numpy as np


def str_2_bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def gen_border_circle(parent_x, parent_y, parent_radius, r, angle, pos='out'):
    if pos == 'in':
        r = -1 * r

    rsum = parent_radius + r
    x2 = parent_x + round(rsum * math.cos(angle))
    y2 = parent_y + round(rsum * math.sin(angle))

    return x2, y2


def draw_spirograph(radii, speeds, pos=[],
                    canvas_size=(600, 600),
                    draw_color=(200, 125, 150),
                    circle_color=(150, 100, 200)):
    """Draw a spirograph animation

    The spirograph will be made up of bordering circles rotating at given angular speeds

    :param radii: a list of radii of to specify the size of each circle
    :param speeds: a list of angular velocities to be applied to each circle.
                   len(speeds) == len(radii) - 1;
                   the first circle corresponding to the first element of radii is stationary
    :param pos: a list where each element is in ['in', 'out'];
                circles will be drawn inside or outside of their parent based on their pos specified in this list.
                len(pos) == len(radii) - 1;
                the first circle corresponding to the first element of radii is drawn around the center
                point of the canvas
    :param canvas_size: the size of the canvas to draw on
    :param draw_color: which color should be used to draw the spirograph output
    :param circle_color: which color should the circles be in the animation
    :return: the resulting spirograph image without the circles in the animation
    """
    canvas = np.zeros(canvas_size + (3,), dtype='uint8') + 50
    cx = canvas_size[1] // 2
    cy = canvas_size[0] // 2
    parent_x = parent_y = parent_radius = 0  # initialized to please pycharm code checker

    angles = [0 for _ in radii]
    if not pos:
        pos = ['out' for _ in radii]

    prev_x = prev_y = None
    while True:
        canvas_i = canvas.copy()
        for i, radius in enumerate(radii):
            if i == 0:
                x = cx
                y = cy
            else:
                x, y = gen_border_circle(parent_x, parent_y, parent_radius, radius, angle=angles[i], pos=pos[i - 1])
                angles[i] += speeds[i - 1]

            cv2.circle(canvas_i, (x, y), radius, circle_color, thickness=1)

            if i == len(radii) - 1:
                canvas[y, x] = draw_color
                if prev_x is not None and prev_y is not None:
                    cv2.line(canvas, (prev_x, prev_y), (x, y), draw_color, 1)
                prev_x = x
                prev_y = y

            parent_radius = radius
            parent_x = x
            parent_y = y

        cv2.imshow('Spirograph Progress (press ESC or Q to quit)', canvas_i)
        key = cv2.waitKey(10)

        if key == ord('q') or key == 27:
            break

    return canvas
