import random
import cv2
import numpy as np


class Moth:
    def __init__(self, course_dims, target_location, obstacles=[], flight_path_size=300, size=3):
        self.course_dims = course_dims
        self.flight_path_size = flight_path_size
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

    def reset(self):
        self.location = self.start_location.copy()
        self.step = 0
        self.fitness = 0.5

    def _random_flight_path(self):
        velocities = []
        for _ in range(self.flight_path_size):
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
            else:
                self.velocity = self.flight_path[self.step]
                self.location += self.velocity
        self.step += 1

    def show(self, course):
        cv2.circle(course, tuple(self.location), self.size, self.color, -1)

    @staticmethod
    def _e_dist(xy1, xy2):
        sq_dist = (xy1[0] - xy2[0])**2 + (xy1[1] - xy2[1])**2
        return sq_dist**0.5

    def evaluate_fitness(self):
        max_dist = self._e_dist((0, 0), self.course_dims)
        dist = self._e_dist(self.location, self.target_location)
        fitness_change = np.interp(dist, [0, max_dist], [2, 0.5])

        self.fitness *= fitness_change


class SmartMoths:
    def __init__(self, n_moths=50, n_obstacles=1, n_generations=10, mate_rate=0.25, mutate_rate=0.05,
                 n_frames=500, course_dims=(400, 600)):
        self.target = (np.random.randint(5, course_dims[0] - 5),
                       np.random.randint(5, 30))
        self.n_moths = n_moths
        self.n_obstacles = n_obstacles
        self.n_generations = n_generations
        self.mate_rate = mate_rate
        self.mutate_rate = mutate_rate
        self.n_frames = n_frames
        self.course_dims = course_dims

        self.obstacles = self._gen_obstacles()
        self.course = self._create_course()
        self.moths = [Moth(course_dims, self.target, self.obstacles, n_frames) for _ in range(n_moths)]
        self.generation_i = 0

    def _create_course(self):
        course = np.zeros(self.course_dims[::-1] + (3,), dtype='uint8')
        self._draw_obstacles(course)
        self._draw_target(course)

        return course

    def _draw_target(self, course):
        cv2.circle(course, self.target, 20, (255, 255, 255), -1)

    def _draw_obstacles(self, course):
        for obstacle in self.obstacles:
            cv2.rectangle(course, obstacle[0], obstacle[1], (0, 0, 142), -1)

    def _gen_obstacles(self):
        x_range = (30, self.course_dims[0] * .75)
        y_range = (30, self.course_dims[1] * .75)
        w_range = (50, 100)
        h_range = (50, 100)

        obstacles = []
        for _ in range(self.n_obstacles):
            x, y, w, h = (np.random.randint(*r) for r in [x_range, y_range, w_range, h_range])
            obstacles.append([(x, y), ((x + w), (y + h))])
        return obstacles

    def _run_generation(self):
        for frame in range(self.n_frames):
            course_clone = self.course.copy()
            cv2.putText(course_clone,
                        'Generation {}'.format(self.generation_i),
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (200, 200, 200), 2)
            cv2.putText(course_clone,
                        'Success Rate: {}%'.format(self.success_rate()),
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, .5, (200, 200, 200), 2)

            for moth in self.moths:
                moth.update()
                moth.show(course_clone)

            if (frame == self.n_frames - 1 and
                    (self.success_rate() == 100 or self.generation_i == self.n_generations - 1)):
                wait_key = 0
            else:
                wait_key = 1

            cv2.imshow('Smart Moths (Esc to Quit)', course_clone)
            key = cv2.waitKey(wait_key)

            if key == 27:
                return 'stop early'

        for moth in self.moths:
            moth.evaluate_fitness()

        self.generation_i += 1

        return None

    def _mutation(self, v):
        if np.random.rand() < self.mutate_rate:
            noise = np.random.randint(-5, 6)
            v += noise
            if v < -5:
                v = -5
            if v > 5:
                v = 5
        return v

    def _mate(self):
        n = int(self.n_moths * self.mate_rate)
        fitnesses = [moth.fitness for moth in self.moths]
        top_n_moth_inds = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i])[-n:]

        for moth in self.moths:
            if not moth.succeeded:
                for i in range(self.n_frames):
                    parent = self.moths[random.choice(top_n_moth_inds)]
                    new_x = self._mutation(parent.flight_path[i][0])
                    new_y = self._mutation(parent.flight_path[i][1])

                    moth.flight_path[i] = np.array([new_x, new_y], dtype='int')
            moth.reset()

    def find_light(self):
        for gen_i in range(self.n_generations):
            stop = self._run_generation()
            if stop:
                break
            self._mate()

    def success_rate(self):
        return 100 * sum(moth.succeeded for moth in self.moths) // self.n_moths


if __name__ == '__main__':
    smart_moths = SmartMoths(n_obstacles=4,
                             n_moths=200,
                             n_generations=30,
                             mate_rate=0.25,
                             n_frames=600)

    smart_moths.find_light()
