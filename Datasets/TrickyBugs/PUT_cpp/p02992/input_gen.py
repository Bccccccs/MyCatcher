import sys
import os
import random
import argparse

MOD = 10**9 + 7

def generate_test(N, K):
    return f"{N} {K}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    for idx in range(args.num):
        # Generate N and K according to constraints
        # N in [1, 1e9], K in [2, 100]
        N = random.randint(1, 10**9)
        K = random.randint(2, 100)
        
        # Ensure some variety: sometimes small N, sometimes large
        if random.random() < 0.3:
            N = random.randint(1, 1000)
        elif random.random() < 0.6:
            N = random.randint(1, 10**6)
        
        # Ensure some edge cases appear occasionally
        if idx == 0:
            N, K = 3, 2  # example 1
        elif idx == 1:
            N, K = 10, 3  # example 2
        elif idx == 2:
            N, K = 314159265, 35  # example 3
        elif idx == 3:
            N, K = 1, 2  # minimal N
        elif idx == 4:
            N, K = 10**9, 100  # maximal N, maximal K
        elif idx == 5:
            N, K = 10**9, 2  # maximal N, minimal K
        elif idx == 6:
            N, K = 1, 100  # minimal N, maximal K
        
        content = generate_test(N, K)
        filename = os.path.join(args.out_dir, f"test_{idx:03d}.in")
        with open(filename, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
