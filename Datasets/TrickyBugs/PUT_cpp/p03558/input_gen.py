import sys
import random
import os
import argparse

def generate_one(seed_val, idx):
    random.seed(seed_val + idx)
    # K between 2 and 100000
    # We want variety: small, medium, large, edge cases
    r = random.random()
    if r < 0.2:
        # small K
        K = random.randint(2, 100)
    elif r < 0.4:
        # medium K
        K = random.randint(101, 5000)
    elif r < 0.6:
        # large K
        K = random.randint(5001, 50000)
    elif r < 0.8:
        # very large K
        K = random.randint(50001, 99999)
    else:
        # edge: near upper bound
        K = random.randint(99900, 100000)
    return f"{K}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_one(args.seed, i)
        filename = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filename, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
