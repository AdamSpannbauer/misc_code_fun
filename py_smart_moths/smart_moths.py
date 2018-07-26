import argparse
from smart_moth_class import SmartMoths

ap = argparse.ArgumentParser()
ap.add_argument('-m', '--nMoths', type=int, default=200, help='Number of moths to create')
ap.add_argument('-o', '--nObstacles', type=int, default=4, help='Number of obstacles')
ap.add_argument('-g', '--nGenerations', type=int, default=100, help='Number of generations')
ap.add_argument('-l', '--lifespan', type=int, default=500, help='Number of frames per generation')
ap.add_argument('-u', '--mutateRate', type=float, default=0.05, help='Percent chance of a gene mutating')
ap.add_argument('-a', '--mateRate', type=float, default=0.25,
                help='Top percentage of moths to be pass genes to next generation')
args = vars(ap.parse_args())

smart_moths = SmartMoths(n_moths=args['nMoths'],
                         n_obstacles=args['nObstacles'],
                         n_generations=args['nGenerations'],
                         mate_rate=args['mutateRate'],
                         mutate_rate=args['mateRate'],
                         lifespan=args['lifespan'])

smart_moths.find_light()

print('\n\n*{}% Success Rate* after *{} Generations*\n\n'.format(smart_moths.success_rate(),
                                                                 smart_moths.generation_i))
