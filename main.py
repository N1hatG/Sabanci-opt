#!/usr/bin/env python

import sys
import argparse 
from model import *
import CoveringSolver
import generate_vrp

def main(radius = 10, filename='instances/Instance_0.txt'):
    model = ProblemModel.from_file(filename)
    print(model)
    if 0:
        res = CoveringSolver.solve_to_optimality(model, radius)
        print("Opt sol found!")
        return

if __name__ == '__main__':
    rad = 0
    if len(sys.argv) <= 1:
        rad = float(input("Please enter radius: "))
    else:
        rad = float(sys.argv[1])
    filename = ''
    if len(sys.argv) <= 2:
        filename = input("Enter file path: ")
    else:
        filename = sys.argv[2]
    main(radius=rad, filename=filename)
    if 0:    
        parser = argparse.ArgumentParser()
        parser.add_argument('filename', required=True)