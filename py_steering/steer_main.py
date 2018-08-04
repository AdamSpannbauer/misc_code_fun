import argparse
import cv2
import imutils
from utils import steer_image

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input', default='pyimage_combo.png',
                help='path to input image')
ap.add_argument('-w', '--resizeWidth', default=900,
                help='pixel width to resize to before processing')
args = vars(ap.parse_args())

image = cv2.imread(args['input'])
image = imutils.resize(image, width=args['resizeWidth'])
steer_image(image)
