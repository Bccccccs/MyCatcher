import sys

def validate():
    data = sys.stdin.read().strip().split()
    if not data:
        return False
    if len(data) != 2:
        return False
    try:
        N = int(data[0])
        M = int(data[1])
    except ValueError:
        return False
    if not (1 <= N <= 10**5):
        return False
    if not (N <= M <= 10**9):
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
