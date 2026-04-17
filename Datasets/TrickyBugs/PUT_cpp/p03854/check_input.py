import sys

def main():
    data = sys.stdin.read()
    lines = data.strip().splitlines()
    if len(lines) == 0:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(lines) > 1:
        sys.stderr.write("Extra lines in input\n")
        sys.exit(1)
    s = lines[0].rstrip('\n')
    if len(s) < 1 or len(s) > 10**5:
        sys.stderr.write("String length out of range\n")
        sys.exit(1)
    if not s.islower():
        sys.stderr.write("String contains non-lowercase letters\n")
        sys.exit(1)
    if not s.isalpha():
        sys.stderr.write("String contains non-alphabetic characters\n")
        sys.exit(1)
    # Check for extra tokens (more than one token on the line)
    tokens = lines[0].split()
    if len(tokens) != 1:
        sys.stderr.write("Extra non-whitespace tokens\n")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
