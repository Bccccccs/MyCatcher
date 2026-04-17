import sys
import os
import random
import argparse

def generate_one(seed_offset):
    rng = random.Random(seed_offset)
    # choose which one will be the unique one: 0,1,2
    unique_pos = rng.randint(0, 2)
    # choose the value for the unique one
    unique_val = rng.randint(-100, 100)
    # choose the value for the pair
    pair_val = rng.randint(-100, 100)
    # ensure they are different
    while pair_val == unique_val:
        pair_val = rng.randint(-100, 100)
    
    vals = [pair_val, pair_val, pair_val]
    vals[unique_pos] = unique_val
    
    return f"{vals[0]} {vals[1]} {vals[2]}"

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
            f.write(content + "\n")

if __name__ == "__main__":
    main()
