import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) != 2:
        sys.stderr.write("Error: Input must contain exactly two integers.\n")
        sys.exit(1)
    
    try:
        N = int(data[0])
        M = int(data[1])
    except ValueError:
        sys.stderr.write("Error: Input tokens must be integers.\n")
        sys.exit(1)
    
    if not (1 <= N <= 10**12):
        sys.stderr.write("Error: N must be between 1 and 10^12.\n")
        sys.exit(1)
    
    if not (1 <= M <= 10**12):
        sys.stderr.write("Error: M must be between 1 and 10^12.\n")
        sys.exit(1)
    
    # Check for extra non‑whitespace tokens
    extra = sys.stdin.read()
    if extra.strip():
        sys.stderr.write("Error: Extra non‑whitespace tokens after the two integers.\n")
        sys.exit(1)
    
    # If everything is valid
    sys.stderr.write("OK\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
