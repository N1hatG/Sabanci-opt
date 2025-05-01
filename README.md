# Optimization Challenge 2025 – Healthcare Unit Deployment and Equipment Routing

This repository contains the full solution developed by our team for the **Optimization Challenge 2025**, organized by Sabancı University. Our implementation efficiently solves a two-stage problem involving the strategic deployment of healthcare units and the planning of equipment delivery routes.

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

---

## 🧩 Our Solution Approach

We implemented a modular pipeline in Python that includes:

- **Stage 1 Solvers (in `CoveringSolver.py`)**:
  - `solve_given_r`: Checks feasibility for a given radius.
  - `solve_to_optimality`: Finds optimal health center placement minimizing maximum distance.
  - `solve_capacity_removed`: A fast approximation version for heuristics.
  - `solve_capacity_removed_withz`: Score-guided center selection to diversify solutions.

- **Stage 2 Planner (via `generate_vrp.py` + `LKH-3`)**:
  - Converts Stage 1 results to `.vrp` format.
  - Runs LKH-3 on `.par` file for optimized CVRP.
  - Parses and validates the output.

- **Pipeline Scripts**:
  - `manualsolver.py`: Runs the pipeline manually.
  - `heuristicsolver.py`: Automates iterative heuristic-based solving.
  - `longtester.py`: Finds minimum feasible radius and routes it.
  - `main.py`: Minimal script for custom runs.

---

## 🗂 Directory Structure

```
.
├── algos.py                  # Utilities for radius filtering
├── CoveringSolver.py         # Gurobi models for Stage 1
├── generate_vrp.py           # VRP converter and LKH output parser
├── heuristicsolver.py        # Full solver with heuristic loop
├── longtester.py             # Iteratively checks feasible radius
├── main.py                   # Minimal execution pipeline
├── manualsolver.py           # Manual run with LKH toggle
├── model.py                  # Data structures and feasibility checks
├── instances/                # Input data (not included here)
├── solutions/                # Output files for solved instances
├── optchall_25.pdf           # Original challenge description
```

---

## 🧪 How to Run

### Install Requirements
```bash
pip install gurobipy
# Ensure LKH executable is in the project root
chmod +x ./LKH
```

### Run the Heuristic Solver
```bash
python heuristicsolver.py <instance_id> <starting_radius>
```

### Run LongTester (Binary Search Style)
```bash
python longtester.py <instance_id> [start_radius]
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

## 🏁 Evaluation Criteria (per Sabancı Guidelines)

1. Minimize maximum population-weighted distance
2. Minimize total routing distance
3. Minimize number of delivery routes

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
- **[Teammate's Name Here]** – [Affiliation, optional]

---

## 📬 Contact

For questions about the challenge:
- 📧 opt-challenge@sabanciuniv.edu

For technical details:
- 🔗 https://github.com/N1hatG
- 🔗 https://github.com/Agoraaa

---