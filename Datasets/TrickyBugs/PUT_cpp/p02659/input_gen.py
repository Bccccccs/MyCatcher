import sys
import os
import random
import argparse

def generate_one(rng):
    # Generate A in [0, 10^15]
    max_A = 10**15
    # Use a distribution that includes edge cases
    choice = rng.random()
    if choice < 0.1:
        A = 0
    elif choice < 0.2:
        A = max_A
    elif choice < 0.4:
        A = rng.randint(0, 100)
    elif choice < 0.6:
        A = rng.randint(10**9, 10**12)
    else:
        A = rng.randint(0, max_A)
    
    # Generate B in [0, 9.99] with exactly two decimal places
    # B < 10, so integer part 0-9, decimal part 00-99
    int_part = rng.randint(0, 9)
    dec_part = rng.randint(0, 99)
    # Ensure B < 10: if int_part == 9, dec_part must be <= 99 (always true)
    B = f"{int_part}.{dec_part:02d}"
    
    return f"{A} {B}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    rng = random.Random(args.seed)
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_one(rng)
        filename = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filename, 'w') as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
