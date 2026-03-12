#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

const int MAXN = 2005;
int dp[MAXN][MAXN];
int pos[MAXN][3];
int seq[MAXN * 3];
int N;

int solve(int l, int r) {
    if (l > r) return 0;
    if (dp[l][r] != -1) return dp[l][r];
    int res = 0;
    int a = seq[l];
    int idx1 = -1, idx2 = -1;
    for (int k = 0; k < 3; ++k) {
        if (pos[a][k] == l) idx1 = k;
        else if (pos[a][k] == r) idx2 = k;
    }
    if (idx1 != -1 && idx2 != -1) {
        int p1 = pos[a][(idx1 + 1) % 3];
        int p2 = pos[a][(idx1 + 2) % 3];
        if (p1 > p2) swap(p1, p2);
        if (p1 >= l && p2 <= r) {
            res = max(res, 1 + solve(p1 + 1, p2 - 1) + solve(l + 1, p1 - 1) + solve(p2 + 1, r - 1));
        }
    }
    res = max(res, solve(l + 1, r));
    res = max(res, solve(l, r - 1));
    return dp[l][r] = res;
}

int main() {
    cin >> N;
    int m = 3 * N;
    for (int i = 0; i < m; ++i) {
        cin >> seq[i];
    }
    vector<int> cnt(N + 1, 0);
    for (int i = 0; i < m; ++i) {
        int v = seq[i];
        pos[v][cnt[v]++] = i;
    }
    memset(dp, -1, sizeof(dp));
    cout << solve(0, m - 1) << endl;
    return 0;
}
