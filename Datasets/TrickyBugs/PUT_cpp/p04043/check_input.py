import sys


def main() -> None:
    data = sys.stdin.read().strip().split()
    if len(data) != 3:
        sys.stderr.write("Error: expected exactly three integers: A B C\n")
        sys.exit(1)

    try:
        a, b, c = map(int, data)
    except ValueError:
        sys.stderr.write("Error: all input values must be integers\n")
        sys.exit(1)

    if not all(1 <= x <= 10 for x in (a, b, c)):
        sys.stderr.write("Error: require 1 <= A, B, C <= 10\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
