import sys
import os
import random
import argparse

def generate_one(rand, N):
    s = ''.join(chr(rand.randint(ord('a'), ord('z'))) for _ in range(N))
    t = ''.join(chr(rand.randint(ord('a'), ord('z'))) for _ in range(N))
    return f"{N}\n{s}\n{t}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    rand = random.Random(args.seed)

    for i in range(args.num):
        N = rand.randint(1, 100)
        content = generate_one(rand, N)
        with open(os.path.join(args.out_dir, f"test_{i:03d}.in"), "w") as f:
            f.write(content)

if __name__ == "__main__":
    main()
