import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)

    # Check token count: N plus (N-1) B values
    try:
        idx = 0
        N = int(data[idx])
        idx += 1
    except ValueError:
        sys.stderr.write("N must be an integer\n")
        sys.exit(1)

    if N < 2 or N > 100:
        sys.stderr.write("N out of range\n")
        sys.exit(1)

    expected_tokens = 1 + (N - 1)
    if len(data) != expected_tokens:
        sys.stderr.write("Incorrect number of tokens\n")
        sys.exit(1)

    # Read B values
    B = []
    for i in range(N - 1):
        try:
            val = int(data[idx])
            idx += 1
        except ValueError:
            sys.stderr.write("B values must be integers\n")
            sys.exit(1)
        if val < 0 or val > 10**5:
            sys.stderr.write("B_i out of range\n")
            sys.exit(1)
        B.append(val)

    # No extra tokens check already done via length match
    sys.exit(0)

if __name__ == "__main__":
    main()
