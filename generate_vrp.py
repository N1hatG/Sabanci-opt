import argparse
from model import ProblemModel

def generate_lkh3_vrp_file_from_solution(solution, instance_id: str, vehicle_capacity: int = 10000):
    output_path = f'solutions/{instance_id}/part2.vrp'
    depot_x, depot_y = solution.model.depot
    centers = solution.centers
    assigned = solution.assigned_cities

    nodes = [(0, depot_x, depot_y, 0)]  # depot is node 0
    for center in centers:
        demand = sum(city.population_size for city in assigned[center])
        nodes.append((center.index, center.coords[0], center.coords[1], demand))

    remapped = [(i + 1, x, y, d) for i, (orig_id, x, y, d) in enumerate(nodes)]
    id_map = {orig_id: i + 1 for i, (orig_id, x, y, d) in enumerate(nodes)}

    def format_vrp(nodes, cap):
        header = [
            "NAME : HealthcareRouting",
            "TYPE : CVRP",
            f"DIMENSION : {len(nodes)}",
            "EDGE_WEIGHT_TYPE : EUC_2D",
            f"CAPACITY : {cap}",
            "NODE_COORD_SECTION"
        ]
        coords = [f"{nid} {int(x)} {int(y)}" for nid, x, y, _ in nodes]
        demands = ["DEMAND_SECTION"] + [f"{nid} {d}" for nid, _, _, d in nodes]
        tail = ["DEPOT_SECTION", "1", "-1", "EOF"]
        return "\n".join(header + coords + demands + tail)

    content = format_vrp(remapped, vehicle_capacity)
    with open(output_path, "w") as f:
        f.write(content)
    with open(f'solutions/{instance_id}/part2.par', 'w+') as f:
        f.write(f'PROBLEM_FILE = solutions/{instance_id}/part2.vrp\nTOUR_FILE = solutions/{instance_id}/tour.sol')
    print(f"✅ VRP file written to: {output_path}")

    return output_path

def lkh3_sol_to_jagged(sol_path, city_count):
    text = open(sol_path).readlines()
    curr_ind = 0
    city_arr = []
    while text[curr_ind] != 'TOUR_SECTION\n':
        curr_ind += 1
    curr_ind += 1
    while text[curr_ind] != '-1\n':
        city_arr.append(int(text[curr_ind].strip()))
        curr_ind += 1
    city_arr.append(10**8) # flush the last tour
    all_tours = []
    curr_tour = []
    for city in city_arr:
        if city <= city_count:
            curr_tour.append(city-1)
            continue
        curr_tour.append(0)
        all_tours.append(curr_tour)
        curr_tour = [0]
    return(all_tours)
