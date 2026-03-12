#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

const int MAXN = 2005;
int dp[MAXN][MAXN];
int pos[MAXN][3];
int seq[3 * MAXN];
int N;

int solve(int l, int r) {
    if (l > r) return 0;
    if (dp[l][r] != -1) return dp[l][r];
    int res = 0;
    int a = seq[l];
    int idx1 = -1, idx2 = -1, idx3 = -1;
    for (int k = 0; k < 3; k++) {
        if (pos[a][k] == l) idx1 = k;
        else if (pos[a][k] == r) idx3 = k;
        else idx2 = k;
    }
    if (idx1 != -1 && idx3 != -1) {
        res = max(res, (l == r ? 0 : solve(l + 1, r - 1)) + 1);
    }
    for (int k = 0; k < 3; k++) {
        if (pos[a][k] > l && pos[a][k] <= r) {
            int m = pos[a][k];
            res = max(res, solve(l + 1, m - 1) + solve(m + 1, r));
        }
    }
    res = max(res, solve(l + 1, r));
    return dp[l][r] = res;
}

int main() {
    cin >> N;
    for (int i = 0; i < 3 * N; i++) {
        cin >> seq[i];
    }
    vector<int> cnt(N + 1, 0);
    for (int i = 0; i < 3 * N; i++) {
        int v = seq[i];
        pos[v][cnt[v]++] = i;
    }
    memset(dp, -1, sizeof(dp));
    cout << solve(0, 3 * N - 1) << endl;
    return 0;
}
