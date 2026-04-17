import sys

def main():
    data = sys.stdin.read()
    if not data:
        sys.stderr.write("Empty input")
        sys.exit(1)
    
    lines = data.strip().splitlines()
    if len(lines) != 1:
        sys.stderr.write("Must have exactly one line")
        sys.exit(1)
    
    s = lines[0].strip()
    if not s:
        sys.stderr.write("Empty string")
        sys.exit(1)
    
    # Check that all characters are digits
    if not s.isdigit():
        sys.stderr.write("Non-digit character found")
        sys.exit(1)
    
    # Check no leading zeros unless N is exactly "0"
    if len(s) > 1 and s[0] == '0':
        sys.stderr.write("Leading zero not allowed")
        sys.exit(1)
    
    # Check length constraint: N < 10^200000 means at most 200000 digits
    if len(s) > 200000:
        sys.stderr.write("Too many digits")
        sys.exit(1)
    
    # Check that N is within given range: 0 <= N < 10^200000
    # Since we already checked length <= 200000, the only violation would be if
    # N has exactly 200001 digits, which we already prevented.
    # Also ensure N is not negative (already guaranteed by isdigit)
    
    # Check for extra non‑whitespace tokens: after stripping, the original line
    # should contain only the number and optional surrounding whitespace.
    original_line = lines[0]
    stripped_original = original_line.strip()
    if stripped_original != s:
        sys.stderr.write("Extra non‑whitespace tokens")
        sys.exit(1)
    
    # All checks passed
    sys.stderr.write("OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
