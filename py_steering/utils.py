import cv2
import numpy as np
from particle_class import Particle


def image_to_particles(image, every_n=20, radius=4, color=(255, 255, 255)):
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

    return tuple(int(x) for x in image[cy, cx])


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
