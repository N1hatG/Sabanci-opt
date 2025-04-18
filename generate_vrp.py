import argparse
from model import ProblemModel

def generate_lkh3_vrp_file_from_solution(solution, output_path: str, vehicle_capacity: int = 10000):
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
    print(f"✅ VRP file written to: {output_path}")

    return output_path