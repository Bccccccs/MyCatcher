import sys
import os
import random

def generate_input(seed_offset, base_seed):
    rng = random.Random(base_seed + seed_offset)
    
    # Generate N, A, B within [1, 1e9]
    # Use various distributions to cover edge cases
    choice = rng.randint(0, 9)
    
    if choice == 0:
        # Small values
        N = rng.randint(1, 100)
        A = rng.randint(1, 100)
        B = rng.randint(1, 100)
    elif choice == 1:
        # Large values near upper bound
        N = rng.randint(10**9 - 100, 10**9)
        A = rng.randint(10**9 - 100, 10**9)
        B = rng.randint(10**9 - 100, 10**9)
    elif choice == 2:
        # A > B case (should produce 0)
        N = rng.randint(1, 10**9)
        A = rng.randint(2, 10**9)
        B = rng.randint(1, A - 1)
    elif choice == 3:
        # A == B case
        N = rng.randint(1, 10**9)
        val = rng.randint(1, 10**9)
        A = val
        B = val
    elif choice == 4:
        # N = 1 edge cases
        N = 1
        A = rng.randint(1, 10**9)
        B = rng.randint(1, 10**9)
    elif choice == 5:
        # Random uniform
        N = rng.randint(1, 10**9)
        A = rng.randint(1, 10**9)
        B = rng.randint(1, 10**9)
    elif choice == 6:
        # A and B close together
        N = rng.randint(1, 10**9)
        A = rng.randint(1, 10**9 - 100)
        B = rng.randint(A, min(10**9, A + 100))
    elif choice == 7:
        # A and B far apart
        N = rng.randint(1, 10**9)
        A = rng.randint(1, 10**9 // 2)
        B = rng.randint(10**9 // 2 + 1, 10**9)
    elif choice == 8:
        # N very small, A and B large
        N = rng.randint(1, 10)
        A = rng.randint(10**8, 10**9)
        B = rng.randint(10**8, 10**9)
    else:
        # Random but ensure A <= B sometimes
        N = rng.randint(1, 10**9)
        A = rng.randint(1, 10**9)
        B = rng.randint(1, 10**9)
        if rng.random() < 0.5 and A > B:
            A, B = B, A
    
    # Ensure constraints
    N = max(1, min(N, 10**9))
    A = max(1, min(A, 10**9))
    B = max(1, min(B, 10**9))
    
    return f"{N} {A} {B}"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out_dir, exist_ok=True)
    
    for i in range(args.num):
        content = generate_input(i, args.seed)
        filename = os.path.join(args.out_dir, f"test_{i:03d}.in")
        with open(filename, 'w') as f:
            f.write(content + "\n")

if __name__ == "__main__":
    main()
