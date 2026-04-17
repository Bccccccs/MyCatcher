import sys
import os
import random
import argparse

def generate_one(rand):
    # A and B between 1 and 16 inclusive, A+B <= 16
    total = rand.randint(2, 16)  # at least 2 because both >=1
    A = rand.randint(1, total - 1)
    B = total - A
    # Ensure A <= 16, B <= 16 (already true because total <=16)
    # But we must also ensure A>=1, B>=1 (already by construction)
    return A, B

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    for i in range(args.num):
        A, B = generate_one(random)
        with open(os.path.join(args.out_dir, f'test_{i:03d}.in'), 'w') as f:
            f.write(f'{A} {B}\n')

if __name__ == '__main__':
    main()
