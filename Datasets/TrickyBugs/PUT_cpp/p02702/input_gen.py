import sys
import os
import random
import argparse

def generate_single_test(seed, length):
    rng = random.Random(seed)
    digits = [str(rng.randint(1, 9)) for _ in range(length)]
    return ''.join(digits)

def generate_tests(out_dir, num_tests, base_seed):
    os.makedirs(out_dir, exist_ok=True)
    for test_id in range(1, num_tests + 1):
        seed = base_seed + test_id
        rng = random.Random(seed)
        
        # Generate length: mix of small, medium, large up to 200000
        if test_id == 1:
            length = 1
        elif test_id == 2:
            length = 200000
        elif test_id <= 5:
            length = rng.randint(1, 100)
        elif test_id <= 10:
            length = rng.randint(100, 1000)
        elif test_id <= 15:
            length = rng.randint(1000, 10000)
        elif test_id <= 20:
            length = rng.randint(10000, 50000)
        else:
            length = rng.randint(50000, 200000)
        
        s = generate_single_test(seed, length)
        with open(os.path.join(out_dir, f"test_{test_id:03d}.in"), 'w') as f:
            f.write(s + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    generate_tests(args.out_dir, args.num, args.seed)

if __name__ == "__main__":
    main()
