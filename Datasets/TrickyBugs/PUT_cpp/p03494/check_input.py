import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    
    idx = 0
    try:
        # Read N
        N = int(data[idx])
        idx += 1
    except ValueError:
        sys.stderr.write("N must be an integer\n")
        sys.exit(1)
    
    if not (1 <= N <= 200):
        sys.stderr.write("N out of range\n")
        sys.exit(1)
    
    # Check there are exactly N integers after N
    if len(data) - idx != N:
        sys.stderr.write("Incorrect number of A_i values\n")
        sys.exit(1)
    
    A = []
    for i in range(N):
        try:
            val = int(data[idx])
            idx += 1
        except ValueError:
            sys.stderr.write("A_i must be integers\n")
            sys.exit(1)
        if not (1 <= val <= 10**9):
            sys.stderr.write("A_i out of range\n")
            sys.exit(1)
        A.append(val)
    
    # Check no extra tokens
    if idx != len(data):
        sys.stderr.write("Extra tokens in input\n")
        sys.exit(1)
    
    # All checks passed
    sys.stderr.write("OK\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
