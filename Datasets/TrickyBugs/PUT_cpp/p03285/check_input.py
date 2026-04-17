import sys

def main():
    data = sys.stdin.read().strip().split()
    
    # Check token count
    if len(data) != 1:
        sys.stderr.write("Error: Exactly one integer expected")
        sys.exit(1)
    
    # Check if it's a valid integer
    try:
        N = int(data[0])
    except ValueError:
        sys.stderr.write("Error: N must be an integer")
        sys.exit(1)
    
    # Check range constraint
    if not (1 <= N <= 100):
        sys.stderr.write("Error: N must be between 1 and 100 inclusive")
        sys.exit(1)
    
    # Check for extra non-whitespace characters
    # Reconstruct input to verify no extra tokens
    original = sys.stdin.read()
    sys.stdin = open(0)  # Reset stdin
    lines = [line.rstrip('\n') for line in sys.stdin]
    if len(lines) > 1:
        sys.stderr.write("Error: Too many lines")
        sys.exit(1)
    
    # Check the single line doesn't have trailing non-whitespace after parsing
    if lines:
        stripped_line = lines[0].strip()
        if stripped_line != data[0]:
            sys.stderr.write("Error: Extra non-whitespace characters")
            sys.exit(1)
    
    # If we reach here, input is valid
    sys.exit(0)

if __name__ == "__main__":
    main()
