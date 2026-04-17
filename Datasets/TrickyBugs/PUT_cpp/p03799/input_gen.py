import sys
import os
import random
import argparse

def generate_one(rand, constraints):
    N_max = constraints['N_max']
    M_max = constraints['M_max']
    N = rand.randint(1, N_max)
    M = rand.randint(1, M_max)
    return f"{N} {M}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    rand = random.Random(args.seed)

    constraints = {
        'N_max': 10**12,
        'M_max': 10**12
    }

    for i in range(args.num):
        content = generate_one(rand, constraints)
        filename = os.path.join(args.out_dir, f"test_{i+1:03d}.in")
        with open(filename, 'w') as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
