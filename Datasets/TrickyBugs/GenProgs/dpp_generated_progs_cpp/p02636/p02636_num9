#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

const int MOD = 998244353;
int dp[2][305][305];

int main() {
    string S;
    cin >> S;
    int n = S.size();
    
    memset(dp, 0, sizeof(dp));
    dp[0][0][0] = 1;
    
    for (int i = 0; i < n; ++i) {
        int cur = i & 1;
        int nxt = cur ^ 1;
        memset(dp[nxt], 0, sizeof(dp[nxt]));
        
        for (int a = 0; a <= n; ++a) {
            for (int b = 0; b <= n; ++b) {
                if (dp[cur][a][b] == 0) continue;
                int val = dp[cur][a][b];
                
                if (S[i] == '0') {
                    // consume a 1 if possible
                    if (b > 0) {
                        dp[nxt][a][b - 1] = (dp[nxt][a][b - 1] + val) % MOD;
                    }
                    // add a new 0
                    dp[nxt][a + 1][b] = (dp[nxt][a + 1][b] + val) % MOD;
                } else { // S[i] == '1'
                    // consume a 0 if possible
                    if (a > 0) {
                        dp[nxt][a - 1][b] = (dp[nxt][a - 1][b] + val) % MOD;
                    }
                    // add a new 1
                    dp[nxt][a][b + 1] = (dp[nxt][a][b + 1] + val) % MOD;
                }
            }
        }
    }
    
    int ans = 0;
    for (int a = 0; a <= n; ++a) {
        for (int b = 0; b <= n; ++b) {
            ans = (ans + dp[n & 1][a][b]) % MOD;
        }
    }
    
    cout << ans << endl;
    return 0;
}
