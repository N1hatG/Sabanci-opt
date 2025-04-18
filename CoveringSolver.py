# Solves the first part of the problem, note that there may be multiple solutions
from model import *
import algos
import gurobipy as gp
from gurobipy import GRB

import sys

sys.stdout = open("output_log.txt", "w")

# Finds *one* solution if optimal solution is below given radius. Can be used with binary search
def solve_given_r(problem: ProblemModel, radius):
    model = gp.Model('Sabanci_Covering_Model')
    feasible_ranges = algos.get_points_in_range(radius, problem.nodes)
    # Decision variables
    # 1 if city i contains a healthcenter, 0 otherwise
    print(f'Initializing decision variables.')
    is_center = model.addVars(problem.num_communities, vtype=GRB.BINARY)
    
    # 1 if city i is assigned to city j, 0 otherwise
    is_assigned_to = model.addVars(problem.num_communities, problem.num_communities, vtype=GRB.BINARY)

    # constraints
    print(f'Adding constraints')
    print(f'C3')
    if 0:
        for i in range(problem.num_communities):
            #print(f'city {i} has {len(feasible_ranges[i])} points in range')
            points_in_range = feasible_ranges[i]
            model.addConstr(
                gp.quicksum(is_assigned_to[i, other_point] for other_point in points_in_range) == 1
            )
    if 1:
        outside_points = algos.get_points_out_range(radius, problem.nodes)
        for i in range(problem.num_communities):
            points_out_range = outside_points[i]
            model.addConstr(
                gp.quicksum(is_assigned_to[i, other_point] for other_point in points_out_range) == 0
            )
            
    model.presolve()
    # maximum C healthcenters
    print(f'C1')
    model.addConstr(
        gp.quicksum(is_center[i] for i in range(problem.num_communities)) <= problem.num_healthcenters
    )

    # every city is assigned to 1 healthcenter
    print(f'C2')
    for i in range(problem.num_communities):
        model.addConstr(
            gp.quicksum(is_assigned_to[i, j] for j in range(problem.num_communities)) == 1
        )
    
    # ... which should be in range. the constraint above is not needed but i think it is necessary to set out of range
    # variables to 0
    
    # every city can only be assigned to places with healthcenters
    print(f'C4')
    bigM = problem.num_communities
    for j in range(problem.num_communities):
        model.addConstr(
            gp.quicksum(is_assigned_to[i, j] for i in range(problem.num_communities)) <= bigM* is_center[j]
        )


    # every center must not exceed its capacity
    print(f'C5')
    total_people = 0
    for node in problem.nodes:
        point: PopulationNode = node
        total_people += point.population_size
    bigM = total_people + 5

    for i in range(problem.num_communities):
        point: PopulationNode = problem.nodes[i]
        
        model.addConstr(
            gp.quicksum(problem.nodes[j].population_size * is_assigned_to[j,i] for j in range(problem.num_communities)) <= point.healthcare_capacity
            )

    print(f'Starting optimization...')        
    #model.setObjective(1)
    model.optimize()
    if 1:
        if model.status == GRB.OPTIMAL:
            assigned_cities = {}
            print(f'Solution found')
            for i in range(problem.num_communities):
                if is_center[i].X > 0.5:
                    assigned_cities[i] = []
            for i in range(problem.num_communities):
                for j in range(problem.num_communities):
                    if is_assigned_to[i, j].X > 0.5:
                        assigned_cities[j].append(i)
            res = FirstSolution(assigned_cities, problem)
            res.print_sol()
        else:
            print(f'No feasible solution found for r={radius}')

