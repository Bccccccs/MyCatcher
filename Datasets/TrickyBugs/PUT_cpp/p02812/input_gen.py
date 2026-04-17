import sys
import os
import random
import argparse

def generate_one(seed_offset, n=None):
    rng = random.Random(seed_offset)
    if n is None:
        n = rng.randint(3, 50)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    s = ''.join(rng.choice(letters) for _ in range(n))
    return f"{n}\n{s}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    rng = random.Random(args.seed)

    for i in range(args.num):
        content = generate_one(rng.randint(0, 10**9))
        out_path = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(out_path, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
