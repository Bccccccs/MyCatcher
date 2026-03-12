#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <cstring>
using namespace std;

const int MOD = 998244353;

int main() {
    string S;
    cin >> S;
    int n = S.size();
    
    vector<vector<int>> dp(n + 1, vector<int>(n + 1, 0));
    dp[0][0] = 1;
    
    for (char c : S) {
        vector<vector<int>> ndp(n + 1, vector<int>(n + 1, 0));
        for (int a = 0; a <= n; ++a) {
            for (int b = 0; b <= n; ++b) {
                if (dp[a][b] == 0) continue;
                int val = dp[a][b];
                if (c == '0') {
                    if (b > 0) {
                        ndp[a][b - 1] = (ndp[a][b - 1] + val) % MOD;
                    } else {
                        ndp[a + 1][b] = (ndp[a + 1][b] + val) % MOD;
                    }
                } else { // c == '1'
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
