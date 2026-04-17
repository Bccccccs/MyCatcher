import sys
import os
import random
import argparse

def generate_test_input(N, out_dir, idx):
    filename = os.path.join(out_dir, f"test_{idx:03d}.in")
    with open(filename, 'w') as f:
        f.write(f"{N}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    # Precompute all possible withdrawable amounts
    amounts = [1]
    # Powers of 6
    p = 6
    while p <= 100000:
        amounts.append(p)
        p *= 6
    # Powers of 9
    p = 9
    while p <= 100000:
        amounts.append(p)
        p *= 9
    amounts = sorted(set(amounts))
    
    # Generate N values with varied difficulty
    for i in range(args.num):
        # Mix different types of N:
        # 1. Small random
        # 2. Large random
        # 3. Edge cases
        choice = random.random()
        if choice < 0.3:
            N = random.randint(1, 1000)
        elif choice < 0.6:
            N = random.randint(1000, 50000)
        elif choice < 0.8:
            N = random.randint(50000, 100000)
        else:
            # Edge cases: exact powers or combinations
            if random.random() < 0.5:
                # Exact power
                N = random.choice(amounts)
            else:
                # Sum of few powers
                N = 0
                for _ in range(random.randint(2, 5)):
                    N += random.choice(amounts)
                N = min(N, 100000)
        
        # Ensure within bounds
        N = max(1, min(N, 100000))
        generate_test_input(N, args.out_dir, i)

if __name__ == "__main__":
    main()
