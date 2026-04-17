import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    
    if len(data) != 3:
        sys.stderr.write("Exactly 3 tokens required\n")
        sys.exit(1)
    
    try:
        N = int(data[0])
        A = int(data[1])
        B = int(data[2])
    except ValueError:
        sys.stderr.write("All tokens must be integers\n")
        sys.exit(1)
    
    if not (1 <= N <= 10**9):
        sys.stderr.write("N out of range\n")
        sys.exit(1)
    if not (1 <= A <= 10**9):
        sys.stderr.write("A out of range\n")
        sys.exit(1)
    if not (1 <= B <= 10**9):
        sys.stderr.write("B out of range\n")
        sys.exit(1)
    
    # Check for extra non-whitespace content
    full_input = sys.stdin.read()
    if full_input != '':
        # We already read all data earlier, so this shouldn't happen
        # but if there is leftover non-whitespace, it's invalid
        if full_input.strip():
            sys.stderr.write("Extra non-whitespace tokens\n")
            sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
