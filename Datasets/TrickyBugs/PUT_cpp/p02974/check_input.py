import sys

def validate():
    data = sys.stdin.read().strip().split()
    if not data:
        return False
    if len(data) != 2:
        return False
    try:
        n = int(data[0])
        k = int(data[1])
    except ValueError:
        return False
    if not (1 <= n <= 50):
        return False
    if not (0 <= k <= n * n):
        return False
    # Check for extra non‑whitespace tokens
    extra = sys.stdin.read()
    if extra.strip():
        return False
    return True

if __name__ == "__main__":
    if validate():
        sys.exit(0)
    else:
        sys.exit(1)
