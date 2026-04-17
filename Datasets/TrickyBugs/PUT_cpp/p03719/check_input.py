import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        sys.stderr.write("Empty input\n")
        sys.exit(1)
    
    tokens = data.split()
    if len(tokens) != 3:
        sys.stderr.write(f"Expected 3 tokens, got {len(tokens)}\n")
        sys.exit(1)
    
    try:
        A = int(tokens[0])
        B = int(tokens[1])
        C = int(tokens[2])
    except ValueError:
        sys.stderr.write("All tokens must be integers\n")
        sys.exit(1)
    
    for name, val in [("A", A), ("B", B), ("C", C)]:
        if not (-100 <= val <= 100):
            sys.stderr.write(f"{name} = {val} out of range [-100, 100]\n")
            sys.exit(1)
    
    # Check for extra non‑whitespace content
    lines = data.splitlines()
    if len(lines) > 1:
        sys.stderr.write("Input must be a single line\n")
        sys.exit(1)
    if len(data.split()) != 3:
        sys.stderr.write("Extra non‑whitespace tokens\n")
        sys.exit(1)
    
    sys.stderr.write("OK\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
