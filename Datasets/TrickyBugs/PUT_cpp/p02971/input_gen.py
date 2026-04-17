import sys
import random
import argparse
import os

def generate_one(rand, constraints):
    N = rand.randint(2, constraints['maxN'])
    if constraints['fixedN'] is not None:
        N = constraints['fixedN']
    
    maxA = constraints['maxA']
    if constraints['fixedMaxA'] is not None:
        maxA = constraints['fixedMaxA']
    
    if constraints['distinct']:
        pool = list(range(1, maxA + 1))
        rand.shuffle(pool)
        A = pool[:N]
    elif constraints['allSame']:
        val = rand.randint(1, maxA)
        A = [val] * N
    elif constraints['twoValues']:
        v1 = rand.randint(1, maxA)
        v2 = rand.randint(1, maxA)
        while v2 == v1:
            v2 = rand.randint(1, maxA)
        A = [v1 if rand.random() < 0.5 else v2 for _ in range(N)]
    elif constraints['maxAtEnds']:
        A = [rand.randint(1, maxA - 1) for _ in range(N)]
        pos = rand.randint(0, N - 1)
        A[pos] = maxA
    else:
        A = [rand.randint(1, maxA) for _ in range(N)]
    
    lines = [str(N)] + [str(x) for x in A]
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    constraints_list = [
        {'maxN': 10, 'maxA': 10, 'fixedN': None, 'fixedMaxA': None,
         'distinct': False, 'allSame': False, 'twoValues': False, 'maxAtEnds': False},
        {'maxN': 200000, 'maxA': 200000, 'fixedN': 200000, 'fixedMaxA': None,
         'distinct': False, 'allSame': False, 'twoValues': False, 'maxAtEnds': False},
        {'maxN': 200000, 'maxA': 200000, 'fixedN': None, 'fixedMaxA': None,
         'distinct': True, 'allSame': False, 'twoValues': False, 'maxAtEnds': False},
        {'maxN': 200000, 'maxA': 200000, 'fixedN': None, 'fixedMaxA': None,
         'distinct': False, 'allSame': True, 'twoValues': False, 'maxAtEnds': False},
        {'maxN': 200000, 'maxA': 200000, 'fixedN': None, 'fixedMaxA': None,
         'distinct': False, 'allSame': False, 'twoValues': True, 'maxAtEnds': False},
        {'maxN': 200000, 'maxA': 200000, 'fixedN': None, 'fixedMaxA': None,
         'distinct': False, 'allSame': False, 'twoValues': False, 'maxAtEnds': True},
    ]
    
    for i in range(args.num):
        cons = constraints_list[i % len(constraints_list)]
        content = generate_one(random, cons)
        with open(os.path.join(args.out_dir, f'test_{i:03d}.in'), 'w') as f:
            f.write(content)

if __name__ == '__main__':
    main()
