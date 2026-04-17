import sys
import random
import argparse
import os

def generate_one(N, B):
    # For each position i, A_i can be at most min(B_{i-1}, B_i) with B_0 = B_1, B_N = B_{N-1}
    A = [0] * N
    A[0] = B[0]
    A[N-1] = B[N-1]
    for i in range(1, N-1):
        A[i] = min(B[i-1], B[i])
    return A

def generate_test(seed):
    random.seed(seed)
    N = random.randint(2, 100)
    B = [random.randint(0, 10**5) for _ in range(N-1)]
    return N, B

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    for i in range(args.num):
        N, B = generate_test(args.seed + i)
        with open(os.path.join(args.out_dir, f'test_{i:03d}.in'), 'w') as f:
            f.write(f'{N}\n')
            f.write(' '.join(map(str, B)) + '\n')

if __name__ == '__main__':
    main()
