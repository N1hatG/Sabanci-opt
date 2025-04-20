import sys
import os
from model import *
import CoveringSolver
import generate_vrp
instance_id = sys.argv[1]
upper_bound = int(sys.argv[2])

try:
    os.mkdir(f'solutions/{instance_id}')
except Exception:
    pass
model = ProblemModel.from_file(f'instances/{instance_id}.txt')
def run_lkh3(solution):
    status_code = os.system(f'./LKH solutions/{instance_id}/part2.par')
    if status_code != 0:
        print(f'LKH-3 failed. Exiting...')
        sys.exit(1)
    print('LKH-3 successful. Parsing the results..')
    tours = generate_vrp.lkh3_sol_to_jagged(f'solutions/{instance_id}/tour.sol', model.num_healthcenters+1)
    for tour in tours:
        for i in range(len(tour)):
            city_id = tour[i]-2
            if city_id < 0:
                print("Depot")
            else:
                print(solution.centers[city_id].index)
    depot = PopulationNode(0, model.depot, -1, -1)
    demands = [] 
    for c in solution.centers:
        demands.append(sum(city.population_size for city in solution.assigned_cities[c]))
    res_str = 'Stage-2:\n'
    for i, tour in enumerate(tours):
        tot_dist = 0
        available_capacity = 10000
        str_tour = []
        for i in range(len(tour)-1):
            from_city = tour[i]-1
            to_city = tour[i+1]-1
            if from_city != -1:
                available_capacity -= demands[from_city]
                from_city = solution.centers[from_city]
            else:
                from_city = depot
            if to_city != -1:
                to_city = solution.centers[to_city]
            else:
                to_city = depot
            tot_dist += from_city.dist_to(to_city)
            if from_city == depot:
                str_tour.append('Depot')
            else:
                str_tour.append(f'Healthcenter at {from_city.index}')
        last_city = tour[-1]
        if last_city != 0:
            print("???????????????????????")
            sys.exit()
        str_tour.append('Depot')
        if available_capacity < 0:
            print(f'Tour {i+1} is out of capacity')
            sys.exit()
        res_str += f"""Route {i+1}: {' -> '.join(str_tour)}\n"""
    res_str += f'Objective Value: {tot_dist}'
    print(f'Total distance: {tot_dist}')
    with open(f'solutions/{instance_id}/Sol_{instance_id}.txt', 'a') as f:
        f.write(res_str)
    print(f'Written to solutions/{instance_id}/Sol_{instance_id}.txt')

    
used_sols = []
best_sol = None
while 1:
    res = CoveringSolver.solve_capacity_removed(model, upper_bound, used_sols)
    if not res:
        print(f"All solutions exhausted for r={radius}, exiting...")
        break
    solution = CoveringSolver.solve_distribute_cities(res)
    if solution:
        should_save = False
        if best_sol is not None:
            if solution.calculate_objective() < best_sol.calculate_objective():
                best_sol = solution
                should_save = True
        if best_sol is None:
            best_sol = solution
            should_save = True
        if should_save:
            solution.to_file(f'solutions/{instance_id}/Sol_{instance_id}.txt')
            generate_vrp.generate_lkh3_vrp_file_from_solution(solution, instance_id)
            

    used_sols.append(res)
    

