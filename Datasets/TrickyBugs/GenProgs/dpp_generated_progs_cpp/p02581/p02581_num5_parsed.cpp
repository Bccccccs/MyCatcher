#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int N;
    cin >> N;
    vector<int> A(3 * N);
    for (int i = 0; i < 3 * N; ++i) {
        cin >> A[i];
    }

    vector<vector<int>> dp(3 * N + 1, vector<int>(3 * N + 1, 0));

    for (int len = 2; len <= 3 * N; len += 2) {
        for (int l = 0; l + len <= 3 * N; ++l) {
            int r = l + len - 1;
            if (A[l] == A[r]) {
                dp[l][r] = max(dp[l][r], dp[l + 1][r - 1] + 1);
            }
            for (int k = l + 1; k < r; k += 2) {
                dp[l][r] = max(dp[l][r], dp[l][k] + dp[k + 1][r]);
            }
        }
    }

    cout << dp[0][3 * N - 1] << endl;
    return 0;
}
