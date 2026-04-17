import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)

    idx = 0
    try:
        # read N
        if idx >= len(data):
            raise ValueError("Missing N")
        N_str = data[idx]
        idx += 1
        N = int(N_str)
        if N < 2 or N > 200000:
            sys.stderr.write("N out of range\n")
            sys.exit(1)

        # read A_1 ... A_N
        A = []
        for _ in range(N):
            if idx >= len(data):
                raise ValueError("Not enough A_i values")
            a_str = data[idx]
            idx += 1
            a = int(a_str)
            if a < 1 or a > 200000:
                sys.stderr.write("A_i out of range\n")
                sys.exit(1)
            A.append(a)

        # check for extra non-whitespace tokens
        if idx != len(data):
            sys.stderr.write("Extra input tokens\n")
            sys.exit(1)

    except ValueError as e:
        sys.stderr.write(f"Invalid integer or format: {e}\n")
        sys.exit(1)

    # If we reach here, input is valid
    sys.stderr.write("OK\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
