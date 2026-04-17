import sys
import os
import random
import argparse

def generate_valid_string(seed, length):
    random.seed(seed)
    tokens = ["dream", "dreamer", "erase", "eraser"]
    result = []
    total_len = 0
    
    while total_len < length:
        t = random.choice(tokens)
        if total_len + len(t) > length:
            # Try to find a token that fits
            fitting = [tok for tok in tokens if total_len + len(tok) <= length]
            if not fitting:
                # If no token fits, break and pad with a partial token if needed
                break
            t = random.choice(fitting)
        result.append(t)
        total_len += len(t)
    
    # If we're under length, append a token and truncate
    if total_len < length:
        t = random.choice(tokens)
        result.append(t)
        total_len += len(t)
        s = ''.join(result)
        return s[:length]
    elif total_len > length:
        s = ''.join(result)
        return s[:length]
    else:
        return ''.join(result)

def generate_invalid_string(seed, length):
    random.seed(seed + 1000000)
    tokens = ["dream", "dreamer", "erase", "eraser"]
    result = []
    total_len = 0
    
    # First build a valid prefix
    while total_len < length:
        t = random.choice(tokens)
        if total_len + len(t) > length:
            fitting = [tok for tok in tokens if total_len + len(tok) <= length]
            if not fitting:
                break
            t = random.choice(fitting)
        result.append(t)
        total_len += len(t)
    
    s = ''.join(result)
    
    # If we already have exact length, make it invalid by changing last char
    if len(s) == length:
        # Change a random character to something else
        if s:
            pos = random.randint(0, len(s)-1)
            new_char = random.choice([c for c in 'abcdefghijklmnopqrstuvwxyz' if c != s[pos]])
            s = s[:pos] + new_char + s[pos+1:]
    
    # If shorter, append random chars
    if len(s) < length:
        s += ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length - len(s)))
    
    # Ensure it's not accidentally valid by checking with greedy algorithm
    # Simple validity check (not perfect but good enough for generation)
    temp = s
    while temp:
        if temp.endswith("dreamer"):
            temp = temp[:-7]
        elif temp.endswith("eraser"):
            temp = temp[:-6]
        elif temp.endswith("dream"):
            temp = temp[:-5]
        elif temp.endswith("erase"):
            temp = temp[:-5]
        else:
            break
    if not temp:
        # Accidentally made valid, recurse with different seed
        return generate_invalid_string(seed + 1, length)
    
    return s[:length]

def generate_one(seed, idx):
    random.seed(seed + idx * 1000)
    length = random.randint(1, 100000)
    
    # Mix of valid and invalid strings
    if random.random() < 0.5:
        s = generate_valid_string(seed + idx * 2000, length)
    else:
        s = generate_invalid_string(seed + idx * 3000, length)
    
    return s

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        s = generate_one(args.seed, i)
        with open(os.path.join(args.out_dir, f'test_{i:03d}.in'), 'w') as f:
            f.write(s + '\n')

if __name__ == '__main__':
    main()
