import itertools as it
from typing import List

def to_num_arr(inp_str):
    splitted = list(inp_str.strip().split())
    for i in range(len(splitted)):
        if '.' in splitted[i]:
            splitted[i] = float(splitted[i])
        else:
            splitted[i] = int(splitted[i])
    return splitted


class ProblemModel:
    def __init__(self, num_communities, num_healthcenters, depot, nodes):
        self.num_communities = num_communities
        self.num_healthcenters = num_healthcenters
        self.depot = depot
        self.nodes: List[PopulationNode] = nodes
        pass
    def __str__(self):
        res = f'{self.num_communities} {self.num_healthcenters}\n'
        res += f'0 {self.depot[0]} {self.depot[1]}\n'
        for node in self.nodes:
            res += f'{str(node)}\n'
        return res
    
    def from_file(filepath):
        lines = []
        with open(filepath, 'r') as fil:
            lines = fil.readlines()
        if not lines:
            print("Wadafak")
            return
        (communities,healthcenters) = to_num_arr(lines[0])
        _, centerx, centery = to_num_arr(lines[1])
        nodes = []
        for node_str in lines[2:]:
            nodes.append(PopulationNode.from_str(node_str))
        return ProblemModel(communities, healthcenters, (centerx, centery), nodes)
    
class PopulationNode:
    def __init__(self, index, coords, population_size, healthcare_capacity):
        self.index = index
        self.coords = coords
        self.population_size = population_size
        self.healthcare_capacity = healthcare_capacity
    
    def __str__(self):
        return f'{self.index} {self.coords[0]} {self.coords[1]} {self.healthcare_capacity} {self.population_size}'
    def from_str(str_to_parse: str):
        parsed_nums = to_num_arr(str_to_parse)
        return PopulationNode(parsed_nums[0],
                             (parsed_nums[1], parsed_nums[2]),
                              parsed_nums[4],
                              parsed_nums[3])
    
    def dist_to(self, other_node: 'PopulationNode'):
        return ((self.coords[0]-other_node.coords[0])**2 + (self.coords[1]-other_node.coords[1])**2)**(1/2)
        
class FirstSolution:
    def __init__(self, assigned_cities, model: ProblemModel):
        self.model = model
        formatted_cities = {}
        centers = []
        for key in assigned_cities:
            city: PopulationNode = None
            if type(key) is PopulationNode:
                city = key
            elif type(key) is int:
                city = model.nodes[key]
            formatted_cities[city] = []
            if len(assigned_cities[key]):
                centers.append(city)
                for city2 in assigned_cities[key]:
                    if type(city2) is int:
                        formatted_cities[city].append(model.nodes[city2])
                    elif type(city2) is PopulationNode:
                        formatted_cities[city].append(city2)
                    else:
                        raise Exception()
        self.assigned_cities = formatted_cities
        self.centers = centers

    def calculate_objective(self):
        max_r = 0
        for center in self.assigned_cities:
            for city in self.assigned_cities[center]:
                max_r = max(city.population_size * city.dist_to(center) ,max_r)
        return max_r
    
    def print_sol(self):
        print(f'Centers are deployed in:')
        for center in self.assigned_cities:
            print(center.index)
        print("With cities assigned:")
        for center in self.assigned_cities:
            print(f'''City {center.index} <- ({" ".join([str(i.index) for i in self.assigned_cities[center]])})''')
        print(f'With Z={self.calculate_objective()}')
        self.is_feasible(do_print_reason=True)

    def is_feasible(self, do_print_reason = False):
        is_assigned = [False] * self.model.num_communities
        used_capacities = {}
        for c in self.centers:
            used_capacities[c] = 0
        if len(self.centers) > self.model.num_healthcenters:
            if do_print_reason:
                print("Infeasible because of too many healthcenters")
            return False
        for c in self.assigned_cities:
            for city in self.assigned_cities[c]:
                is_assigned[city.index-1] = True
                used_capacities[c] += city.population_size
        for i in range(self.model.num_communities):
            if not is_assigned[i]:
                if do_print_reason:
                    print(f'City {i+1} is unassigned')
                return False
        for c in used_capacities:
            if c.healthcare_capacity < used_capacities[c]:
                if do_print_reason:
                    print(f'Infeasible because city {c.index} exceeds capacity')
                return False
        return True
        