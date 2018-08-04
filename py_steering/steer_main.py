import argparse
import cv2
import imutils
from utils import steer_image

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input', default='input/st_logo_poster.png',
                help='path to input image')
ap.add_argument('-w', '--resizeWidth', type=int, default=500,
                help='pixel width to resize to before processing')
args = vars(ap.parse_args())

image = cv2.imread(args['input'])
image = imutils.resize(image, width=args['resizeWidth'])
steer_image(image)

# use for sensor tower logo
# steer_image(image, 75, 255, cv2.THRESH_BINARY)
