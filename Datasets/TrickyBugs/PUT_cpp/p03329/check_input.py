import sys

def validate() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        raise ValueError("No input")
    if len(data) != 1:
        raise ValueError("Extra tokens")
    
    s = data[0]
    if not s.isdigit():
        raise ValueError("N must be integer")
    
    N = int(s)
    if N < 1 or N > 100000:
        raise ValueError("N out of range")
    
    # Check for leading zeros
    if s[0] == '0':
        raise ValueError("Leading zero not allowed")
    
    # Ensure no extra characters in the original line (except whitespace)
    # Already handled by split, but we must ensure no extra non‑whitespace tokens.
    # We can reconstruct the integer and compare with original stripped line.
    original_stripped = sys.stdin.read(0)  # dummy, but we need original input
    # Better: read all lines, strip each, join with single space, compare tokens.
    sys.stdin.seek(0)
    lines = [line.rstrip('\n') for line in sys.stdin.readlines()]
    # Re‑parse carefully
    reconstructed = ' '.join(' '.join(line.split()) for line in lines if line.strip() != '')
    if reconstructed != s:
        # If there were extra numbers or words, they'd appear here
        tokens = reconstructed.split()
        if len(tokens) != 1:
            raise ValueError("Extra non‑whitespace tokens")
        # If single token but different (e.g., '127 ' vs '127'), fine.
        if tokens[0] != s:
            raise ValueError("Extra characters")

def main() -> None:
    try:
        validate()
        sys.stderr.write("OK\n")
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
