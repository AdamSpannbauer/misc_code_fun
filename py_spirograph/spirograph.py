import random
import argparse
import cv2
from utils import draw_spirograph, str_2_bool

ap = argparse.ArgumentParser()
ap.add_argument('-o', '--output', type=str, default='spirograph_drawing.png',
                help='path to save output image to')
ap.add_argument('-n', '--nCircles', type=int, default=3,
                help='number of circles in spirograph')
ap.add_argument('-p', '--randomPos', type=str_2_bool, default='f',
                help='randomize whether circles are draw inside or outside of parent?')
args = vars(ap.parse_args())


# create random descending radii
radii = sorted([random.randrange(1, 101, 1) for _ in range(args['nCircles'])], key=lambda x: -x)

# create random ascending speeds
speeds = sorted([random.randrange(10, 101, 1) / 200 for _ in radii[1:]])
# force speeds to alternate direction
speeds = [s * (-1) ** i for i, s in enumerate(speeds)]

# create positioning list
if args['randomPos']:
    pos = [random.choice(['in', 'out']) for _ in radii[1:]]
else:
    pos = []

# derive canvas from max possible radii combination
max_dist = int(2 * (sum(r * 2 for r in radii[1:]) + radii[0])) + 1
drawing = draw_spirograph(radii, speeds, pos, canvas_size=(max_dist, max_dist))

# save output
cv2.imwrite('spirograph_drawing.png', drawing)
