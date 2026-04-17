import sys

def main():
    data = sys.stdin.read()
    lines = data.strip().splitlines()
    if len(lines) != 1:
        sys.stderr.write("Exactly one line expected")
        sys.exit(1)
    s = lines[0].rstrip('\n')
    if s != lines[0]:
        sys.stderr.write("Extra whitespace at end of line")
        sys.exit(1)
    if not (2 <= len(s) <= 26):
        sys.stderr.write("String length must be between 2 and 26 inclusive")
        sys.exit(1)
    if not s.isalpha() or not s.islower():
        sys.stderr.write("String must consist only of lowercase English letters")
        sys.exit(1)
    # Check for extra tokens (more than one token on the line)
    tokens = lines[0].split()
    if len(tokens) != 1:
        sys.stderr.write("Only one token allowed")
        sys.exit(1)
    # No need to check character uniqueness; that's the problem's task.
    sys.exit(0)

if __name__ == "__main__":
    main()
