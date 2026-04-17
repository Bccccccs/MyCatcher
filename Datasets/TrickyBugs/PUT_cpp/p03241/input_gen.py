import sys
import os
import random
import math
import argparse

def generate_one(seed, idx):
    rng = random.Random(seed + idx * 10007)
    
    # Choose N in [1, 1e5] but we can bias toward interesting cases
    # Use a mix: sometimes small, sometimes large, sometimes near M
    choice = rng.random()
    if choice < 0.3:
        N = rng.randint(1, 100)
    elif choice < 0.6:
        N = rng.randint(100, 10000)
    elif choice < 0.9:
        N = rng.randint(10000, 100000)
    else:
        N = 100000
    
    # Ensure N <= M, M up to 1e9
    # Choose M >= N
    # Let's pick M in [N, 1e9] with some distribution
    m_choice = rng.random()
    if m_choice < 0.3:
        # M close to N
        M = rng.randint(N, min(N + 100, 10**9))
    elif m_choice < 0.6:
        # M moderately larger
        max_range = min(N * 100, 10**9)
        M = rng.randint(N, max_range)
    elif m_choice < 0.9:
        # M large but not huge
        lower = max(N, 10**7)
        M = rng.randint(lower, 10**9)
    else:
        # M huge, near 1e9
        M = rng.randint(10**8, 10**9)
    
    # Ensure N <= M
    if M < N:
        M = N
    
    return f"{N} {M}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_one(args.seed, i)
        filepath = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filepath, 'w') as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
