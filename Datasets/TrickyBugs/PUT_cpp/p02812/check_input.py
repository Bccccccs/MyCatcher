import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    if len(data) < 2:
        sys.stderr.write("Not enough lines")
        sys.exit(1)
    # Check no extra non‑whitespace tokens
    tokens = []
    for line in data:
        tokens.extend(line.split())
    if len(tokens) != 2:
        sys.stderr.write("Expected exactly 2 tokens (N and S)")
        sys.exit(1)

    # First token: N
    if not tokens[0].isdigit():
        sys.stderr.write("N must be an integer")
        sys.exit(1)
    N = int(tokens[0])
    if not (3 <= N <= 50):
        sys.stderr.write("N out of range")
        sys.exit(1)

    # Second token: S
    S = tokens[1]
    if len(S) != N:
        sys.stderr.write("Length of S does not match N")
        sys.exit(1)
    if not S.isalpha() or not S.isupper():
        sys.stderr.write("S must consist of uppercase English letters")
        sys.exit(1)

    # No extra characters after S in its line is already ensured by token splitting.
    # But we must ensure the original line count matches exactly two lines.
    if len(data) != 2:
        # If there were empty lines after S, they become extra lines.
        # However, .splitlines() removes trailing empty lines, so we check
        # by counting non‑empty lines.
        non_empty = [line for line in data if line.strip() != ""]
        if len(non_empty) != 2:
            sys.stderr.write("Extra non‑empty lines")
            sys.exit(1)

    # If we reach here, input is valid.
    sys.stderr.write("OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
