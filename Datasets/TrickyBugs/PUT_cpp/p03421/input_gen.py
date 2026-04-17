import sys
import os
import random

def generate_permutation(N, A, B):
    if A * B < N or A + B > N + 1:
        return None
    
    result = []
    remaining = N
    for i in range(B):
        take = min(A, remaining - (B - i - 1))
        if take <= 0:
            return None
        block = list(range(remaining - take + 1, remaining + 1))
        result.extend(block)
        remaining -= take
    
    if len(result) != N:
        return None
    return result

def generate_test(N, A, B):
    if A * B < N or A + B > N + 1:
        return "-1"
    
    perm = generate_permutation(N, A, B)
    if perm is None:
        return "-1"
    return " ".join(map(str, perm))

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    max_n = 300000
    for idx in range(args.num):
        while True:
            N = random.randint(1, max_n)
            A = random.randint(1, max_n)
            B = random.randint(1, max_n)
            
            if random.random() < 0.3:
                A = random.randint(1, N)
                B = random.randint(1, N)
            
            if random.random() < 0.2:
                A = min(N, random.randint(max(1, N - 10), N + 10))
                B = min(N, random.randint(max(1, N - 10), N + 10))
            
            if random.random() < 0.1:
                A = N
                B = 1
            elif random.random() < 0.1:
                A = 1
                B = N
            
            if random.random() < 0.1:
                A = B = N
            
            if A * B >= N and A + B <= N + 1:
                if random.random() < 0.7:
                    break
            
            if random.random() < 0.3:
                break
        
        content = generate_test(N, A, B)
        
        filename = os.path.join(args.out_dir, f"test_{idx:03d}.in")
        with open(filename, 'w') as f:
            f.write(f"{N} {A} {B}\n")
    
if __name__ == "__main__":
    main()
