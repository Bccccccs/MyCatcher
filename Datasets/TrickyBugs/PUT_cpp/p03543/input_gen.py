import sys
import os
import random
import argparse

def generate_one(seed_offset):
    rng = random.Random(seed_offset)
    n = rng.randint(1000, 9999)
    return f"{n}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_one(args.seed + i)
        with open(os.path.join(args.out_dir, f"test_{i:03d}.in"), "w") as f:
            f.write(content)

if __name__ == "__main__":
    main()
