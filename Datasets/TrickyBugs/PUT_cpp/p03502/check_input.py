import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) != 1:
        sys.stderr.write("Extra tokens found\n")
        sys.exit(1)
    
    s = data[0]
    # Check if it's a valid integer
    if not (s.isdigit() or (s[0] == '-' and s[1:].isdigit())):
        sys.stderr.write("Not a valid integer\n")
        sys.exit(1)
    
    n = int(s)
    # Check constraints
    if n < 1 or n > 10**8:
        sys.stderr.write("N out of range\n")
        sys.exit(1)
    
    # No extra content after the integer except whitespace already stripped
    # If we reach here, input is valid
    sys.exit(0)

if __name__ == "__main__":
    main()
