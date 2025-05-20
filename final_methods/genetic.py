# Add directory to sys.path to allow importing modules like model, CoveringSolver, etc.
import sys
sys.path.append('./..')
sys.path.append('.')

import os
from model import ProblemModel, PopulationNode, FirstSolution
import finalsolvers
from generate_vrp import generate_lkh3_vrp_file_from_solution, lkh3_sol_to_jagged
import random as rng

instance_id = sys.argv[1]




try:
    os.mkdir(f'Final_solutions/{instance_id}')
except Exception:
    pass
model = ProblemModel.from_file(f'instances/{instance_id}.txt')

def generate_random():
    rand_indexes = [i for i in range(model.num_communities)]
    rng.shuffle(rand_indexes)
    finalsolvers.solve_given_r(model, 40000)
    return rand_indexes[:model.num_healthcenters]
    center_indexes = rand_indexes[:model.num_healthcenters]

def crossover(chromosome1, chromosome2):
    rng.shuffle(chromosome1)
    rng.shuffle(chromosome2)
    genes_to_take = rng.randint(0, len(chromosome2))
    child = []
    child.extend(chromosome1[:genes_to_take])
    child.extend(chromosome2[:(len(chromosome1)-genes_to_take)])
    return child

def mutate(chromosome):
    rng.shuffle(chromosome)
    chromosome.pop()
    while 1:
        new_center = rng.randint(0, len(chromosome))
        if new_center not in chromosome:
            chromosome.append(new_center)
            return chromosome

def eval(chromosome):
    centers = [model.nodes[i] for i in chromosome]
    initial_sol = FirstSolution([], model)
    initial_sol.centers = centers
    res = finalsolvers.solve_distribute_cities(initial_sol)
    print(res.print_sol())
    return res, res.calculate_objective()

pop_size = 10
mutation_count = 3
population = [generate_random() for _ in range(pop_size)]
population = [[i, eval(i)] for i in population]
best_sol = 10**8
print(population[0][1][1])
population.sort(key=(lambda x: x[1][1]))

while 1:
    if population[0][1][1] < best_sol:
        population[0][1][0].to_file(f'Final_solutions/{instance_id}/Sol_{instance_id}.txt')
        best_sol = population[0][1][1]
    population = population[:(pop_size//2)]
    while len(population) != pop_size:
        mom = rng.choice(population[:(pop_size//2)])
        dad = rng.choice(population[:(pop_size//2)])
        kid = crossover(mom[0], dad[0])
        for _ in range(mutation_count):
            kid = mutate(kid)
        population.append([kid, eval(kid)])
    population.sort(key= lambda x: x[1][1])


print(res.print_sol())