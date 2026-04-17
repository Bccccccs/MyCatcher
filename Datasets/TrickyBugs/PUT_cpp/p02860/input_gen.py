import sys
import os
import random
import argparse

def generate_one(seed, idx):
    rng = random.Random(seed + idx)
    N = rng.randint(1, 100)
    if N % 2 == 1:
        # odd length -> cannot be double
        letters = [rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(N)]
        S = ''.join(letters)
    else:
        half = N // 2
        first_half = [rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(half)]
        if rng.random() < 0.5:
            # make it a double
            S = ''.join(first_half) * 2
        else:
            # make it not a double
            second_half = [rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(half)]
            # ensure they are different
            while second_half == first_half:
                second_half = [rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(half)]
            S = ''.join(first_half + second_half)
    return f"{N}\n{S}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    for i in range(args.num):
        content = generate_one(args.seed, i)
        with open(os.path.join(args.out_dir, f"test_{i:03d}.in"), 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
