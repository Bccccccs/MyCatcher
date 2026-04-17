import sys
import os
import random
import math
import argparse

MOD = 10**9 + 7

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

def generate_input(N, out_dir, idx):
    filename = os.path.join(out_dir, f"test_{idx:03d}.in")
    with open(filename, 'w') as f:
        f.write(f"{N}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    max_N = 1000
    primes = sieve_primes(max_N)

    for i in range(args.num):
        # Generate N with distribution favoring larger values for stress tests
        r = random.random()
        if r < 0.3:
            N = random.randint(1, 10)
        elif r < 0.6:
            N = random.randint(10, 100)
        elif r < 0.9:
            N = random.randint(100, 500)
        else:
            N = random.randint(500, max_N)
        generate_input(N, args.out_dir, i)

if __name__ == "__main__":
    main()
