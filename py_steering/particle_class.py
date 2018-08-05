import numpy as np
import cv2


class Particle:
    def __init__(self, location, target, radius=4, color=(255, 255, 255), max_speed=75):
        self.target = np.array(target)
        self.location = np.array(location, dtype='float64')
        self.speed = np.array([0, 0], dtype='float64')
        self.acceleration = np.array([0, 0], dtype='float64')
        self.max_speed = max_speed

        self.radius = radius
        self.og_color = color
        self.color = color

        self.game_target = np.array(target)
        self.is_hit = False

    def update(self, canvas, mouse_loc, target=None):
        self.arrive_step(canvas, target=target)
        self.flee_step(canvas, mouse_loc)
        self.speed += self.acceleration
        self.location += self.speed

    def show(self, canvas):
        location = self.location.astype('int')
        cv2.circle(canvas, tuple(location), self.radius, self.color, -1)

    def arrive_step(self, canvas, target=None):
        if target is None:
            target = self.target

        xy_diff = target - self.location
        speed = np.interp(xy_diff, (-max(canvas.shape), max(canvas.shape) + 1), (-self.max_speed, self.max_speed))
        self.speed = speed

    def flee_step(self, canvas, mouse_loc):
        if mouse_loc:
            xy_diff = np.array(mouse_loc) - self.location
            dist = np.linalg.norm(xy_diff)
            if dist <= 50:
                speed = np.interp(xy_diff, (-max(canvas.shape), max(canvas.shape) + 1), (-self.max_speed, self.max_speed))
                self.speed = -10 * speed

    def check_hit(self, mouse_loc, mouse_range=50):
        xy_diff = np.array(mouse_loc) - self.location
        dist = np.linalg.norm(xy_diff)

        if dist <= mouse_range or self.color == (50, 50, 50):
            self.is_hit = True
            self.game_target = self.target
            self.color = self.og_color
