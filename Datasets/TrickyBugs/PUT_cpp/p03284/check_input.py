import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("Empty input")
        sys.exit(1)
    
    if len(data) != 2:
        sys.stderr.write("Exactly two tokens required")
        sys.exit(1)
    
    try:
        N = int(data[0])
        K = int(data[1])
    except ValueError:
        sys.stderr.write("Tokens must be integers")
        sys.exit(1)
    
    if not (1 <= N <= 100):
        sys.stderr.write("N out of range")
        sys.exit(1)
    
    if not (1 <= K <= 100):
        sys.stderr.write("K out of range")
        sys.exit(1)
    
    # Check for extra non‑whitespace tokens
    extra = sys.stdin.read()
    if extra.strip():
        sys.stderr.write("Extra non‑whitespace tokens")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
