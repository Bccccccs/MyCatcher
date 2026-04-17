import sys
import random
import argparse
import os

def generate_input(seed_offset, main_seed):
    rng = random.Random(main_seed + seed_offset)
    
    # Generate K first because it's small and used for N's upper bound if needed
    K = rng.randint(2, 10)
    
    # Generate N with distribution that covers edge cases
    choice = rng.random()
    if choice < 0.2:  # Small N
        N = rng.randint(1, 100)
    elif choice < 0.4:  # Near powers of K
        max_power = 0
        while K ** (max_power + 1) <= 10**9:
            max_power += 1
        if max_power > 0:
            power = rng.randint(0, max_power)
            base = K ** power
            if power == 0:
                N = rng.randint(1, K - 1)
            else:
                N = rng.randint(base, min(base * K - 1, 10**9))
        else:
            N = rng.randint(1, 10**9)
    elif choice < 0.6:  # Random in full range
        N = rng.randint(1, 10**9)
    elif choice < 0.8:  # Edge: N = 1
        N = 1
    else:  # Edge: N = 10^9
        N = 10**9
    
    return f"{N} {K}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_input(i, args.seed)
        with open(os.path.join(args.out_dir, f"test_{i:03d}.in"), "w") as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
