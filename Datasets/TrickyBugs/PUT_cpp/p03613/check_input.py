import sys

def validate():
    data = sys.stdin.read().strip().split()
    if not data:
        return False
    # Check token count
    if len(data) < 2:
        return False
    try:
        N = int(data[0])
    except ValueError:
        return False
    if not (1 <= N <= 10**5):
        return False
    # Check if we have exactly N numbers after N
    if len(data) != N + 1:
        return False
    # Check each a_i
    for i in range(1, N + 1):
        try:
            a = int(data[i])
        except ValueError:
            return False
        if not (0 <= a < 10**5):
            return False
    # No extra tokens beyond what we processed
    return True

if __name__ == "__main__":
    if validate():
        sys.exit(0)
    else:
        sys.exit(1)
