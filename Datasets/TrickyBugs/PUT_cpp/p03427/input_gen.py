import sys
import random
import os
import argparse

def max_digit_sum(n_str):
    # Convert to list of digits
    digits = list(map(int, n_str))
    L = len(digits)
    
    # Try all positions where we decrease a digit
    best = sum(digits)  # candidate: N itself
    
    for i in range(L):
        if digits[i] == 0:
            continue
        # Decrease digit at position i by 1
        new_digits = digits[:]
        new_digits[i] -= 1
        # Set all following digits to 9
        for j in range(i+1, L):
            new_digits[j] = 9
        candidate = sum(new_digits)
        if candidate > best:
            best = candidate
    return best

def generate_one(seed_val):
    rng = random.Random(seed_val)
    # Generate N in [1, 1e16]
    # We'll generate random length and random digits
    # Choose length between 1 and 17 (since 10^16 has 17 digits)
    length = rng.randint(1, 17)
    if length == 1:
        N = rng.randint(1, 9)
    else:
        if length == 17:
            # For 17 digits, first digit must be 1 (since max is 10^16)
            first = 1
        else:
            first = rng.randint(1, 9)
        other_digits = [rng.randint(0, 9) for _ in range(length-1)]
        # Ensure not all zero for length>1? Actually fine.
        digits = [first] + other_digits
        N = int(''.join(map(str, digits)))
        # Ensure N <= 10^16
        if N > 10**16:
            N = 10**16
    return str(N)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    rng = random.Random(args.seed)
    
    for i in range(args.num):
        seed_val = rng.randint(0, 2**63 - 1)
        N_str = generate_one(seed_val)
        with open(os.path.join(args.out_dir, f'test_{i:03d}.in'), 'w') as f:
            f.write(N_str + '\n')

if __name__ == '__main__':
    main()
