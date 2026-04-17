import sys

def validate():
    data = sys.stdin.read()
    lines = data.strip().splitlines()
    if len(lines) == 0:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(lines) > 1:
        sys.stderr.write("Extra lines\n")
        sys.exit(1)

    S = lines[0].strip()
    if len(S) == 0:
        sys.stderr.write("Empty string\n")
        sys.exit(1)

    if not (1 <= len(S) <= 200000):
        sys.stderr.write("String length out of range\n")
        sys.exit(1)

    for ch in S:
        if not ('1' <= ch <= '9'):
            sys.stderr.write("Invalid character\n")
            sys.exit(1)

    # Check for extra non‑whitespace tokens
    # We already split into lines and took the first line.
    # Ensure there are no other non‑whitespace characters before/after.
    # Since we stripped the whole data, any extra non‑whitespace would make more lines or longer first line.
    # But we already checked line count. However, there could be spaces/tabs in the first line.
    # Problem says input format is just S, so no internal whitespace.
    if S != lines[0]:
        sys.stderr.write("Whitespace inside string\n")
        sys.exit(1)

    # Ensure no extra tokens after ignoring whitespace
    tokens = data.split()
    if len(tokens) != 1:
        sys.stderr.write("Extra tokens\n")
        sys.exit(1)

    sys.stderr.write("OK")
    sys.exit(0)

if __name__ == "__main__":
    validate()
