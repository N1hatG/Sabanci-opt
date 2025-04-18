# Add directory to sys.path to allow importing modules like model, CoveringSolver, etc.
import sys

from model import ProblemModel
import CoveringSolver
from generate_vrp import generate_lkh3_vrp_file_from_solution

# Load the instance model
instance_path = "instances/Instance_12.txt"
model = ProblemModel.from_file(instance_path)

# Try predefined radii
radii = [5000, 10000, 15000, 20000]
solution = None
selected_radius = None

for r in radii:
    print(f"🔍 Trying radius = {r}")
    sol = CoveringSolver.solve_to_optimality(model, r)
    if sol:
        print(f"🧪 Solution found at radius = {r}, checking feasibility...")
        if CoveringSolver.solve_distribute_cities(sol):
            print(f"✅ Feasible solution confirmed at radius = {r}")
            solution = sol
            selected_radius = r
            break
        else:
            print(f"❌ Infeasible distribution at radius = {r}")
    else:
        print(f"❌ No solution found at radius = {r}")

# Export if feasible solution is found
output_path = None
if solution:
    output_path = "Sol_Instance_12.vrp"
    generate_lkh3_vrp_file_from_solution(solution, output_path)
    print(f"✅ Final radius used: {selected_radius}")
    print(f"📦 VRP file written to: {output_path}")
else:
    print("❌ No feasible solution found for any radius.")
