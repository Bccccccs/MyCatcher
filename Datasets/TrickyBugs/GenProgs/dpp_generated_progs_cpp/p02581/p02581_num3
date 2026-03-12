#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

const int MAXN = 2005;
int dp[MAXN][MAXN];
int pos[MAXN][3];
int seq[3*MAXN];
int N;

int solve(int l, int r) {
    if (l > r) return 0;
    if (dp[l][r] != -1) return dp[l][r];
    
    int res = 0;
    
    // Option 1: match the leftmost card with its pair from the right
    int val = seq[l];
    // find the two other positions of this value within [l, r]
    int cnt = 0;
    int other[2];
    for (int k = 0; k < 3; k++) {
        int p = pos[val][k];
        if (p >= l && p <= r && p != l) {
            other[cnt++] = p;
        }
    }
    
    if (cnt == 2) {
        int p1 = other[0], p2 = other[1];
        if (p1 > p2) swap(p1, p2);
        // we can match l with p1 and p2? Actually we need to remove symmetric pairs.
        // Instead, consider matching l with r if they are same value
    }
    
    // Try matching l and r if they are same
    if (seq[l] == seq[r]) {
        // remove l and r
        res = max(res, 1 + solve(l+1, r-1));
    }
    
    // Try splitting at some k
    for (int k = l; k < r; k++) {
        res = max(res, solve(l, k) + solve(k+1, r));
    }
    
    // Try operation where we pick i-th from left and i-th from right
    // Let's think: current segment length = r-l+1
    int len = r - l + 1;
    for (int i = 1; i <= len/2; i++) {
        int left_idx = l + i - 1;
        int right_idx = r - i + 1;
        if (left_idx >= right_idx) break;
        if (seq[left_idx] == seq[right_idx]) {
            res = max(res, 1 + solve(left_idx+1, right_idx-1));
        }
    }
    
    dp[l][r] = res;
    return res;
}

int main() {
    cin >> N;
    for (int i = 0; i < 3*N; i++) {
        cin >> seq[i];
    }
    
    // record positions of each value
    vector<int> cnt(N+1, 0);
    for (int i = 0; i < 3*N; i++) {
        int v = seq[i];
        pos[v][cnt[v]++] = i;
    }
    
    memset(dp, -1, sizeof(dp));
    cout << solve(0, 3*N - 1) << endl;
    
    return 0;
}
