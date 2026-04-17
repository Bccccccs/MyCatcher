import sys

def validate():
    data = sys.stdin.read().strip().split()
    if not data:
        return False
    if len(data) != 1:
        return False
    try:
        N = int(data[0])
    except ValueError:
        return False
    if not (1 <= N <= 1000):
        return False
    # Ensure no extra non‑whitespace tokens
    # We already split, so just check that the whole input after stripping
    # consists of exactly this token.
    raw = sys.stdin.read()
    sys.stdin.seek(0)
    raw_lines = sys.stdin.read().splitlines()
    reconstructed = ' '.join(' '.join(line.split()) for line in raw_lines if line.strip())
    tokens = reconstructed.split()
    if len(tokens) != 1:
        return False
    if int(tokens[0]) != N:
        return False
    return True

if __name__ == "__main__":
    if validate():
        sys.exit(0)
    else:
        sys.exit(1)
