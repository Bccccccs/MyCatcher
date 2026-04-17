import sys

def is_perfect_power(n):
    if n <= 1:
        return True  # 1 = 1^p for any p
    max_b = int(n ** 0.5) + 1
    for b in range(2, max_b + 1):
        p = 2
        while b ** p <= n:
            if b ** p == n:
                return True
            p += 1
    return False

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) != 1:
        sys.stderr.write("Exactly one integer expected\n")
        sys.exit(1)
    token = data[0]
    if not token.isdigit():
        sys.stderr.write("Input must be a positive integer\n")
        sys.exit(1)
    X = int(token)
    if X < 1 or X > 1000:
        sys.stderr.write("X must be between 1 and 1000\n")
        sys.exit(1)
    # Check for extra non‑whitespace characters by re‑reading the whole line
    sys.stdin.seek(0)
    line = sys.stdin.readline().rstrip('\n')
    if line.strip() != token:
        sys.stderr.write("Extra non‑whitespace characters found\n")
        sys.exit(1)
    # Optional: verify that the answer exists (it always does, but we can check)
    best = 1
    for candidate in range(1, X + 1):
        if is_perfect_power(candidate):
            best = candidate
    # (We don't output the answer, just ensure input is valid)
    sys.exit(0)

if __name__ == "__main__":
    main()
