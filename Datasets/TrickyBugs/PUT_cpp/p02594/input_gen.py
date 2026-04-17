import sys
import os
import random
import argparse

def generate_one(seed_offset):
    random.seed(seed_offset)
    X = random.randint(-40, 40)
    return f"{X}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_one(args.seed + i)
        filepath = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filepath, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
