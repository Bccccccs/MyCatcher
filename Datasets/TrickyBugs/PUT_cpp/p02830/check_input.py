import sys

def validate():
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return False
    # Remove empty lines at the end if any, but keep structure
    lines = [line.rstrip('\n') for line in data if line.strip() != '' or line == '']
    # We need exactly two non-empty lines after ignoring trailing empty lines
    non_empty = [line for line in lines if line.strip() != '']
    if len(non_empty) != 2:
        return False
    # First line: N
    try:
        N = int(non_empty[0].strip())
    except ValueError:
        return False
    if not (1 <= N <= 100):
        return False
    # Second line: S and T separated by space
    parts = non_empty[1].strip().split()
    if len(parts) != 2:
        return False
    S, T = parts[0], parts[1]
    if len(S) != N or len(T) != N:
        return False
    if not S.isalpha() or not S.islower():
        return False
    if not T.isalpha() or not T.islower():
        return False
    # Check for extra tokens beyond the two lines
    # We already filtered to exactly two non-empty lines, but ensure no extra non-whitespace tokens exist
    # by verifying the original line count matches expectation (2 lines) after stripping empty lines at end
    # However, the problem allows extra whitespace, so we only care about non-empty content.
    # Reconstruct: split by whitespace on entire input
    all_tokens = sys.stdin.read().split()
    sys.stdin.seek(0)
    first_line = sys.stdin.readline().strip()
    second_line = sys.stdin.readline().strip()
    rest = sys.stdin.read().strip()
    if rest != '':
        return False
    # Check token counts: first line 1 token, second line 2 tokens
    tokens_first = first_line.split()
    if len(tokens_first) != 1:
        return False
    tokens_second = second_line.split()
    if len(tokens_second) != 2:
        return False
    # No extra lines allowed
    if sys.stdin.read().strip() != '':
        return False
    return True

if __name__ == "__main__":
    if validate():
        sys.exit(0)
    else:
        sys.exit(1)
