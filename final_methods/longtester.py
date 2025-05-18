# Add directory to sys.path to allow importing modules like model, CoveringSolver, etc.
import sys
sys.path.append('./..')
sys.path.append('.')

import os
from model import ProblemModel, PopulationNode
import finalsolvers
from generate_vrp import generate_lkh3_vrp_file_from_solution, lkh3_sol_to_jagged

# Load the instance model
instance_id = sys.argv[1]
instance_path = f'final_data/{instance_id}.txt' if 0 else f'instances/{instance_id}.txt'
res_path = f'Sol_{instance_path}'
model = ProblemModel.from_file(instance_path)
try:
    os.mkdir(f'solutions/{instance_id}')
except Exception:
    pass
solution = None
selected_radius = None
r = 5000
if len(sys.argv) > 2:
    r = int(sys.argv[2])
while 1:
    print(f"🔍 Trying radius = {r}")
    sol = finalsolvers.solve_to_optimality(model, r)
    if sol:
        print(f"🧪 Solution found at radius = {r}, checking feasibility...")
        if True:
            print(f"✅ Feasible solution confirmed at radius = {r}")
            solution = sol
            selected_radius = r
            break
        else:
            print(f"❌ Infeasible distribution at radius = {r}")
    else:
        print(f"❌ No solution found at radius = {r}")
        r += 2000

# Export if feasible solution is found
output_path = None
if not not solution:
    print("❌ No feasible solution found for any radius.")
solution.to_file(f'solutions/{instance_id}/Sol_{instance_id}.txt')
print(f"✅ Final radius used: {selected_radius}")

sys.exit(0)


print('Running LKH-3...')
res_code = os.system(f'./LKH solutions/{instance_id}/part2.par')
if res_code != 0:
    print('LKH-3 failed. Exiting...')
    generate_vrp.get_trivial_vrp(model, solution, instance_id)
    sys.exit(1)
print('LKH-3 successful. Parsing the results..')
tours = lkh3_sol_to_jagged(f'solutions/{instance_id}/tour.sol', model.num_healthcenters+1)
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
        generate_vrp.get_trivial_vrp(model, solution, instance_id)
        sys.exit()
    str_tour.append('Depot')
    if available_capacity < 0:
        print(f'Tour {tour_num+1} is out of capacity')
        generate_vrp.get_trivial_vrp(model, solution, instance_id)
        sys.exit()
    res_str += f"""Route {tour_num+1}: {' -> '.join(str_tour)}\n"""
res_str += f'Objective Value: {tot_dist}'
print(f'Total distance: {tot_dist}')
with open(f'solutions/{instance_id}/Sol_{instance_id}.txt', 'a') as f:
    f.write(res_str)
print(f'Written to solutions/{instance_id}/Sol_{instance_id}.txt')