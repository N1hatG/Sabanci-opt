from model import *
from typing import List

def get_points_in_range(radius, nodes: List[PopulationNode]):
    # For each node i, returns the list of nodes that are in the radius of i, with population weighted
    # O(n^2) for now, maybe there is an O(nlogn) algorithm
    res = [[] for _ in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i==j:
                res[i].append(j)
                continue
            if (nodes[i].population_size * nodes[i].dist_to(nodes[j])) <= radius:
                res[i].append(j)
    return res

def get_points_out_range(radius, nodes: List[PopulationNode]):
    # For each node i, returns the list of nodes that are in the radius of i, with population weighted
    # O(n^2) for now, maybe there is an O(nlogn) algorithm
    res = [[] for _ in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i==j:
                continue
            if (nodes[i].population_size * nodes[i].dist_to(nodes[j])) > radius:
                res[i].append(j)
    return res