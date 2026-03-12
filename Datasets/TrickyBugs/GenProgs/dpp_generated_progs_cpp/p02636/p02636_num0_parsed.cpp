#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

const int MOD = 998244353;

int main() {
    string S;
    cin >> S;
    int n = S.length();
    
    vector<vector<int>> dp(n + 1, vector<int>(n + 1, 0));
    dp[0][0] = 1;
    
    for (int i = 0; i < n; ++i) {
        vector<vector<int>> ndp(n + 1, vector<int>(n + 1, 0));
        for (int a = 0; a <= n; ++a) {
            for (int b = 0; b <= n; ++b) {
                if (dp[a][b] == 0) continue;
                int val = dp[a][b];
                if (S[i] == '0') {
                    if (b > 0) {
                        ndp[a][b - 1] = (ndp[a][b - 1] + val) % MOD;
                    } else {
                        ndp[a + 1][b] = (ndp[a + 1][b] + val) % MOD;
                    }
                } else {
                    if (a > 0) {
                        ndp[a - 1][b] = (ndp[a - 1][b] + val) % MOD;
                    } else {
                        ndp[a][b + 1] = (ndp[a][b + 1] + val) % MOD;
                    }
                }
                ndp[a][b] = (ndp[a][b] + val) % MOD;
            }
        }
        dp = move(ndp);
    }
    
    int ans = 0;
    for (int a = 0; a <= n; ++a) {
        for (int b = 0; b <= n; ++b) {
            ans = (ans + dp[a][b]) % MOD;
        }
    }
    cout << ans << endl;
    return 0;
}
