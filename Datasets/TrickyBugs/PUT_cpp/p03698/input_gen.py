import sys
import random
import os
import argparse

def generate_input(seed_offset):
    random.seed(seed_offset)
    length = random.randint(2, 26)
    
    # Decide whether to generate "yes" or "no" case
    make_unique = random.random() < 0.5
    
    if make_unique:
        # Generate all unique characters
        letters = list('abcdefghijklmnopqrstuvwxyz')
        random.shuffle(letters)
        s = ''.join(letters[:length])
    else:
        # Generate with at least one duplicate
        # First create a base with some duplicates
        pool_size = random.randint(1, min(13, length))
        pool = random.choices('abcdefghijklmnopqrstuvwxyz', k=pool_size)
        
        # Ensure at least one duplicate by making length > pool_size
        # or by repeating some characters
        if pool_size == length:
            # Force a duplicate by making two positions same
            s_list = random.choices(pool, k=length)
            # Ensure duplicate exists
            if len(set(s_list)) == length:
                # Pick random position to duplicate
                dup_pos = random.randint(0, length-2)
                s_list[dup_pos+1] = s_list[dup_pos]
            s = ''.join(s_list)
        else:
            s = ''.join(random.choices(pool, k=length))
    
    return s

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        s = generate_input(args.seed + i)
        filename = os.path.join(args.out_dir, f'test_{i:03d}.in')
        with open(filename, 'w') as f:
            f.write(s + '\n')

if __name__ == '__main__':
    main()