# Finds the optimal solution as long as radius is above it. Bigger radius means slower solution
def solve_to_optimality(problem: ProblemModel, radius):
    model = gp.Model('Sabanci_Covering_Model')
    feasible_ranges = algos.get_points_in_range(radius, problem.nodes)
    # Decision variables
    # 1 if city i contains a healthcenter, 0 otherwise
    print(f'Initializing decision variables.')
    is_center = model.addVars(problem.num_communities, vtype=GRB.BINARY)
    
    # 1 if city i is assigned to city j, 0 otherwise
    is_assigned_to = model.addVars(problem.num_communities, problem.num_communities, vtype=GRB.BINARY)

    # maximum distance
    Z = model.addVar()

    # constraints
    print(f'Adding constraints')
    print(f'C3')
    if 0:
        for i in range(problem.num_communities):
            #print(f'city {i} has {len(feasible_ranges[i])} points in range')
            points_in_range = feasible_ranges[i]
            model.addConstr(
                gp.quicksum(is_assigned_to[i, other_point] for other_point in points_in_range) == 1
            )
    if 1:
        outside_points = algos.get_points_out_range(radius, problem.nodes)
        for i in range(problem.num_communities):
            points_out_range = outside_points[i]
            model.addConstr(
                gp.quicksum(is_assigned_to[i, other_point] for other_point in points_out_range) == 0
            )
            
    #model.presolve()
    # maximum C healthcenters
    print(f'C1')
    model.addConstr(
        gp.quicksum(is_center[i] for i in range(problem.num_communities)) == problem.num_healthcenters
    )

    # every city is assigned to 1 healthcenter
    print(f'C2')
    for i in range(problem.num_communities):
        model.addConstr(
            gp.quicksum(is_assigned_to[i, j] for j in range(problem.num_communities)) == 1
        )
    
    # ... which should be in range. the constraint above is not needed but i think it is necessary to set out of range
    # variables to 0
    
    # every city can only be assigned to places with healthcenters
    print(f'C4')
    bigM = problem.num_communities
    for j in range(problem.num_communities):
        model.addConstr(
            gp.quicksum(is_assigned_to[i, j] for i in range(problem.num_communities)) <= bigM* is_center[j]
        )


    # every center must not exceed its capacity
    print(f'C5')
    for i in range(problem.num_communities):
        point: PopulationNode = problem.nodes[i]
        
        model.addConstr(
            gp.quicksum(problem.nodes[j].population_size * is_assigned_to[j,i] for j in range(problem.num_communities)) <= point.healthcare_capacity
            )

    # Z is bigger than all the distances    
    for i in range(problem.num_communities):
        node = problem.nodes[i]
        max_dist = 0
        for j in range(problem.num_communities):
            max_dist = max(node.population_size*node.dist_to(problem.nodes[j]) ,max_dist)
        for j in range(problem.num_communities):
            model.addConstr(
                node.population_size * node.dist_to(problem.nodes[j])* is_assigned_to[i, j] <=
                Z + ((1-is_center[j])*max_dist)
            )

    print(f'Starting optimization...')        
    model.setObjective(Z, GRB.MINIMIZE)
    model.optimize()
    if 1:
        if model.status == GRB.OPTIMAL:
            assigned_cities = {}
            print(f'Solution found')
            for i in range(problem.num_communities):
                if is_center[i].X > 0.5:
                    assigned_cities[i] = []
            for i in range(problem.num_communities):
                for j in range(problem.num_communities):
                    if is_assigned_to[i, j].X > 0.5:
                        assigned_cities[j].append(i)
            res = FirstSolution(assigned_cities, problem)
            res.print_sol()
            return res
        else:
            print(f'No feasible solution found for maxr={radius}')
            return False

# each healthcenter contains closest k points, turning n^2 decision variables to n
# but we lose the optimality
def solve_capacity_removed(problem: ProblemModel, max_radius):
    model = gp.Model('Sabanci_Covering_Model_RelaxedC')
    feasible_ranges = algos.get_points_in_range(max_radius, problem.nodes)
    # Decision variables
    print(f'Initializing decision variables.')
    # 1 if city i contains a healthcenter, 0 otherwise
    is_center = model.addVars(problem.num_communities, vtype=GRB.BINARY)

    # perhaps add a Z representing maximum of all distances and minimize it
    # constraints
    print(f'Adding constraints')


    # every city must be assigned to at least one center
    print(f'C0')
    for i in range(problem.num_communities):
        feasible_points = feasible_ranges[i]
        model.addConstr(
            gp.quicksum(is_center[i] for i in feasible_points) >= 1
        )

    # maximum C healthcenters
    print(f'C1')
    model.addConstr(
        gp.quicksum(is_center[i] for i in range(problem.num_communities)) == problem.num_healthcenters
    )


    print(f'Starting optimization...')        
    model.optimize()
    if 1:
        if model.status == GRB.OPTIMAL:
            assigned_cities = {}
            print(f'Solution found')
            for i in range(problem.num_communities):
                if is_center[i].X > 0.5:
                    assigned_cities[i] = []
            center_can_cover = [[] for _ in range(problem.num_communities)]
            for i in range(problem.num_communities):
                for j in feasible_ranges[i]:
                    center_can_cover[j].append(i)
            for i in assigned_cities:
                for j in center_can_cover[i]:
                    assigned_cities[i].append(j)
            res = FirstSolution(assigned_cities, problem)
            res.print_sol()
            return res
        else:
            print(f'No feasible solution found for r={max_radius}')
            return False

