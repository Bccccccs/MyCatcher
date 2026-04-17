import sys
import os
import random
import math

def generate_N(length, rng):
    """Generate a random N with given length (number of digits)."""
    if length == 1:
        return str(rng.randint(1, 9))
    first = rng.randint(1, 9)
    rest = ''.join(str(rng.randint(0, 9)) for _ in range(length - 1))
    return str(first) + rest

def generate_small_N(max_digits, rng):
    """Generate N with up to max_digits digits."""
    length = rng.randint(1, max_digits)
    return generate_N(length, rng)

def generate_large_N(rng):
    """Generate N with up to 100 digits."""
    length = rng.randint(1, 100)
    return generate_N(length, rng)

def generate_edge_N(rng):
    """Generate edge-case N."""
    choice = rng.randint(0, 5)
    if choice == 0:
        return "1"
    elif choice == 1:
        return "9" * rng.randint(1, 100)
    elif choice == 2:
        length = rng.randint(1, 100)
        return "1" + "0" * (length - 1)
    elif choice == 3:
        length = rng.randint(1, 100)
        return "1" * length
    elif choice == 4:
        length = rng.randint(2, 100)
        mid = rng.randint(0, 9)
        return "1" + str(mid) + "0" * (length - 2)
    else:
        length = rng.randint(2, 100)
        return str(rng.randint(2, 9)) + "0" * (length - 1)

def generate_test_input(rng):
    """Generate one test case."""
    # Choose K
    K = rng.randint(1, 3)
    
    # Choose N type
    type_choice = rng.random()
    if type_choice < 0.3:
        N = generate_small_N(18, rng)
    elif type_choice < 0.6:
        N = generate_large_N(rng)
    else:
        N = generate_edge_N(rng)
    
    # Ensure N < 10^100
    if len(N) > 100:
        N = N[:100]
    if len(N) == 100:
        while N[0] == '0' or int(N[0]) >= 10:
            N = str(rng.randint(1, 9)) + N[1:]
    
    return f"{N}\n{K}\n"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_dir', type=str, required=True)
    parser.add_argument('--num', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_test_input(random.Random(args.seed + i * 10007))
        with open(os.path.join(args.out_dir, f"test_{i:03d}.in"), 'w') as f:
            f.write(content)

if __name__ == "__main__":
    main()
