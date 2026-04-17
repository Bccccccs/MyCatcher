import sys
import random
import argparse
import os

def generate_one(rand, constraints):
    N_min, N_max = constraints['N']
    a_min, a_max = constraints['a_i']
    N = rand.randint(N_min, N_max)
    a = [rand.randint(a_min, a_max) for _ in range(N)]
    return f"{N}\n" + " ".join(map(str, a))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    constraints = {
        'N': (1, 10**5),
        'a_i': (0, 10**5 - 1)
    }

    for idx in range(args.num):
        content = generate_one(random, constraints)
        filename = os.path.join(args.out_dir, f"test_{idx:03d}.in")
        with open(filename, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
