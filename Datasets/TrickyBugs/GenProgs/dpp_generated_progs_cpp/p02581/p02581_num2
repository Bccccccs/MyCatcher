#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

const int MAXN = 2005;
int dp[MAXN][MAXN];
int pos[MAXN][3];
int seq[3 * MAXN];

int main() {
    int N;
    cin >> N;
    for (int i = 0; i < 3 * N; ++i) {
        cin >> seq[i];
    }

    for (int v = 1; v <= N; ++v) {
        int cnt = 0;
        for (int i = 0; i < 3 * N; ++i) {
            if (seq[i] == v) {
                pos[v][cnt++] = i;
            }
        }
    }

    memset(dp, -1, sizeof(dp));
    dp[0][3 * N] = 0;

    for (int l = 0; l <= 3 * N; ++l) {
        for (int r = 3 * N; r >= l; --r) {
            if (dp[l][r] < 0) continue;
            if (l == r) continue;

            int len = r - l;
            if (len % 2 != 0) continue;

            for (int v = 1; v <= N; ++v) {
                int p1 = pos[v][0];
                int p2 = pos[v][1];
                int p3 = pos[v][2];
                if (p1 < l || p3 >= r) continue;

                int nl = l, nr = r;
                bool ok = true;
                int add = 0;

                if (p1 == l && p3 == r - 1) {
                    add = 1;
                    nl = l + 1;
                    nr = r - 1;
                    p2 = pos[v][1];
                    if (p2 >= nl && p2 < nr) {
                        if (p2 == nl && p2 == nr - 1) {
                            add = 2;
                            nl++;
                            nr--;
                        } else if (p2 == nl) {
                            nl++;
                        } else if (p2 == nr - 1) {
                            nr--;
                        }
                    }
                } else if (p1 == l && p2 == l + 1) {
                    nl = l + 2;
                    if (p3 == nr - 1) {
                        add = 1;
                        nr--;
                    } else if (p3 == nr - 2) {
                        add = 1;
                        nr -= 2;
                    }
                } else if (p2 == r - 2 && p3 == r - 1) {
                    nr = r - 2;
                    if (p1 == nl) {
                        add = 1;
                        nl++;
                    } else if (p1 == nl + 1) {
                        add = 1;
                        nl += 2;
                    }
                } else if (p1 == l && p2 == r - 2 && p3 == r - 1) {
                    add = 1;
                    nl = l + 1;
                    nr = r - 2;
                } else if (p1 == l && p2 == l + 1 && p3 == r - 1) {
                    add = 1;
                    nl = l + 2;
                    nr = r - 1;
                } else if (p1 == l && p2 == r - 2 && p3 == r - 1) {
                    add = 1;
                    nl = l + 1;
                    nr = r - 2;
                } else {
                    continue;
                }

                if (nl > nr) continue;
                if ((nr - nl) % 2 != 0) continue;
                dp[nl][nr] = max(dp[nl][nr], dp[l][r] + add);
            }

            if (l + 1 <= r - 1) {
                dp[l + 1][r - 1] = max(dp[l + 1][r - 1], dp[l][r]);
            }
        }
    }

    int ans = 0;
    for (int i = 0; i <= 3 * N; ++i) {
        ans = max(ans, dp[i][i]);
    }
    cout << ans << endl;

    return 0;
}
