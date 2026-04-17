import sys

def validate():
    data = sys.stdin.read().strip().split()
    if not data:
        return False
    if len(data) != 1:
        return False
    s = data[0]
    if not s.isdigit():
        return False
    N = int(s)
    if N < 2 or N > 10**5:
        return False
    # Check for extra non‑whitespace tokens by reading the rest
    # We already split, so if there was extra non‑whitespace, len>1 caught it.
    # But we must also ensure no extra characters in the token itself (already done via isdigit).
    # Also ensure no leading zeros unless N is exactly "0", but N>=2 so not an issue.
    if s[0] == '0':
        return False
    return True

if __name__ == "__main__":
    if validate():
        sys.exit(0)
    else:
        sys.exit(1)
