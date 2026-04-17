import sys

def validate():
    data = sys.stdin.read().strip().split()
    if len(data) != 1:
        sys.stderr.write("Exactly one token expected")
        return False
    token = data[0]
    if not token.isdigit():
        sys.stderr.write("K must be an integer")
        return False
    K = int(token)
    if K < 2 or K > 100000:
        sys.stderr.write("K must be between 2 and 100000")
        return False
    # Ensure no extra non-whitespace content after the token
    # Since we split, extra tokens would appear in data
    # Already checked len(data) == 1, so no extra tokens.
    # But also ensure the original input didn't have extra non-whitespace
    # after stripping, by reconstructing:
    original = sys.stdin.getvalue() if hasattr(sys.stdin, 'getvalue') else None
    if original is None:
        # If we can't get original, we trust the split check
        pass
    else:
        stripped = original.strip()
        if stripped != token:
            # There were extra non-whitespace characters
            sys.stderr.write("Extra non-whitespace characters after K")
            return False
    return True

if __name__ == "__main__":
    try:
        if validate():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception:
        sys.exit(1)
