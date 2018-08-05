import argparse
import cv2
import imutils
from utils import steer_image

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input', default='input/pyimage_combo.png',
                help='path to input image')
ap.add_argument('-w', '--resizeWidth', type=int, default=900,
                help='pixel width to resize to before processing')
ap.add_argument('-t', '--thresholdParams', nargs=3, type=int,
                help='custom params for thresholding before contour detection')
args = vars(ap.parse_args())

image = cv2.imread(args['input'])
image = imutils.resize(image, width=args['resizeWidth'])
if args['thresholdParams']:
    steer_image(image, *tuple(args['thresholdParams']))
else:
    steer_image(image)

# use for sensor tower logo
# steer_image(image, 75, 255, 0)
