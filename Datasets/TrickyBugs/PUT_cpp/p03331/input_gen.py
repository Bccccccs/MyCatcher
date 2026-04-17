import sys
import os
import random
import argparse

def generate_input(N):
    return f"{N}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        # Generate N in [2, 100000]
        # Use various distributions to cover edge cases
        choice = random.random()
        if choice < 0.2:
            # small numbers
            N = random.randint(2, 100)
        elif choice < 0.4:
            # around powers of 10
            exp = random.randint(1, 5)
            base = 10 ** exp
            offset = random.randint(-50, 50)
            N = max(2, min(100000, base + offset))
        elif choice < 0.6:
            # random in full range
            N = random.randint(2, 100000)
        elif choice < 0.8:
            # numbers with many 9s
            digits = random.randint(1, 5)
            N = int('9' * digits)
            if N > 100000:
                N = 99999
            N = max(2, N)
        else:
            # edge cases: 2, 100000, and numbers just below powers of 10
            candidates = [2, 100000, 99999, 100, 9999, 10000]
            N = random.choice(candidates)
        
        content = generate_input(N)
        filename = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filename, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
