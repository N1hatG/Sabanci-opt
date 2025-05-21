# Optimization Challenge 2025 – Healthcare Unit Deployment and Equipment Routing

Made by [N1hatG](https://github.com/N1hatG/) and [Agoraaa](https://github.com/Agoraaa/)

This repository contains our, 3rd place winner, solution developed for the **[Optimization Challenge 2025](https://fens.sabanciuniv.edu/tr/opt-challenge)** competition, organized by Sabancı University. Our implementation efficiently solves a two-stage problem involving the strategic deployment of healthcare units and the planning of equipment delivery routes.

Please forgive the messy code, the final round's code was written in the span of 24 hours (and with lots of coffee) so we didn't have time to get rid of duplicate codes and form a cleaner architecture. Even though we can fix it right now, we'd like to keep the code's authenticity so we'll only change markdown files and file paths.

---

## 🧠 Problem Summary

The challenge is composed of two main stages:

### Stage 1: Healthcare Unit Deployment
- **Goal**: Deploy M healthcare units in N communities to minimize the **maximum population-weighted distance** any community must travel to reach its assigned center.
- **Constraints**:
  - Each community must be served.
  - Each center has a maximum capacity (`C`) it cannot exceed.

### Stage 2: Equipment Routing
- **Goal**: Route a fleet of ambulances (capacity `Q = 10000`) from a central depot to the healthcare units to minimize **total travel distance**.
- **Constraints**:
  - Each health center must be visited exactly once.
  - Distribution must not exceed the vehicle capacity.

In the final round, stage 2 was ditched and we were requested to solve stage 1 part, along with these additional constraints:
- **Fairness in Workload**: None of the healthcenters should be over- or under-utilized compared to other ones.
- **Equity in Access**: None of the individuals should have to travel very high or very low distances compared to others.

---

## 🧩 Our Solution Approach

We implemented a modular pipeline in Python that includes:

- **Stage 1 Solvers (in `CoveringSolver.py`)**:
  - `solve_to_optimality`: Finds optimal health center placement minimizing maximum distance. This is the exact solver probably everyone else used as well. We also use an `upper_bound` parameter to cut down lots of possible assignments.
  - `solve_given_r`: Instead of finding the optimal solution, finds *a* solution with the given `upper_bound` parameter. If a solution is found, it means that optimal solution is below the upper bound. If the problem comes out at infeasible instead, we know that optimal solution will be above the upper bound. These 2 facts mean that we can use binary search on the objective function and stop when there is only one solution in the given lower and upper limits. Most of the hard instances were solved using this method.
  - `solve_capacity_removed`: Solves the problem with the capacity constraints removed which turns the problem into a set covering problem. At this point we give up on finding the optimal solution and just try finding a feasible and good enough one.
  - `solve_distribute_cities`: Assigns communities to healthcenters, used right after using `solve_capacity_removed`
  - `solve_capacity_removed_withz`: Tries to find better set covering solutions (e.g each city is covered at least 2 times instead) to have a higher chance of getting feasible solutions in the city distribution part.

`finalsolver.py` has pretty much the same solvers but with added constraints of the final round problem. 

- **Stage 2 Planner (via `generate_vrp.py` + `LKH-3`)**:
We use LKH-3 algorithm developed by Keld Helsgaun to solve the CVRP. Note that a compiled version of the algorithm needs to be present in the main folder. It can be found [here](https://github.com/c4v4/LKH3).

  - Converts Stage 1 results to `.vrp` format.
  - Runs LKH-3 on `.par` file for optimized CVRP. 
  - Parses and validates the output.

- **Pipeline Scripts**:
  - `longtester.py`, `final_methods/longtester.py`: Finds optimum solution (and routes it).
  - `final_methods/longtester_nobeta.py`: Like `longtester.py`, but restricts the solution space so that beta constraint can be safely removed. None of the optimal solutions was ever outside this restricted solution space in the instances, so we can safely use this without worrying.
  - `manualsolver.py`, `final_methods/manualsolver.py`: Used to manually binary search optimal solution. We didn't need to automate it since each iteration would take 10-600 seconds. We also wouldn't be able to incorporate past solving times for selecting the next point.
  - `heuristicsolver.py`: Automates iterative heuristic-based solving.
  - `final_methods/genetic.py`: A bare-bones genetic algorithm. It technically does work but is highly inefficient.
  - `main.py`: Minimal script for custom runs.

---

## 🗂 Directory Structure

```
.
├── algos.py                             # Utilities for radius filtering
├── CoveringSolver.py                    # Gurobi models for Stage 1
├── generate_vrp.py                      # VRP converter and LKH output parser
├── heuristicsolver.py                   # Full solver with heuristic loop
├── longtester.py                        # Iteratively checks feasible radius
├── main.py                              # Minimal execution pipeline
├── manualsolver.py                      # Manual run with LKH toggle
├── model.py                             # Data structures and feasibility checks
├── instances/                           # Input data (not included here)
├── solutions/                           # Output files for solved instances
├── optchall_25.pdf                      # Original challenge description
├── finalsolvers.py                      # Final round solvers 
├──── final_methods/genetic.py           # Genetic algorithm solver
├──── final_methods/longtester.py        # Final version of longtester.py
├──── final_methods/longtester_nobeta.py # Relaxed version of longtester
├──── final_methods/manualsolver.py      # Final version of manualsolver.py
├──── final_methods/parser.py            # Solution parser
├── instances/                           # Problem instances
├── final_data/                          # Given final round files





```

---

## 🧪 How to Run

### Install Requirements
```bash
pip install gurobipy
# Ensure LKH executable is in the project root
chmod +x ./LKH
```

### Run LongTester
```bash
python longtester.py <instance_id> [start_radius]
```

### Run the Heuristic Solver
```bash
python heuristicsolver.py <instance_id> <starting_radius>
```

### Manual Execution
```bash
python manualsolver.py <instance_id> <radius> [run_lkh = 1]
```

---

## 📤 Outputs

All outputs are saved under:
```
solutions/<instance_id>/Sol_<instance_id>.txt
```

This file includes:
- Stage 1 assignment (center → communities)
- Stage 2 delivery routes and total travel distance

---

## 🛠 Technologies Used

- **Python 3.9+**
- **Gurobi Optimizer** for MIP modeling
- **LKH-3** for Capacitated Vehicle Routing Problem
- Custom parsing and VRP formatting tools

---

## 👨‍👩‍👧‍👦 Team

Developed by:
- **Nihat Guliyev** – AI Engineering @ Hacettepe University
- **Agoraaa** – Someone similar

---

## 📬 Contact

For technical details:
- 🔗 https://github.com/N1hatG
- 🔗 https://github.com/Agoraaa

---