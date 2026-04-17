import sys
import os
import random
import argparse

def generate_one(rand, constraints):
    N_min, N_max = constraints['N']
    i_min, i_max = constraints['i']
    
    N = rand.randint(N_min, N_max)
    i = rand.randint(i_min, min(i_max, N))
    return f"{N} {i}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    constraints = {
        'N': (1, 100),
        'i': (1, 100)
    }
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for idx in range(args.num):
        content = generate_one(random, constraints)
        filename = os.path.join(args.out_dir, f"test_{idx:03d}.in")
        with open(filename, 'w') as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
