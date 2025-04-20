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
res = CoveringSolver.solve_given_r(model, upper_bound)
if not res:
    print(f"Model infeasible for r={upper_bound}")
    sys.exit()
res.to_file(f'solutions/{instance_id}/Sol_{instance_id}.txt')
generate_vrp.generate_lkh3_vrp_file_from_solution(res, instance_id, time_limit=1)
solution = res
if len(sys.argv) > 3:
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
    for tour_num, tour in enumerate(tours):
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
            print(f'Tour {tour_num+1} is out of capacity')
            sys.exit()
        res_str += f"""Route {tour_num+1}: {' -> '.join(str_tour)}\n"""
    res_str += f'Objective Value: {tot_dist}'
    print(f'Total distance: {tot_dist}')
    with open(f'solutions/{instance_id}/Sol_{instance_id}.txt', 'a') as f:
        f.write(res_str)
    print(f'Written to solutions/{instance_id}/Sol_{instance_id}.txt')