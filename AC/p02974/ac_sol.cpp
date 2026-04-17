#include <bits/stdc++.h>
using namespace std;

#define rep(i, n) REP(i, 0, n)
#define ALL(v) v.begin(), v.end()
#define MSG(a) cout << #a << " " << a << endl;
#define REP(i, x, n) for (int i = x; i < n; i++)
#define OP(m) cout << m << endl;

int mod = 1000000007;

#define mul(a, b) ((a % mod) * (b % mod)) % mod

long long int dp[55][55][2600] = {0};

int main()
{
    int n, score;
    cin >> n >> score;

    dp[0][0][0] = 1;

    rep(i, n + 1)
    {
        rep(j, i + 1)
        {
            rep(k, score + 1)
            {
                dp[i + 1][j][k + j * 2] += dp[i][j][k] % mod;

                dp[i + 1][j + 1][k + (j + 1) * 2] += dp[i][j][k] % mod;

                dp[i + 1][j][k + j * 2] += mul(dp[i][j][k], 2 * j);

                if (j >= 1)
                {
                    dp[i + 1][j - 1][k + (j - 1) * 2] += mul(mul(dp[i][j][k], j), j);
                }
            }
        }
    }

    OP(dp[n][0][score] % mod)

    return 0;
}