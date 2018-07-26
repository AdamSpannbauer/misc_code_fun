import random
import cv2
import numpy as np
from moth_class import Moth


class SmartMoths:
    def __init__(self, n_moths=50, n_obstacles=1, n_generations=10, mate_rate=0.25, mutate_rate=0.05,
                 lifespan=500, course_dims=(400, 600)):
        self.target = (np.random.randint(5, course_dims[0] - 5),
                       np.random.randint(5, 30))
        self.n_moths = n_moths
        self.n_obstacles = n_obstacles
        self.n_generations = n_generations
        self.mate_rate = mate_rate
        self.mutate_rate = mutate_rate
        self.lifespan = lifespan
        self.course_dims = course_dims

        self.obstacles = self._gen_obstacles()
        self.course = self._create_course()
        self.moths = [Moth(course_dims, self.target, self.obstacles, lifespan) for _ in range(n_moths)]
        self.generation_i = 0
        self.victory_lap_i = -1

    def _create_course(self):
        course = np.zeros(self.course_dims[::-1] + (3,), dtype='uint8') + 50
        self._draw_obstacles(course)
        self._draw_target(course)

        return course

    def _draw_target(self, course):
        cv2.circle(course, self.target, 20, (255, 255, 255), -1)
        cv2.circle(course, self.target, 15, (0, 0, 255), -1)
        cv2.circle(course, self.target, 10, (255, 255, 255), -1)
        cv2.circle(course, self.target, 5, (0, 0, 255), -1)
        cv2.circle(course, self.target, 1, (255, 255, 255), -1)

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
        for frame in range(self.lifespan):
            course_clone = self.course.copy()
            cv2.putText(course_clone,
                        'Generation {}'.format(self.generation_i),
                        (10, self.course_dims[1] - 40), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 2)
            cv2.putText(course_clone,
                        'Success Rate: {}%'.format(self.success_rate()),
                        (10, self.course_dims[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 2)

            for moth in self.moths:
                moth.update()
                is_victory_lap = (self.victory_lap_i - 1) == self.generation_i
                moth.show(course_clone, victory_lap=is_victory_lap)

            cv2.imshow('Smart Moths (Esc to Quit)', course_clone)
            key = cv2.waitKey(1)

            if key == 27 or self.victory_lap_i == self.generation_i:
                return 'stop early'

            if self.victory_lap_i == -1 and self.success_rate() == 100:
                self.victory_lap_i = self.generation_i + 2

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
                for i in range(self.lifespan):
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
