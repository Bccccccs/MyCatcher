#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

const int MAXN = 2005;
int dp[MAXN][MAXN];
int pos[MAXN][3];
int seq[MAXN * 3];

int main() {
    int N;
    cin >> N;
    int M = 3 * N;
    for (int i = 0; i < M; ++i) {
        cin >> seq[i];
    }
    
    vector<int> cnt(N + 1, 0);
    for (int v = 1; v <= N; ++v) {
        pos[v][0] = pos[v][1] = pos[v][2] = -1;
    }
    for (int i = 0; i < M; ++i) {
        int v = seq[i];
        pos[v][cnt[v]] = i;
        cnt[v]++;
    }
    
    memset(dp, -1, sizeof(dp));
    dp[0][M] = 0;
    
    for (int len = M; len >= 0; --len) {
        for (int l = 0; l + len <= M; ++l) {
            int r = l + len;
            if (dp[l][r] == -1) continue;
            
            if (l + 2 <= r) {
                int v1 = seq[l];
                int v2 = seq[r - 1];
                int add = (v1 == v2) ? 1 : 0;
                dp[l + 1][r - 1] = max(dp[l + 1][r - 1], dp[l][r] + add);
            }
            
            for (int v = 1; v <= N; ++v) {
                int p1 = pos[v][0];
                int p2 = pos[v][1];
                int p3 = pos[v][2];
                if (p1 < l || p1 >= r) continue;
                if (p2 < l || p2 >= r) continue;
                if (p3 < l || p3 >= r) continue;
                
                vector<int> ps = {p1, p2, p3};
                sort(ps.begin(), ps.end());
                int a = ps[0], b = ps[1], c = ps[2];
                
                if (a == l && c == r - 1) {
                    dp[l + 1][r - 1] = max(dp[l + 1][r - 1], dp[l][r] + 1);
                }
                
                if (a == l && b == l + 1) {
                    dp[l + 2][r] = max(dp[l + 2][r], dp[l][r] + 1);
                }
                
                if (b == r - 2 && c == r - 1) {
                    dp[l][r - 2] = max(dp[l][r - 2], dp[l][r] + 1);
                }
            }
        }
    }
    
    int ans = 0;
    for (int l = 0; l <= M; ++l) {
        ans = max(ans, dp[l][l]);
    }
    cout << ans << endl;
    
    return 0;
}
