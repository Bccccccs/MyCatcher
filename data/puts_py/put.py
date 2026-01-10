import sys

def solve():
    data = list(map(int, sys.stdin.read().split()))
    it = iter(data)

    n = next(it)
    m = next(it)
    k = next(it)

    A = [next(it) for _ in range(n)]
    B = [next(it) for _ in range(m)]

    A.sort()
    B.sort()

    i = j = 0
    ans = 0

    while i < n and j < m:
        if abs(A[i] - B[j]) < k:   # ⚠️ bug：严格小于
            ans += 1
            i += 1
            j += 1
        elif A[i] < B[j]:
            i += 1
        else:
            j += 1

    print(ans)

if __name__ == "__main__":
    solve()