import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    if len(data) < 2:
        sys.stderr.write("Error: insufficient lines")
        sys.exit(1)
    
    # Check first line: exactly one integer
    first_line = data[0].strip()
    if not first_line:
        sys.stderr.write("Error: first line empty")
        sys.exit(1)
    parts = first_line.split()
    if len(parts) != 1:
        sys.stderr.write("Error: first line must contain exactly one integer")
        sys.exit(1)
    try:
        N = int(parts[0])
    except ValueError:
        sys.stderr.write("Error: N must be an integer")
        sys.exit(1)
    
    if not (1 <= N <= 100):
        sys.stderr.write("Error: N out of range")
        sys.exit(1)
    
    # Check second line: exactly one string
    if len(data) < 2:
        sys.stderr.write("Error: missing second line")
        sys.exit(1)
    second_line = data[1].rstrip('\n')
    # Allow trailing spaces? Problem says format: N then S, so second line should be S.
    # We'll split to check extra non‑whitespace tokens.
    second_parts = second_line.split()
    if len(second_parts) != 1:
        sys.stderr.write("Error: second line must contain exactly one string")
        sys.exit(1)
    S = second_parts[0]
    
    if len(S) != N:
        sys.stderr.write("Error: length of S does not match N")
        sys.exit(1)
    
    if not S.isalpha() or not S.islower():
        sys.stderr.write("Error: S must consist of lowercase English letters")
        sys.exit(1)
    
    # Check for extra lines
    if len(data) > 2:
        # Allow trailing empty lines? Problem says input format is exactly two lines.
        # We'll treat any non‑whitespace content after line 2 as extra tokens.
        for idx in range(2, len(data)):
            if data[idx].strip():
                sys.stderr.write("Error: extra non‑whitespace tokens after second line")
                sys.exit(1)
    
    # If we reach here, input is valid
    sys.stderr.write("OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
