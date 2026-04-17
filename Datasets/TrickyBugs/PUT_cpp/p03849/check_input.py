import sys

MOD = 10**9 + 7

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    
    if len(data) != 1:
        sys.stderr.write("Exactly one token expected\n")
        sys.exit(1)
    
    s = data[0]
    if not s.isdigit():
        sys.stderr.write("N must be a positive integer\n")
        sys.exit(1)
    
    if s[0] == '0':
        sys.stderr.write("N must not have leading zeros\n")
        sys.exit(1)
    
    try:
        N = int(s)
    except ValueError:
        sys.stderr.write("N must be a valid integer\n")
        sys.exit(1)
    
    if N < 1 or N > 10**18:
        sys.stderr.write("N must be between 1 and 10^18 inclusive\n")
        sys.exit(1)
    
    # Check for extra whitespace or characters after reading
    # We already split, so we just need to ensure no extra non‑whitespace tokens.
    # But we must also ensure no extra content after the first token in the original input.
    # We'll re-read the first line to check for extra tokens on the same line.
    sys.stdin.seek(0)
    first_line = sys.stdin.readline().rstrip('\n')
    tokens_first_line = first_line.split()
    if len(tokens_first_line) != 1:
        sys.stderr.write("Extra tokens on first line\n")
        sys.exit(1)
    
    # Check if there is any second line (should be EOF)
    second_line = sys.stdin.readline()
    if second_line != '':
        sys.stderr.write("Extra lines after first line\n")
        sys.exit(1)
    
    # If we reach here, input is valid
    sys.exit(0)

if __name__ == "__main__":
    main()
