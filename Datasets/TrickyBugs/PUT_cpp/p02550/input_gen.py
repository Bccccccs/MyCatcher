import sys
import os
import random
import math

def generate_one(rand, constraints):
    N_max, X_max, M_max = constraints
    
    # Decide N type: small, medium, large, or huge
    r = rand.random()
    if r < 0.3:
        N = rand.randint(1, min(1000, N_max))
    elif r < 0.6:
        N = rand.randint(1000, min(10**6, N_max))
    elif r < 0.9:
        N = rand.randint(10**6, min(10**9, N_max))
    else:
        N = rand.randint(10**9, N_max)
    
    M = rand.randint(1, M_max)
    X = rand.randint(0, M-1)
    
    return N, X, M

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    constraints = (10**10, 10**5, 10**5)
    
    for idx in range(args.num):
        N, X, M = generate_one(random, constraints)
        filename = os.path.join(args.out_dir, f'test_{idx:03d}.in')
        with open(filename, 'w') as f:
            f.write(f'{N} {X} {M}\n')

if __name__ == '__main__':
    main()