# distributes cities, with given healthcare centers
def solve_distribute_cities(curr_sol: FirstSolution):
    problem = curr_sol.model
    
    model = gp.Model()

    centers = []
    # 1 if city i assigned to center c
    is_assigned_to = model.addVars(problem.num_communities, problem.num_healthcenters, vtype=GRB.BINARY)

    for i in range(problem.num_communities):
        model.addConstr(
            gp.quicksum(is_assigned_to[i, j] for j in range(problem.num_healthcenters)) == 1
        )
    
    is_assignable_to = [[] for i in range(problem.num_communities)]
    for center in curr_sol.assigned_cities:
        for city in curr_sol.assigned_cities[center]:
            center_ind = curr_sol.centers.index(center)
            is_assignable_to[city.index-1].append(center_ind)
    
    for i in range(problem.num_communities):
        assignable_centers = is_assignable_to[i]
        model.addConstr(
            gp.quicksum(is_assigned_to[i, j] for j in assignable_centers) == 1
        )
    
    for center in range(problem.num_healthcenters):
        model.addConstr(
            gp.quicksum(problem.nodes[i].population_size* is_assigned_to[i, center] for i in range(problem.num_communities)) <= curr_sol.centers[center].healthcare_capacity
        )

    model.optimize()
    if model.status == GRB.INFEASIBLE:
        return False
    elif model.status == GRB.OPTIMAL:
        assigned_cities = [[] for _ in range(problem.num_healthcenters)]
        for i in range(problem.num_communities):
            for j in range(problem.num_healthcenters):
                if is_assigned_to[i, j].X > 0.5:
                    assigned_cities[j].append(i)
        assigned_dict = {}
        for i in range(problem.num_healthcenters):
            assigned_dict[curr_sol.centers[i]] = assigned_cities[i]
        new_sol = FirstSolution(assigned_dict, problem)
        new_sol.print_sol()
        return True


def solve_capacity_removed_withz(problem: ProblemModel, max_radius, banned_sols = None, lb=None):
    model = gp.Model('Sabanci_Covering_Model_RelaxedC')
    feasible_ranges = algos.get_points_in_range(max_radius, problem.nodes)
    # Decision variables
    print(f'Initializing decision variables.')
    # 1 if city i contains a healthcenter, 0 otherwise
    is_center = model.addVars(problem.num_communities, vtype=GRB.BINARY)

    Z = model.addVar()
    
    # represents maximum distance to healthcenter in each city, minimum is better but isnt linear programmable
    city_max = model.addVars(problem.num_communities)

    print(f'Adding constraints')


    # every city must be assigned to at least one center
    print(f'C0')
    for i in range(problem.num_communities):
        feasible_points = feasible_ranges[i]
        model.addConstr(
            gp.quicksum(is_center[i] for i in feasible_points) >= 1
        )

    # maximum C healthcenters
    print(f'C1')
    model.addConstr(
        gp.quicksum(is_center[i] for i in range(problem.num_communities)) == problem.num_healthcenters
    )
    
    # calculate city_maxes
    print(f'C2')
    for i in range(problem.num_communities):
        node = problem.nodes[i]
        feasible_points = feasible_ranges[i]
        for j in feasible_points:
            dist = node.population_size * node.dist_to(problem.nodes[j])
            model.addConstr(
                city_max[i] >= dist*is_center[j]
            )

    # Z is maximum of all maxes
    print(f'C3')
    for i in range(problem.num_communities):
        model.addConstr(
            city_max[i] <= Z
        )

    print(f'Starting optimization...')

    if lb:
        model.addConstr(
            Z >= lb, name='Lower_Bound'
        )
    model.setObjective(Z, GRB.MINIMIZE)
    model.optimize()
    if 1:
        if model.status == GRB.OPTIMAL:
            assigned_cities = {}
            print(f'Solution found')
            for i in range(problem.num_communities):
                if is_center[i].X > 0.5:
                    assigned_cities[i] = []
            center_can_cover = [[] for _ in range(problem.num_communities)]
            for i in range(problem.num_communities):
                for j in feasible_ranges[i]:
                    center_can_cover[j].append(i)
            for i in assigned_cities:
                for j in center_can_cover[i]:
                    assigned_cities[i].append(j)
            res = FirstSolution(assigned_cities, problem)
            res.print_sol()
            print(f'Models objective Z={Z.X}')
            return res
        else:
            print(f'No feasible solution found for r={max_radius}')
            return False
