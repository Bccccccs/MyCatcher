import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) != 1:
        sys.stderr.write("Exactly one token expected\n")
        sys.exit(1)
    
    token = data[0]
    if not token.isdigit():
        sys.stderr.write("N must be an integer\n")
        sys.exit(1)
    
    N = int(token)
    if N < 1000 or N > 9999:
        sys.stderr.write("N must be between 1000 and 9999\n")
        sys.exit(1)
    
    # Check for extra leading zeros (e.g., 0123)
    if len(token) != 4:
        sys.stderr.write("N must be a 4-digit integer\n")
        sys.exit(1)
    
    # Check for extra whitespace or characters after the integer
    # Already handled by split() and token count check
    
    # Check if input is good according to problem definition
    # This is NOT part of validation, but we must ensure input matches constraints.
    # The problem only asks to validate input, not solve.
    # So we stop here after verifying format and constraints.
    
    # If we reach here, input is valid.
    sys.exit(0)

if __name__ == "__main__":
    main()
