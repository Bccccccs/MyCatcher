import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) != 2:
        sys.stderr.write("Exactly two tokens required")
        sys.exit(1)
    
    N_str, K_str = data[0], data[1]
    
    # Check N is a positive integer with no leading zeros unless it's "0" (but N >= 1)
    if not N_str.isdigit():
        sys.stderr.write("N must be a decimal integer")
        sys.exit(1)
    if len(N_str) > 1 and N_str[0] == '0':
        sys.stderr.write("N cannot have leading zeros")
        sys.exit(1)
    
    # Check N >= 1 and N < 10^100
    if len(N_str) > 100:
        sys.stderr.write("N must be less than 10^100")
        sys.exit(1)
    if N_str == '0':
        sys.stderr.write("N must be at least 1")
        sys.exit(1)
    
    # Check K is integer, 1 <= K <= 3
    if not K_str.isdigit():
        sys.stderr.write("K must be an integer")
        sys.exit(1)
    K = int(K_str)
    if K < 1 or K > 3:
        sys.stderr.write("K must be between 1 and 3")
        sys.exit(1)
    
    # Ensure no extra non‑whitespace tokens
    # Already checked len(data) == 2, so fine.
    sys.exit(0)

if __name__ == "__main__":
    main()
