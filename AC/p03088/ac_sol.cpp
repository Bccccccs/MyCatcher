#include <bits/stdc++.h>

using namespace std;
using ll = long long;

int main() {
	const ll MOD = 1e9 + 7;
	const int A = 0, C = 1, G = 2, T = 3;

	int N;
	cin >> N;

	int dp[110][4][4][4] = { 0 };
	dp[0][T][T][T] = 1;
	ll res = 0;
	for (int i = 1; i <= N; ++i) {
		for (int j = 0; j < 4; ++j) {
			for (int k = 0; k < 4; ++k) {
				for (int l = 0; l < 4; ++l) {
					for (int m = 0; m < 4; ++m) {
						if (j == A && k == G && l == C) { continue; }
						if (j == G && k == A && l == C) { continue; }
						if (j == A && k == C && l == G) { continue; }
						if (j == A && l == G && m == C) { continue; }
						if (j == A && k == G && m == C) { continue; }

						(dp[i][j][k][l] += dp[i - 1][k][l][m]) %= MOD;
						if (i == N) {
							(res += dp[N - 1][k][l][m]) %= MOD;
						}
					}
				}
			}
		}
	}

	cout << res % MOD << endl;

	return 0;
}
