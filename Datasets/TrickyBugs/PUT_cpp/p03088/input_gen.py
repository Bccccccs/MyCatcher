import sys
import os
import random
import argparse

MOD = 10**9 + 7
CHARS = ['A', 'C', 'G', 'T']
CHAR_TO_IDX = {'A': 0, 'C': 1, 'G': 2, 'T': 3}

def generate_input(N):
    return f"{N}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    for i in range(args.num):
        N = random.randint(3, 100)
        content = generate_input(N)
        with open(os.path.join(args.out_dir, f"test_{i:03d}.in"), 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
