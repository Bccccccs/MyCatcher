#include <iostream>
using namespace std;

/*
Buggy PUT (C++):
- Intended condition: |A[i] - B[j]| <= k
- Buggy condition used here: |A[i] - B[j]| < k   (strict)
This will reject pairs where the difference is exactly k.
*/

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    long long k;
    if (!(cin >> n >> m >> k)) return 0;

    vector<long long> A(n), B(m);
    for (int i = 0; i < n; i++) cin >> A[i];
    for (int j = 0; j < m; j++) cin >> B[j];

    sort(A.begin(), A.end());
    sort(B.begin(), B.end());

    int i = 0, j = 0;
    int ans = 0;

    while (i < n && j < m) {
        // BUG: should be <= k
        if (llabs(A[i] - B[j]) < k) {
            ans++;
            i++;
            j++;
        } else if (A[i] < B[j]) {
            i++;
        } else {
            j++;
        }
    }

    cout << ans << "\n";
    return 0;
}