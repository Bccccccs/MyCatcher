import sys
import os
import random
import argparse

def generate_one(rand):
    N = rand.randint(1, 100)
    K = rand.randint(1, 100)
    return f"{N} {K}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    rand = random.Random(args.seed)

    for i in range(args.num):
        content = generate_one(rand)
        filepath = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filepath, 'w') as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
