#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

const int MAXN = 2005;
int dp[MAXN][MAXN];
int pos[MAXN][3];
int N;
vector<int> a;

int solve(int l, int r) {
    if (l > r) return 0;
    if (dp[l][r] != -1) return dp[l][r];
    int res = 0;
    int x = a[l];
    for (int k = 0; k < 3; k++) {
        int p = pos[x][k];
        if (p < l || p > r) continue;
        for (int m = k + 1; m < 3; m++) {
            int q = pos[x][m];
            if (q < l || q > r) continue;
            int inner = solve(p + 1, q - 1);
            int outer = solve(l, p - 1) + solve(q + 1, r);
            res = max(res, inner + outer + 1);
        }
    }
    res = max(res, solve(l + 1, r));
    return dp[l][r] = res;
}

int main() {
    cin >> N;
    a.resize(3 * N);
    for (int i = 0; i < 3 * N; i++) {
        cin >> a[i];
    }
    vector<int> cnt(N + 1, 0);
    for (int i = 0; i < 3 * N; i++) {
        int v = a[i];
        pos[v][cnt[v]++] = i;
    }
    memset(dp, -1, sizeof(dp));
    cout << solve(0, 3 * N - 1) << endl;
    return 0;
}
