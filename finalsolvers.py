# Solves the first part of the problem, note that there may be multiple solutions
from model import *
import algos
import gurobipy as gp
from gurobipy import GRB

import sys

#sys.stdout = open("output_log.txt", "w")

# Finds *one* solution if optimal solution is below given radius. Can be used with binary search
def solve_given_r(problem: ProblemModel, radius):
    model = gp.Model('Sabanci_Covering_Model')
    lower_range = radius - 2*problem.beta
    feasible_ranges = algos.get_points_in_range(radius, problem.nodes, min_dist=lower_range)
    # Decision variables
    # 1 if city i contains a healthcenter, 0 otherwise
    print(f'Initializing decision variables.')
    is_center = model.addVars(problem.num_communities, vtype=GRB.BINARY)
    
    # 1 if city i is assigned to city j, 0 otherwise
    is_assigned_to = model.addVars(problem.num_communities, problem.num_communities, vtype=GRB.BINARY)

    # upper and lower capacities
    upper_capacity = model.addVar()
    lower_capacity = model.addVar()


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
        outside_points = algos.get_points_out_range(radius, problem.nodes, min_dist=lower_range)
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
        used_capacity = gp.quicksum(problem.nodes[j].population_size * is_assigned_to[j,i] for j in range(problem.num_communities))
        model.addConstr(
             used_capacity <= point.healthcare_capacity
            )
        model.addConstr(
            upper_capacity >= used_capacity
        )
        model.addConstr(
            lower_capacity <= used_capacity + (1-is_center[i])*bigM
        )
        
    model.addConstr(upper_capacity - lower_capacity <= problem.alpha)


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
            return res
        else:
            print(f'No feasible solution found for r={radius}')
            return False

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


    # upper and lower capacities
    upper_capacity = model.addVar()
    lower_capacity = model.addVar()

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
        used_capacity = gp.quicksum(problem.nodes[j].population_size * is_assigned_to[j,i] for j in range(problem.num_communities))
        model.addConstr(
             used_capacity <= point.healthcare_capacity
            )
        model.addConstr(
            upper_capacity >= used_capacity
        )
        model.addConstr(
            lower_capacity <= used_capacity + (1-is_center[i])*bigM
        )

    model.addConstr(upper_capacity-lower_capacity <= problem.alpha)

    max_dist = model.addVar()
    min_dist = model.addVar()
    if 0:
        for i in range(problem.num_communities):
            node = problem.nodes[i]
            dist_bigM = 0
            for j in range(problem.num_communities):
                dist_bigM = max(node.population_size*node.dist_to(problem.nodes[j]) ,dist_bigM)
            for j in range(problem.num_communities):
                model.addConstr(
                    node.population_size * node.dist_to(problem.nodes[j])* is_assigned_to[i, j] <=
                    max_dist + ((1-is_center[j])*dist_bigM)
                )
            for j in range(problem.num_communities):
                model.addConstr(
                    node.population_size * node.dist_to(problem.nodes[j])* is_assigned_to[i, j] >=
                    min_dist - ((1-is_center[j])*dist_bigM)
                )
    else:
        for i in range(problem.num_communities):
            d_i = model.addVar()
            model.addConstr(
                d_i == gp.quicksum((problem.nodes[i].dist_to(problem.nodes[j]) * problem.nodes[i].population_size) * is_assigned_to[i, j] for j in range(problem.num_communities))
            )
            model.addConstr(d_i <= max_dist)
            model.addConstr(d_i >= min_dist)
    model.addConstr(max_dist - min_dist <= problem.beta)

    print(f'Starting optimization...')        
    model.setObjective(max_dist, GRB.MINIMIZE)
    model.optimize()
    if 1:
        if model.status != GRB.INFEASIBLE:
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
def solve_capacity_removed(problem: ProblemModel, max_radius, banned_sols = None):
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
    
    # Remove already done solutions
    if banned_sols:
        for banned_solution in banned_sols:
            centers: List[PopulationNode] = banned_solution.centers
            model.addConstr(
                gp.quicksum(is_center[c.index-1] for c in centers) <= len(centers) -1
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
            #res.print_sol()
            return res
        else:
            print(f'No feasible solution found for r={max_radius}')
            return False

# distributes cities, with given healthcare centers
def solve_distribute_cities(curr_sol: FirstSolution):
    problem = curr_sol.model
    
    model = gp.Model()
    #model.setParam('TimeLimit', 60*2)

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
        return new_sol

def solve_capacity_removed_withz(problem: ProblemModel, max_radius, banned_sols = None):
    model = gp.Model('Sabanci_Covering_Model_RelaxedC')
    feasible_ranges = algos.get_points_in_range(max_radius, problem.nodes)
    center_can_cover = [[] for _ in range(problem.num_communities)]
    for i in range(problem.num_communities):
        for j in feasible_ranges[i]:
            center_can_cover[j].append(i)
    # Decision variables
    print(f'Initializing decision variables.')
    # 1 if city i contains a healthcenter, 0 otherwise
    is_center = model.addVars(problem.num_communities, vtype=GRB.BINARY)

    # add a score to cities with more neighbours to produce better solutions for next part
    scores = [0] * problem.num_communities
    avg_neighbour_cnt = sum(len(x) for x in center_can_cover)/problem.num_communities
    for i in range(len(scores)):
        scores[i] = (len(center_can_cover[i]))/problem.num_communities * 10 # <-- maybe provides more numerical stability
        #print(f'Score: {scores[i]}, neighbour: {len(feasible_ranges[i])}')
    #input()



    print(f'Adding constraints')
    Z = model.addVar()
    print(f'C-1')
    model.addConstr(
        gp.quicksum(scores[i]*is_center[i] for i in range(problem.num_communities)) == Z
    )
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
    
    # Remove already done solutions
    if baned_sols:
        for banned_solution in banned_sols:
            centers: List[PopulationNode] = banned_solution.centers
            model.addConstr(
                gp.quicksum(is_center[c.index-1] for c in centers) <= len(centers) -1
            )


    print(f'Starting optimization...')
    model.setObjective(Z, GRB.MAXIMIZE)
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
            print(f"Heuristic Z={Z.X}")
            return res
        else:
            print(f'No feasible solution found for r={max_radius}')
            return False
