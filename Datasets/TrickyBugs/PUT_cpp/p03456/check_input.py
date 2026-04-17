import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    
    if len(data) != 2:
        sys.stderr.write("Exactly two tokens expected\n")
        sys.exit(1)
    
    try:
        a = int(data[0])
        b = int(data[1])
    except ValueError:
        sys.stderr.write("Tokens must be integers\n")
        sys.exit(1)
    
    if not (1 <= a <= 100):
        sys.stderr.write("a must be between 1 and 100\n")
        sys.exit(1)
    
    if not (1 <= b <= 100):
        sys.stderr.write("b must be between 1 and 100\n")
        sys.exit(1)
    
    # Check for extra non‑whitespace tokens (by reading the whole input again)
    full_lines = sys.stdin.read()
    if full_lines:
        # If there is something left after the first read, it means extra tokens
        sys.stderr.write("Extra non‑whitespace tokens after the first two\n")
        sys.exit(1)
    
    # If we reach here, input is valid
    sys.stderr.write("OK\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
