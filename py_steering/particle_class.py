import numpy as np
import cv2


class Particle:
    def __init__(self, location, target, radius=4, color=(255, 255, 255), max_speed=20):
        self.target = np.array(target)
        self.location = np.array(location, dtype='float64')
        self.speed = np.array([0, 0], dtype='float64')
        self.acceleration = np.array([0, 0], dtype='float64')
        self.max_speed = max_speed

        self.radius = radius
        self.color = color

    def update(self, canvas, mouse_loc):
        self.arrive_step(canvas)
        self.flee_step(canvas, mouse_loc)
        self.speed += self.acceleration
        self.location += self.speed

    def show(self, canvas):
        location = self.location.astype('int')
        cv2.circle(canvas, tuple(location), self.radius, self.color, -1)

    def arrive_step(self, canvas):
        np_dist = self.target - self.location
        speed = np.interp(np_dist, (-max(canvas.shape), max(canvas.shape)), (-self.max_speed, self.max_speed))
        self.speed = speed

    def flee_step(self, canvas, mouse_loc):
        np_dist = np.array(mouse_loc) - self.location
        eu_dist = np.linalg.norm(np_dist)
        if eu_dist <= 50:
            speed = np.interp(np_dist, (-max(canvas.shape), max(canvas.shape)), (-self.max_speed, self.max_speed))
            self.speed = -10 * speed
