import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) != 2:
        sys.stderr.write("Exactly two integers required\n")
        sys.exit(1)
    try:
        L = int(data[0])
        R = int(data[1])
    except ValueError:
        sys.stderr.write("Invalid integer format\n")
        sys.exit(1)
    if not (0 <= L < R <= 2 * 10**9):
        sys.stderr.write("Constraint violation: 0 <= L < R <= 2e9\n")
        sys.exit(1)
    # Check for extra non‑whitespace tokens
    extra = sys.stdin.read().strip()
    if extra:
        sys.stderr.write("Extra non‑whitespace tokens after the first line\n")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
