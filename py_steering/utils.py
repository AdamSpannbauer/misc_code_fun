import cv2
import numpy as np
from particle_class import Particle


def image_to_particles(image, every_n=20, radius=4):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, threshed = cv2.threshold(gray, 3, 255, 0)

    _, contours, _ = cv2.findContours(threshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contour_colors = [get_contour_color(c, image) for c in contours]
    contour_points = [down_sample_points(c, every_n) for c in contours]

    particles = create_particles(contour_points, contour_colors, image, rand_location=True, radius=radius)

    return particles


def down_sample_points(contour, every_n=20):
    return contour[::every_n]


def get_contour_color(contour, image):
    moments = cv2.moments(contour)
    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])

    color = image[cy, cx]
    color = tuple(int(x) for x in color)

    if color == (0, 0, 0):
        mask = np.zeros(image.shape[:2], dtype='uint8')
        cv2.drawContours(mask, [contour], -1, 255, -1)

        masked = cv2.bitwise_and(image, image, mask=mask)
        non_zero = np.where(masked != 0)
        color_pool = masked[non_zero[0], non_zero[1], :]
        color = color_pool[np.random.randint(0, color_pool.shape[0])]
        color = tuple(int(x) for x in color)

    return color


def create_particles(contour_points, contour_colors, canvas, rand_location=True, radius=4):
    particles = []
    for i, points in enumerate(contour_points):
        color = contour_colors[i]
        for point in points:
            location = target = tuple(point.flatten())
            if rand_location:
                location = tuple(np.random.randint(1, canvas.shape[0], 1)) + \
                           tuple(np.random.randint(1, canvas.shape[1], 1))
            particle = Particle(location, target, radius, color)
            particles.append(particle)

    return particles


mouse_x = float('inf')
mouse_y = float('inf')


def get_mouse_xy(event, x, y, flags, param):
    global mouse_x
    global mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y


def steer_image(image, window_name = 'Particles (press ESC or Q to quit)'):
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
