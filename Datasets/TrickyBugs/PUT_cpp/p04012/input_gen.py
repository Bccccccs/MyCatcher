import sys
import os
import random
import argparse

def generate_one(seed_offset, length=None):
    rng = random.Random(seed_offset)
    if length is None:
        length = rng.randint(1, 100)
    
    # Choose strategy: all even counts or one odd count
    strategy = rng.choice(['even', 'odd'])
    
    if strategy == 'even':
        # Ensure all counts are even
        counts = [rng.randint(0, 5) * 2 for _ in range(26)]
        total = sum(counts)
        if total == 0:
            counts[0] = 2
            total = 2
        if total > 100:
            # Scale down while keeping even
            factor = 100 // total
            if factor == 0:
                counts = [2 if c > 0 else 0 for c in counts]
                total = sum(counts)
                if total > 100:
                    # Reduce further
                    for i in range(26):
                        if counts[i] > 0:
                            counts[i] = 2
                            break
                    total = sum(counts)
            else:
                counts = [c * factor for c in counts]
                total = sum(counts)
        
        # Build string
        chars = []
        for i in range(26):
            chars.extend([chr(ord('a') + i)] * counts[i])
        rng.shuffle(chars)
        w = ''.join(chars)
        
    else:  # 'odd'
        # Ensure at least one odd count
        counts = [rng.randint(0, 5) * 2 for _ in range(26)]
        # Make one random count odd
        idx = rng.randint(0, 25)
        counts[idx] = max(1, counts[idx] | 1)  # Make odd, at least 1
        
        total = sum(counts)
        if total > 100:
            # Scale down while keeping that one odd
            factor = 100 // total
            if factor == 0:
                counts = [2 if c > 0 else 0 for c in counts]
                counts[idx] = 1  # Ensure odd
                total = sum(counts)
                if total > 100:
                    # Reduce others
                    for i in range(26):
                        if i != idx and counts[i] > 0:
                            counts[i] = 0
                            total = sum(counts)
                            if total <= 100:
                                break
            else:
                counts = [c * factor for c in counts]
                counts[idx] = counts[idx] | 1  # Ensure odd
                total = sum(counts)
        
        # Build string
        chars = []
        for i in range(26):
            chars.extend([chr(ord('a') + i)] * counts[i])
        rng.shuffle(chars)
        w = ''.join(chars)
    
    # Final length check and adjustment
    if len(w) > 100:
        w = w[:100]
    elif len(w) < 1:
        w = 'a'
    
    return w

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        w = generate_one(args.seed + i)
        with open(os.path.join(args.out_dir, f'test_{i:03d}.in'), 'w') as f:
            f.write(w + '\n')

if __name__ == '__main__':
    main()
