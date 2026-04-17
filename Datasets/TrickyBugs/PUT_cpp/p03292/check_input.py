import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    
    if len(data) != 3:
        sys.stderr.write("Exactly three integers required\n")
        sys.exit(1)
    
    try:
        a1, a2, a3 = map(int, data)
    except ValueError:
        sys.stderr.write("All tokens must be integers\n")
        sys.exit(1)
    
    for val in (a1, a2, a3):
        if not (1 <= val <= 100):
            sys.stderr.write("Values must be between 1 and 100\n")
            sys.exit(1)
    
    # Check for extra non-whitespace tokens by reading the rest of stdin
    extra = sys.stdin.read().strip()
    if extra:
        sys.stderr.write("Extra non-whitespace characters after the three integers\n")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
