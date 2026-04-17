import sys
import random
import os
import argparse


SPECIAL_CASES = [
    (5, 5, 7),
    (5, 7, 5),
    (7, 5, 5),
    (7, 7, 5),
    (1, 1, 1),
    (10, 10, 10),
    (1, 5, 10),
    (4, 6, 8),
]


def generate_one(rand, index):
    if index < len(SPECIAL_CASES):
        a, b, c = SPECIAL_CASES[index]
    else:
        a = rand.randint(1, 10)
        b = rand.randint(1, 10)
        c = rand.randint(1, 10)
    return f"{a} {b} {c}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    rand = random.Random(args.seed)
    
    for i in range(args.num):
        content = generate_one(rand, i)
        filename = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filename, 'w') as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
