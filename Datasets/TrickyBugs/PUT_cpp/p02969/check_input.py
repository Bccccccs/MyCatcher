import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) != 1:
        sys.stderr.write("Exactly one integer expected\n")
        sys.exit(1)
    token = data[0]
    if not token.isdigit() and not (token[0] == '-' and token[1:].isdigit()):
        sys.stderr.write("Input must be an integer\n")
        sys.exit(1)
    try:
        r = int(token)
    except ValueError:
        sys.stderr.write("Invalid integer format\n")
        sys.exit(1)
    if r < 1 or r > 100:
        sys.stderr.write("r must be between 1 and 100 inclusive\n")
        sys.exit(1)
    # Check for extra non‑whitespace content after the first token
    # (already ensured by split, but we also need to ensure no extra lines with content)
    full = sys.stdin.read()
    if full.strip():
        sys.stderr.write("Extra input after the first integer\n")
        sys.exit(1)
    sys.stderr.write("OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
