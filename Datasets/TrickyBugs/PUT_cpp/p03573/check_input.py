import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    
    if len(data) != 3:
        sys.stderr.write("Exactly three tokens expected\n")
        sys.exit(1)
    
    try:
        A = int(data[0])
        B = int(data[1])
        C = int(data[2])
    except ValueError:
        sys.stderr.write("All tokens must be integers\n")
        sys.exit(1)
    
    if not (-100 <= A <= 100):
        sys.stderr.write("A out of range\n")
        sys.exit(1)
    if not (-100 <= B <= 100):
        sys.stderr.write("B out of range\n")
        sys.exit(1)
    if not (-100 <= C <= 100):
        sys.stderr.write("C out of range\n")
        sys.exit(1)
    
    # Check condition: exactly two are equal, one is different
    if (A == B and B == C) or (A != B and B != C and A != C):
        sys.stderr.write("Input does not satisfy 'two same, one different' condition\n")
        sys.exit(1)
    
    # Ensure no extra non‑whitespace tokens after the third
    # (already ensured by len(data) check)
    sys.stderr.write("OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
