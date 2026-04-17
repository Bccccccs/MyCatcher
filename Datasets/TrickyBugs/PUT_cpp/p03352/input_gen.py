import sys
import os
import random
import math
import argparse

def is_perfect_power(n):
    if n <= 1:
        return True
    max_p = int(math.log2(n)) + 1
    for p in range(2, max_p + 1):
        b = int(round(n ** (1.0 / p)))
        if b < 1:
            continue
        if b ** p == n or (b-1) ** p == n or (b+1) ** p == n:
            return True
    return False

def largest_perfect_power_upto(x):
    for n in range(x, 0, -1):
        if is_perfect_power(n):
            return n
    return 1

def generate_one(seed_val):
    random.seed(seed_val)
    return random.randint(1, 1000)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        x = generate_one(args.seed + i * 10007)
        with open(os.path.join(args.out_dir, f'test_{i:03d}.in'), 'w') as f:
            f.write(f'{x}\n')

if __name__ == '__main__':
    main()
