import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) != 1:
        sys.stderr.write("Extra tokens found\n")
        sys.exit(1)
    s = data[0]
    if not s.isdigit() and not (s[0] == '-' and s[1:].isdigit()):
        sys.stderr.write("Not an integer\n")
        sys.exit(1)
    try:
        N = int(s)
    except ValueError:
        sys.stderr.write("Invalid integer format\n")
        sys.exit(1)
    if N < 1 or N > 86:
        sys.stderr.write("N out of range\n")
        sys.exit(1)
    # Check for extra leading zeros
    if s != str(int(s)):
        sys.stderr.write("Leading zeros or extra formatting\n")
        sys.exit(1)
    # Optional: verify answer fits in 10^18 (not needed per constraints)
    sys.stderr.write("OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
