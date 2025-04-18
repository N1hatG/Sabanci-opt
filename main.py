#!/usr/bin/env python

import sys
from model import *
import CoveringSolver
from generate_vrp import generate_lkh3_vrp_file_from_solution  # NEW: import the generator

def main(radius=10, filename='Instance_0.txt'):
    filepath = "instances/" + filename  # NEW: construct full path
    model = ProblemModel.from_file(filepath)
    print(model)

    if 0:  # this block stays untouched
        given_sol = {}
        given_sol[13] = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 19, 20]
        given_sol[16] = [7, 8, 9, 17, 18]
        given_sol[13] = [u - 1 for u in given_sol[13]]
        given_sol[16] = [u - 1 for u in given_sol[16]]
        example_solution = FirstSolution(given_sol, model)
        example_solution.print_sol()

    print(f"Running covering solver with r={radius}")
    left_rad = 1
    right_rad = 10**5
    lb = 0
    if len(sys.argv) >= 4:
        lb = float(sys.argv[3])
        print(f'Using lb={lb}')
        
    res = CoveringSolver.solve_to_optimality(model, radius)
    if res:
        print('###Relaxation solved, distributing cities')
        if CoveringSolver.solve_distribute_cities(res):
            # NEW: Generate VRP file if distribution is successful
            instance_id = ''.join(filter(str.isdigit, filename))
            output_path = f"Sol_Instance_{instance_id}.vrp"
            generate_lkh3_vrp_file_from_solution(res, output_path)
        else:
            print("❌ Distribution failed — solution not feasible under capacity constraints.")
    else:
        print('No sol')

    while 0:
        res = CoveringSolver.solve_capacity_removed(model, radius)
        if not res:
            radius *= 1.1
            continue
        if CoveringSolver.solve_distribute_cities(res):
            break
        else:
            radius += 1

if __name__ == '__main__':
    rad = 0
    if len(sys.argv) <= 1:
        rad = float(input("Please enter radius: "))
    else:
        rad = float(sys.argv[1])
    filename = ''
    if len(sys.argv) <= 2:
        filename = input("Enter instance file name (e.g. Instance_6.txt): ")
    else:
        filename = sys.argv[2]

    main(radius=rad, filename=filename)

    if 0:  # stays untouched
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('filename', required=True)
