import random
import cv2
import numpy as np


class Moth:
    def __init__(self, canvas_dims, target_location, flight_path_size=300, size=3):
        self.canvas_dims = canvas_dims
        self.flight_path_size = flight_path_size
        self.size = size
        self.start_location = np.array([self.canvas_dims[0] / 2, int(self.canvas_dims[1] * 0.9)], dtype='int')
        self.location = self.start_location.copy()
        self.velocity = np.array([0, -1], dtype='int')
        self.flight_path = self._random_flight_path()
        self.step = 0
        self.fitness = 0.5
        self.target_location = target_location
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
                self.location[0] > self.canvas_dims[0] or
                self.location[1] > self.canvas_dims[1])

    def update(self):
        if not self._is_offscreen():
            if self._e_dist(self.location, self.target_location) <= 19:
                self.location = self.target_location
                self.color = (17, 102, 1)
                self.succeeded = 1
            else:
                self.velocity = self.flight_path[self.step]
                self.location += self.velocity
        self.step += 1

    def show(self, canvas):
        cv2.circle(canvas, tuple(self.location), self.size, self.color, -1)

    @staticmethod
    def _e_dist(xy1, xy2):
        sq_dist = (xy1[0] - xy2[0])**2 + (xy1[1] - xy2[1])**2
        return sq_dist**0.5

    def evaluate_fitness(self):
        max_dist = self._e_dist((0, 0), self.canvas_dims)
        dist = self._e_dist(self.location, self.target_location)
        fitness_change = np.interp(dist, [0, max_dist], [2, 0.5])

        self.fitness *= fitness_change


class Population:
    def __init__(self, target, n_moths=50, n_generations=10, mate_rate=0.25, mutate_rate=0.05,
                 n_frames=500, canvas_dims=(400, 400)):
        self.target = target
        self.n_moths = n_moths
        self.n_generations = n_generations
        self.mate_rate = mate_rate
        self.mutate_rate = mutate_rate
        self.n_frames = n_frames
        self.canvas_dims = canvas_dims

        self.canvas = np.zeros(canvas_dims[::-1] + (3,), dtype='uint8')
        cv2.circle(self.canvas, target, 20, (255, 255, 255), -1)
        self.moths = [Moth(canvas_dims, target, n_frames) for _ in range(n_moths)]
        self.generation_i = 0

    def _run_generation(self):
        for frame in range(self.n_frames):
            canvas_clone = self.canvas.copy()
            cv2.putText(canvas_clone,
                        'Generation {}'.format(self.generation_i),
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (200, 200, 200), 2)
            cv2.putText(canvas_clone,
                        'Success Rate: {}%'.format(self.success_rate()),
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, .5, (200, 200, 200), 2)

            for moth in self.moths:
                moth.update()
                moth.show(canvas_clone)

            if self.success_rate() == 100:
                wait_key = 0
            else:
                wait_key = 1

            cv2.imshow('Smart Moths (Esc to Quit)', canvas_clone)
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
    width = 400
    height = 600
    # target_loc = (width // 2, 0)
    target_loc = (np.random.randint(20, width - 20),
                  np.random.randint(20, height - 200))

    smart_moths = Population(target=target_loc,
                             n_moths=100,
                             n_generations=20,
                             mate_rate=0.25,
                             n_frames=500,
                             canvas_dims=(width, height))

    smart_moths.find_light()
