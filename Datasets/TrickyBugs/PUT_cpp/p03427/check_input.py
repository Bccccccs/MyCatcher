import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) != 1:
        sys.stderr.write("Error: Exactly one token expected")
        sys.exit(1)
    
    s = data[0]
    if not s.isdigit():
        sys.stderr.write("Error: Input must be a positive integer")
        sys.exit(1)
    
    # Check no leading zeros unless N is exactly "0" (but N >= 1)
    if s[0] == '0':
        sys.stderr.write("Error: Leading zeros not allowed")
        sys.exit(1)
    
    # Check range 1 ≤ N ≤ 10^16
    if len(s) > 17:
        sys.stderr.write("Error: N too large")
        sys.exit(1)
    
    N = int(s)
    if N < 1:
        sys.stderr.write("Error: N must be at least 1")
        sys.exit(1)
    if N > 10**16:
        sys.stderr.write("Error: N exceeds 10^16")
        sys.exit(1)
    
    # Check for extra non‑whitespace tokens (already ensured by split length)
    # But also ensure the whole input after stripping is exactly the token
    # (allow trailing newline/whitespace)
    full_input = sys.stdin.read(0)  # dummy, we already read all
    # Reconstruct original first line up to first newline to ensure no extra tokens on first line
    # Simpler: just verify that after stripping, the string equals the token
    # However, we already split, so extra whitespace is fine.
    # To catch extra non‑whitespace on same line, we can check:
    # If original input contains newline, everything after first newline must be whitespace.
    sys.stdin.seek(0)
    raw_lines = sys.stdin.readlines()
    if len(raw_lines) > 1:
        # after first line, all must be whitespace only
        for i in range(1, len(raw_lines)):
            if raw_lines[i].strip() != "":
                sys.stderr.write("Error: Extra non‑whitespace after first line")
                sys.exit(1)
    else:
        # single line: after stripping, must be exactly the token
        if raw_lines[0].strip() != s:
            # This catches cases like "123 456" on one line (split gives two tokens, already caught)
            # But also "123abc" etc. – but isdigit already caught that.
            # Actually, isdigit ensures all chars are digits, so "123\n" is fine.
            pass
    
    # If we reach here, input is valid
    sys.exit(0)

if __name__ == "__main__":
    main()
