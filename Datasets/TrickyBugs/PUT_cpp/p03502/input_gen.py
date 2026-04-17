import sys
import os
import random
import argparse

def generate_input(seed_offset, case_num):
    rng = random.Random(seed_offset + case_num)
    
    # Generate N according to constraints: 1 <= N <= 10^8
    # We'll generate with various distributions to cover different cases
    
    choice = rng.random()
    if choice < 0.2:
        # Small numbers (1-100)
        N = rng.randint(1, 100)
    elif choice < 0.4:
        # Medium numbers (100-10^4)
        N = rng.randint(100, 10**4)
    elif choice < 0.6:
        # Large numbers (10^4-10^6)
        N = rng.randint(10**4, 10**6)
    elif choice < 0.8:
        # Very large numbers (10^6-10^8)
        N = rng.randint(10**6, 10**8)
    else:
        # Edge cases: powers of 10, numbers near boundaries
        edges = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000]
        N = rng.choice(edges)
        if rng.random() < 0.5:
            N = rng.randint(max(1, N-100), min(10**8, N+100))
    
    # Ensure N is within bounds
    N = max(1, min(10**8, N))
    
    return f"{N}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_input(args.seed, i)
        filename = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filename, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
