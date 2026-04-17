import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) != 1:
        sys.stderr.write("Exactly one token expected\n")
        sys.exit(1)
    token = data[0]
    if not token.isdigit():
        sys.stderr.write("N must be a positive integer\n")
        sys.exit(1)
    N = int(token)
    if not (1 <= N <= 100):
        sys.stderr.write("N must be between 1 and 100\n")
        sys.exit(1)
    # Ensure no extra non‑whitespace tokens after reading N
    # (already ensured by len(data) check)
    sys.exit(0)

if __name__ == "__main__":
    main()
