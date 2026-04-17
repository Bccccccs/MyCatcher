import sys
import random
import os
import argparse

MOD = 10**9 + 7

def mod_pow(a, e, mod):
    res = 1
    while e:
        if e & 1:
            res = res * a % mod
        a = a * a % mod
        e >>= 1
    return res

def solve_slow(N, K):
    total = 0
    for g in range(1, K + 1):
        cnt = pow(K // g, N, MOD)
        total = (total + g * cnt) % MOD
    return total

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
        # Generate N and K within constraints
        # We'll generate a mix of small, medium, and large tests
        r = random.random()
        if r < 0.2:  # small tests
            N = random.randint(2, 10)
            K = random.randint(1, 10)
        elif r < 0.4:  # medium tests
            N = random.randint(10, 100)
            K = random.randint(10, 100)
        elif r < 0.6:  # larger but still moderate
            N = random.randint(100, 1000)
            K = random.randint(100, 1000)
        elif r < 0.8:  # near upper bound but not max
            N = random.randint(50000, 100000)
            K = random.randint(50000, 100000)
        else:  # random across full range
            N = random.randint(2, 100000)
            K = random.randint(1, 100000)
        
        content = generate_test(N, K)
        filename = os.path.join(args.out_dir, f"test_{idx:03d}.in")
        with open(filename, 'w') as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
