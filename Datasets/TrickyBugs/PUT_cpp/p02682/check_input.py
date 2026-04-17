import sys


def main() -> None:
    data = sys.stdin.read().strip().split()
    if len(data) != 4:
        sys.stderr.write("Error: expected exactly 4 integers: A B C K\n")
        sys.exit(1)

    try:
        a, b, c, k = map(int, data)
    except ValueError:
        sys.stderr.write("Error: all input values must be integers\n")
        sys.exit(1)

    total = a + b + c
    if a < 0 or b < 0 or c < 0:
        sys.stderr.write("Error: require 0 <= A, B, C\n")
        sys.exit(1)
    if not (1 <= k <= total):
        sys.stderr.write("Error: require 1 <= K <= A + B + C\n")
        sys.exit(1)
    if total > 2_000_000_000:
        sys.stderr.write("Error: require A + B + C <= 2e9\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
