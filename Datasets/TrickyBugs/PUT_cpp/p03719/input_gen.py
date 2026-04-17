import sys
import os
import random
import argparse

def generate_one(rand):
    A = rand.randint(-100, 100)
    B = rand.randint(-100, 100)
    C = rand.randint(-100, 100)
    return f"{A} {B} {C}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_one(random)
        filename = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filename, 'w') as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
