import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    
    if len(data) != 2:
        sys.stderr.write("Exactly two integers required\n")
        sys.exit(1)
    
    try:
        N = int(data[0])
        K = int(data[1])
    except ValueError:
        sys.stderr.write("Both tokens must be integers\n")
        sys.exit(1)
    
    if not (1 <= N <= 10**9):
        sys.stderr.write("N out of range\n")
        sys.exit(1)
    
    if not (2 <= K <= 10):
        sys.stderr.write("K out of range\n")
        sys.exit(1)
    
    # Check for extra non‑whitespace tokens
    extra = sys.stdin.read()
    if extra.strip():
        sys.stderr.write("Extra non‑whitespace tokens after the first line\n")
        sys.exit(1)
    
    # If we reach here, input is valid
    sys.stderr.write("OK\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
