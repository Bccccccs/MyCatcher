import sys

def validate():
    data = sys.stdin.read().strip().split()
    if not data:
        return False
    if len(data) != 3:
        return False
    try:
        N = int(data[0])
        X = int(data[1])
        M = int(data[2])
    except ValueError:
        return False
    
    # Check constraints
    if not (1 <= N <= 10**10):
        return False
    if not (0 <= X < M <= 10**5):
        return False
    
    # Ensure no extra non-whitespace tokens
    extra = sys.stdin.read()
    if extra.strip():
        return False
    
    return True

if __name__ == "__main__":
    if validate():
        sys.exit(0)
    else:
        sys.exit(1)
