import cv2
import numpy as np
from utils import image_to_particles


mouse_x = float('inf')
mouse_y = float('inf')


def get_mouse_xy(event, x, y, flags, param):
    global mouse_x
    global mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y


window_name = 'Particles'
image = cv2.imread('python_logo.png')
canvas = np.zeros(image.shape, dtype='uint8') + 50

particles = image_to_particles(image)

cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, get_mouse_xy)

while True:
    canvas_i = canvas.copy()
    for particle in particles:
        particle.update(canvas_i, (mouse_x, mouse_y))
        particle.show(canvas_i)

    cv2.imshow(window_name, canvas_i)
    key = cv2.waitKey(10)

    if key == 27 or key == ord('q'):
        break
