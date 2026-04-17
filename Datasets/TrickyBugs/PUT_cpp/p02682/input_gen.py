import sys
import os
import random

def generate_one(seed_offset):
    # Constraints: 0 <= A, B, C; 1 <= K <= A+B+C <= 2e9
    # We'll generate A+B+C first, then distribute into A,B,C, then choose K.
    total_cards = random.randint(1, 2_000_000_000)
    # Distribute total_cards into A,B,C (non‑negative)
    # Use random multinomial‑like distribution
    x = random.randint(0, total_cards)
    y = random.randint(0, total_cards - x)
    z = total_cards - x - y
    # Permute to assign to A,B,C randomly
    arr = [x, y, z]
    random.shuffle(arr)
    A, B, C = arr
    K = random.randint(1, total_cards)
    return A, B, C, K

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    for i in range(args.num):
        A, B, C, K = generate_one(i)
        with open(os.path.join(args.out_dir, f'test_{i:03d}.in'), 'w') as f:
            f.write(f'{A} {B} {C} {K}\n')

if __name__ == '__main__':
    main()
