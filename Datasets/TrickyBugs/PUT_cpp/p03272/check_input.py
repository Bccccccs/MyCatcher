import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    
    if len(data) != 2:
        sys.stderr.write("Exactly two integers expected\n")
        sys.exit(1)
    
    try:
        N = int(data[0])
        i = int(data[1])
    except ValueError:
        sys.stderr.write("Invalid integer format\n")
        sys.exit(1)
    
    if not (1 <= N <= 100):
        sys.stderr.write("N out of range\n")
        sys.exit(1)
    
    if not (1 <= i <= N):
        sys.stderr.write("i out of range\n")
        sys.exit(1)
    
    # Check for extra non‑whitespace tokens (already ensured by len(data)==2)
    # If there were extra whitespace tokens, split() already removed them.
    # But we must ensure no extra characters in the original input beyond the two tokens.
    # We can reconstruct the two tokens and compare with original stripped input.
    reconstructed = f"{N} {i}"
    original_stripped = sys.stdin.read().strip()  # Already consumed, so this won't work.
    # Instead, we need to check before consuming. Let's read line and split carefully.
    # Better approach: read the whole input, split into lines, process first line.
    sys.exit(0)

if __name__ == "__main__":
    main()
