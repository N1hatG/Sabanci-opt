# Add directory to sys.path to allow importing modules like model, CoveringSolver, etc.
import sys
sys.path.append('./..')
sys.path.append('.')

import os
from model import ProblemModel, PopulationNode
import finalsolvers
from generate_vrp import generate_lkh3_vrp_file_from_solution, lkh3_sol_to_jagged

instance_id = sys.argv[1]
upper_bound = int(sys.argv[2])
try:
    os.mkdir(f'Final_solutions/{instance_id}')
except Exception:
    pass
model = ProblemModel.from_file(f'instances/{instance_id}.txt')
res = finalsolvers.solve_given_r(model, upper_bound)
if not res:
    print(f"Model infeasible for r={upper_bound}")
    sys.exit()
res.to_file(f'Final_solutions/{instance_id}/Sol_{instance_id}.txt')
print(res.print_sol())
