import sys
import os
import random

def generate_input(n, k, rng):
    return f"{n} {k}"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    for idx in range(args.num):
        # n in [1, 50]
        n = rng.randint(1, 50)
        # k in [0, n^2]
        max_k = n * n
        k = rng.randint(0, max_k)
        content = generate_input(n, k, rng)
        with open(os.path.join(args.out_dir, f"test_{idx:03d}.in"), "w") as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
