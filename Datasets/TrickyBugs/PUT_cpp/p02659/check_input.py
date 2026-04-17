import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        sys.stderr.write("Empty input\n")
        sys.exit(1)
    
    lines = data.splitlines()
    if len(lines) != 1:
        sys.stderr.write("Must be exactly one line\n")
        sys.exit(1)
    
    tokens = lines[0].split()
    if len(tokens) != 2:
        sys.stderr.write("Exactly two tokens required\n")
        sys.exit(1)
    
    A_str, B_str = tokens
    
    # Check A
    if not A_str.isdigit():
        sys.stderr.write("A must be a non-negative integer\n")
        sys.exit(1)
    A = int(A_str)
    if A < 0 or A > 10**15:
        sys.stderr.write("A out of range\n")
        sys.exit(1)
    
    # Check B
    parts = B_str.split('.')
    if len(parts) != 2:
        sys.stderr.write("B must have exactly one decimal point\n")
        sys.exit(1)
    
    integer_part, fractional_part = parts
    if not integer_part.isdigit() or not fractional_part.isdigit():
        sys.stderr.write("B must consist of digits and a decimal point\n")
        sys.exit(1)
    
    if len(fractional_part) != 2:
        sys.stderr.write("B must have exactly two digits after decimal point\n")
        sys.exit(1)
    
    # Reconstruct B as integer of hundredths to avoid float precision issues
    B_int = int(integer_part) * 100 + int(fractional_part)
    if B_int < 0 or B_int >= 10 * 100:  # B < 10 means up to 9.99
        sys.stderr.write("B out of range\n")
        sys.exit(1)
    
    # Ensure no extra non‑whitespace content
    if data.strip() != ' '.join(tokens):
        sys.stderr.write("Extra whitespace or formatting issues\n")
        sys.exit(1)
    
    sys.stderr.write("OK\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
