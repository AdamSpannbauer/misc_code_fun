import cv2
import numpy as np


class Moth:
    def __init__(self, course_dims, target_location, obstacles=[], lifespan=300, size=3):
        self.course_dims = course_dims
        self.lifespan = lifespan
        self.size = size
        self.start_location = np.array([self.course_dims[0] / 2, int(self.course_dims[1] * 0.9)], dtype='int')
        self.location = self.start_location.copy()
        self.velocity = np.array([0, -1], dtype='int')
        self.flight_path = self._random_flight_path()
        self.step = 0
        self.fitness = 0.5
        self.target_location = target_location
        self.obstacles = obstacles
        self.color = (150, 150, 150)
        self.succeeded = 0
        self.success_speed = lifespan

    def reset(self):
        self.location = self.start_location.copy()
        self.step = 0
        self.fitness = 0.5

    def _random_flight_path(self):
        velocities = []
        for _ in range(self.lifespan):
            vx = np.random.randint(-5, 6)
            vy = np.random.randint(-5, 6)
            velocities.append(np.array([vx, vy], dtype='int'))
        return velocities

    def _is_offscreen(self):
        return (self.location[0] < 0 or self.location[1] < 0 or
                self.location[0] > self.course_dims[0] or
                self.location[1] > self.course_dims[1])

    def _hit_obstacle(self):
        hit_obstacle = False
        if self.obstacles:
            for obstacle in self.obstacles:
                hit_obstacle = (obstacle[0][0] <= self.location[0] <= obstacle[1][0] and
                                obstacle[0][1] <= self.location[1] <= obstacle[1][1])
                if hit_obstacle:
                    break

        return hit_obstacle

    def update(self):
        if not self._is_offscreen() and not self._hit_obstacle():
            if self._e_dist(self.location, self.target_location) <= 19:
                self.location = self.target_location
                self.color = (17, 102, 1)
                self.succeeded = 1
                self.success_speed = self.step
            else:
                self.velocity = self.flight_path[self.step]
                self.location += self.velocity
        self.step += 1

    def show(self, course, victory_lap=False):
        if victory_lap:
            color = (int(x) for x in np.random.randint(0, 266, 3))
        else:
            color = self.color
        wing_l = (self.location[0] - 3, self.location[1] - 2)
        wind_r = (self.location[0] + 3, self.location[1] - 2)
        cv2.circle(course, wing_l, self.size, (0, 0, 0), 1)
        cv2.circle(course, wind_r, self.size, (0, 0, 0), 1)
        cv2.circle(course, tuple(self.location), self.size, tuple(color), -1)

    @staticmethod
    def _e_dist(xy1, xy2):
        sq_dist = (xy1[0] - xy2[0])**2 + (xy1[1] - xy2[1])**2
        return sq_dist**0.5

    def evaluate_fitness(self):
        max_dist = self._e_dist((0, 0), self.course_dims)
        dist = self._e_dist(self.location, self.target_location)
        worst_case = max_dist * self.lifespan
        fitness = self.success_speed * dist
        fitness_change = np.interp(fitness, [0, worst_case], [2, 0.5])

        self.fitness *= fitness_change
