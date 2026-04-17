import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) != 1:
        sys.stderr.write("Exactly one integer expected\n")
        sys.exit(1)
    token = data[0]
    if token.startswith(('+', '-')):
        if not token[1:].isdigit():
            sys.stderr.write("Invalid integer format\n")
            sys.exit(1)
    else:
        if not token.isdigit():
            sys.stderr.write("Invalid integer format\n")
            sys.exit(1)
    try:
        X = int(token)
    except ValueError:
        sys.stderr.write("Invalid integer format\n")
        sys.exit(1)
    if not (-40 <= X <= 40):
        sys.stderr.write("X out of range\n")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
