import sys
import random
import argparse
import os

def generate_one(rand, constraints):
    N = rand.randint(1, constraints['N_max'])
    A = [rand.randint(1, constraints['A_max']) for _ in range(N)]
    return N, A

def write_test(fname, N, A):
    with open(fname, 'w') as f:
        f.write(f"{N}\n")
        f.write(" ".join(map(str, A)) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    constraints = {'N_max': 200, 'A_max': 10**9}

    for idx in range(args.num):
        N, A = generate_one(random, constraints)
        fname = os.path.join(args.out_dir, f"test_{idx:03d}.in")
        write_test(fname, N, A)

if __name__ == "__main__":
    main()
