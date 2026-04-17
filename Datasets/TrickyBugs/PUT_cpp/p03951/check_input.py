import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    if len(data) != 3:
        sys.stderr.write("Error: Expected exactly 3 lines")
        sys.exit(1)

    # Check N
    try:
        N = int(data[0].strip())
    except ValueError:
        sys.stderr.write("Error: N must be an integer")
        sys.exit(1)

    if not (1 <= N <= 100):
        sys.stderr.write("Error: N must be between 1 and 100")
        sys.exit(1)

    s = data[1].strip()
    t = data[2].strip()

    if len(s) != N or len(t) != N:
        sys.stderr.write("Error: s and t must have length N")
        sys.exit(1)

    if not s.islower() or not t.islower():
        sys.stderr.write("Error: s and t must consist of lowercase English letters")
        sys.exit(1)

    if not s.isalpha() or not t.isalpha():
        sys.stderr.write("Error: s and t must consist only of letters")
        sys.exit(1)

    # Check for extra non-whitespace tokens
    if len(data[0].split()) != 1 or len(data[1].split()) != 1 or len(data[2].split()) != 1:
        sys.stderr.write("Error: Each line must contain exactly one token")
        sys.exit(1)

    # If we reach here, input is valid
    sys.stderr.write("OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
