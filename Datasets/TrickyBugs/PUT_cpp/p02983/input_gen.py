import sys
import os
import random

def generate_one(rand, L_max, R_max):
    # Constraints: 0 <= L < R <= 2e9
    # We'll generate L and R ensuring L < R and within bounds.
    # To cover various cases, we sometimes make interval small, sometimes large.
    choice = rand.randint(1, 10)
    if choice <= 3:
        # Small interval, possibly within 2019
        R = rand.randint(1, min(5000, R_max))
        L = rand.randint(0, R - 1)
    elif choice <= 6:
        # Large interval, but maybe L close to R
        R = rand.randint(1000000, R_max)
        L = rand.randint(max(0, R - 5000), R - 1)
    else:
        # Random general case
        R = rand.randint(1, R_max)
        L = rand.randint(0, R - 1)
    return L, R

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    L_max = 2_000_000_000
    R_max = 2_000_000_000

    for idx in range(args.num):
        L, R = generate_one(random, L_max, R_max)
        fname = os.path.join(args.out_dir, f'test_{idx:03d}.in')
        with open(fname, 'w') as f:
            f.write(f'{L} {R}\n')

if __name__ == '__main__':
    main()
