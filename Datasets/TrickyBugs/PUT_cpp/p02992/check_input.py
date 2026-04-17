import sys

def validate():
    data = sys.stdin.read().strip()
    if not data:
        return False
    lines = data.splitlines()
    if len(lines) != 1:
        return False
    tokens = lines[0].split()
    if len(tokens) != 2:
        return False
    try:
        N = int(tokens[0])
        K = int(tokens[1])
    except ValueError:
        return False
    if not (1 <= N <= 10**9):
        return False
    if not (2 <= K <= 100):
        return False
    # Check for extra non‑whitespace tokens
    if len(lines[0].split()) != 2:
        return False
    return True

if __name__ == "__main__":
    if validate():
        sys.exit(0)
    else:
        sys.exit(1)
