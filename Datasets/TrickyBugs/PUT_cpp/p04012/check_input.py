import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    if len(data) == 0:
        sys.stderr.write("No input provided\n")
        sys.exit(1)
    if len(data) > 1:
        sys.stderr.write("Extra lines\n")
        sys.exit(1)
    
    w = data[0].strip()
    if w == "":
        sys.stderr.write("Empty string\n")
        sys.exit(1)
    
    if not (1 <= len(w) <= 100):
        sys.stderr.write("Length out of range\n")
        sys.exit(1)
    
    if not all('a' <= ch <= 'z' for ch in w):
        sys.stderr.write("Invalid characters\n")
        sys.exit(1)
    
    # Check for extra non-whitespace tokens (ensure the whole line is exactly w, ignoring trailing/leading spaces)
    if data[0].strip() != data[0]:
        sys.stderr.write("Extra whitespace around line\n")
        sys.exit(1)
    
    # If we reach here, input is valid
    sys.exit(0)

if __name__ == "__main__":
    main()
