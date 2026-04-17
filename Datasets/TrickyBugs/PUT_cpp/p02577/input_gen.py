import sys
import os
import random
import argparse

def generate_test_case(rng):
    # Choose length up to 200000 digits
    # Use distribution: sometimes small, sometimes huge
    choice = rng.random()
    if choice < 0.3:
        # Small numbers (0-1000)
        length = rng.randint(1, 4)
    elif choice < 0.6:
        # Medium numbers (up to 10000 digits)
        length = rng.randint(5, 10000)
    elif choice < 0.9:
        # Large numbers (up to 100000 digits)
        length = rng.randint(10001, 100000)
    else:
        # Very large numbers (up to 200000 digits)
        length = rng.randint(100001, 200000)
    
    # Generate digits
    digits = []
    # First digit cannot be 0 unless length == 1 (for N=0 case)
    if length == 1:
        digits.append(str(rng.randint(0, 9)))
    else:
        digits.append(str(rng.randint(1, 9)))
        for _ in range(length - 1):
            digits.append(str(rng.randint(0, 9)))
    
    # Convert to string
    n_str = ''.join(digits)
    
    # Special cases: ensure 0 appears sometimes
    if rng.random() < 0.01:
        n_str = "0"
    
    return n_str

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    rng = random.Random(args.seed)
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        n_str = generate_test_case(rng)
        filename = os.path.join(args.out_dir, f'test_{i:03d}.in')
        with open(filename, 'w') as f:
            f.write(n_str + '\n')

if __name__ == '__main__':
    main()
