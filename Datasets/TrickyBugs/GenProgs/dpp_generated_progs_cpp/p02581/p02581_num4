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
    int idx = -1;
    for (int k = 0; k < 3; ++k) {
        if (pos[a][k] == l) {
            idx = k;
            break;
        }
    }
    int next_pos = pos[a][(idx + 1) % 3];
    int last_pos = pos[a][(idx + 2) % 3];
    if (next_pos > r) {
        res = solve(l + 1, r);
    } else if (next_pos == r) {
        res = 1 + solve(l + 1, r - 1);
    } else {
        res = max(res, solve(l + 1, r));
        if (next_pos < last_pos && last_pos <= r) {
            res = max(res, solve(l + 1, next_pos - 1) + solve(next_pos + 1, last_pos - 1) + solve(last_pos + 1, r) + 1);
        }
        if (next_pos <= r) {
            res = max(res, solve(l + 1, next_pos - 1) + solve(next_pos + 1, r));
        }
    }
    return dp[l][r] = res;
}

int main() {
    cin >> N;
    for (int i = 0; i < 3 * N; ++i) {
        cin >> seq[i];
    }
    vector<int> cnt(N + 1, 0);
    for (int i = 0; i < 3 * N; ++i) {
        int v = seq[i];
        pos[v][cnt[v]] = i;
        cnt[v]++;
    }
    memset(dp, -1, sizeof(dp));
    cout << solve(0, 3 * N - 1) << endl;
    return 0;
}
