import sys
import os
import random
import math
from collections import Counter

def prime_factorize_factorial(n):
    """Return prime factorization of n! as dict {prime: exponent}"""
    primes = []
    is_prime = [True] * (n + 1)
    for i in range(2, n + 1):
        if is_prime[i]:
            primes.append(i)
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    
    fact_exp = {}
    for p in primes:
        exp = 0
        power = p
        while power <= n:
            exp += n // power
            power *= p
        fact_exp[p] = exp
    return fact_exp

def count_shichigo(fact_exp):
    """Count divisors of N! that have exactly 75 divisors"""
    # 75 = 3 * 5 * 5 = 75
    # Possible exponent patterns (a+1)*(b+1)*... = 75
    patterns = [
        (74,),                     # 75 = 75
        (24, 2),                   # 75 = 25 * 3
        (14, 4),                   # 75 = 15 * 5
        (4, 4, 2),                 # 75 = 5 * 5 * 3
        (2, 2, 2, 2),              # 75 = 3 * 5 * 5 (as 3,5,5 but exponents are +1)
    ]
    # Convert to exponent requirements (a,b,c,...) where each is >=1
    # Actually we need (e1+1)*(e2+1)*... = 75
    # Let's generate all multiplicative partitions of 75 into factors >1
    def factorizations(x, start=2):
        if x == 1:
            yield []
        for i in range(start, int(math.isqrt(x)) + 1):
            if x % i == 0:
                for rest in factorizations(x // i, i):
                    yield [i] + rest
        if x >= start:
            yield [x]
    
    factor_list = list(factorizations(75))
    patterns = []
    for facs in factor_list:
        # facs are the (e_i+1) values
        exps = [f - 1 for f in facs]
        exps.sort(reverse=True)
        patterns.append(tuple(exps))
    
    # Remove duplicates
    patterns = list(set(patterns))
    
    primes = sorted(fact_exp.keys())
    exp_vals = [fact_exp[p] for p in primes]
    m = len(primes)
    
    def count_for_pattern(pattern):
        # pattern is tuple of required exponents (each >=0)
        k = len(pattern)
        # We need to choose k distinct primes from available primes
        # and assign each chosen prime an exponent >= pattern[i]
        # but <= available exponent in fact_exp
        
        # Sort pattern descending
        pat = sorted(pattern, reverse=True)
        
        # DP over primes
        # dp[t][j] = ways to satisfy first t pattern positions using first j primes
        # Actually we need to count assignments of primes to pattern positions
        # Since primes are distinguishable, we can assign via combinatorics
        
        # For each pattern position i, we need a prime with exponent >= pat[i]
        # Count how many primes have exponent >= val for each val
        available = []
        for val in pat:
            cnt = sum(1 for e in exp_vals if e >= val)
            available.append(cnt)
        
        # Now we need number of ways to assign distinct primes to positions
        # such that position i gets a prime with exponent >= pat[i]
        # This is like counting injections with constraints
        # Sort pat descending, then available counts are non-increasing
        # Number of ways = product_{i=0..k-1} (available[i] - i)
        # provided available[i] > i for all i
        ways = 1
        for i in range(k):
            if available[i] <= i:
                return 0
            ways *= (available[i] - i)
        return ways
    
    total = 0
    for pat in patterns:
        total += count_for_pattern(pat)
    return total

def generate_input(N):
    """Return string containing single test case"""
    return f"{N}\n"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    # Precompute for all N up to 100
    max_N = 100
    all_fact_exp = [None] * (max_N + 1)
    for n in range(1, max_N + 1):
        all_fact_exp[n] = prime_factorize_factorial(n)
    
    # We'll generate random N values
    for i in range(args.num):
        # Generate N with some distribution
        # Let's make some small, some medium, some large
        r = random.random()
        if r < 0.2:
            N = random.randint(1, 20)
        elif r < 0.5:
            N = random.randint(21, 50)
        elif r < 0.8:
            N = random.randint(51, 80)
        else:
            N = random.randint(81, 100)
        
        content = generate_input(N)
        filename = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filename, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
