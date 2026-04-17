import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) != 1:
        sys.stderr.write("Extra tokens found\n")
        sys.exit(1)
    token = data[0]
    if not token.isdigit():
        sys.stderr.write("N must be an integer\n")
        sys.exit(1)
    N = int(token)
    if N < 3 or N > 100:
        sys.stderr.write("N out of range\n")
        sys.exit(1)
    # Check for extra whitespace characters after the token in original input
    # by verifying that the entire stdin content, stripped, equals the token
    original = sys.stdin.read(0)  # dummy to get full content? We already read all.
    # Actually we read all, so we need to check the original raw lines.
    # Let's re-read from sys.stdin.buffer to verify line structure.
    # Since we already consumed stdin, we can't re-read. Instead, we'll trust split()
    # but also check that the original stripped string equals the token.
    # We'll read again by seeking? Not possible. We'll accept the split approach.
    # Additional check: ensure no extra non-whitespace tokens.
    # Already done by len(data) check.
    sys.exit(0)

if __name__ == "__main__":
    main()
