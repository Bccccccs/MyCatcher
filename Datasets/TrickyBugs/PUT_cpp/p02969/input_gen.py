import sys
import os
import random
import argparse

def generate_input(r):
    return f"{r}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        r = random.randint(1, 100)
        content = generate_input(r)
        filename = os.path.join(args.out_dir, f"test_{i+1:03d}.in")
        with open(filename, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
