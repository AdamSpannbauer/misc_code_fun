import argparse
import cv2
from utils import steer_image

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input',
                # default='python_logo.png',
                default='opencv_logo.png',
                help='path to input image')
args = vars(ap.parse_args())

image = cv2.imread(args['input'])
steer_image(image)
