import sys

def validate():
    data = sys.stdin.read().strip().split()
    if not data:
        return False
    if len(data) != 3:
        return False
    try:
        N, A, B = map(int, data)
    except ValueError:
        return False
    if not (1 <= N <= 3 * 10**5):
        return False
    if not (1 <= A <= 3 * 10**5):
        return False
    if not (1 <= B <= 3 * 10**5):
        return False
    # Check for extra non‑whitespace tokens
    # We already split, so we need to ensure the whole input consisted of exactly three tokens.
    # Reconstruct the input as string without leading/trailing spaces and compare token count.
    raw = sys.stdin.read()
    sys.stdin.seek(0)
    raw_lines = sys.stdin.read().splitlines()
    all_tokens = []
    for line in raw_lines:
        all_tokens.extend(line.split())
    if len(all_tokens) != 3:
        return False
    return True

if __name__ == "__main__":
    if validate():
        sys.exit(0)
    else:
        sys.exit(1)
