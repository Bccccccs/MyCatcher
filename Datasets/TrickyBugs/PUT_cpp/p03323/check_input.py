import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) != 2:
        sys.stderr.write("Error: Exactly two integers required\n")
        sys.exit(1)
    
    try:
        A = int(data[0])
        B = int(data[1])
    except ValueError:
        sys.stderr.write("Error: Input must be integers\n")
        sys.exit(1)
    
    if not (1 <= A <= 16):
        sys.stderr.write("Error: A must be between 1 and 16\n")
        sys.exit(1)
    if not (1 <= B <= 16):
        sys.stderr.write("Error: B must be between 1 and 16\n")
        sys.exit(1)
    
    if A + B > 16:
        sys.stderr.write("Error: A+B must be at most 16\n")
        sys.exit(1)
    
    # Check for extra non-whitespace tokens
    extra = sys.stdin.read()
    if extra.strip():
        sys.stderr.write("Error: Extra input after the two integers\n")
        sys.exit(1)
    
    print("OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
