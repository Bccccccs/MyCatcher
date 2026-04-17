#include <bits/stdc++.h>

#define rep(i, n) for (int i = 0; i < (n); i++)
using namespace std;
typedef long long ll;
const ll mod = 1e9 + 7;

int n, k;

ll modpow(ll a, ll b) {
  ll r = 1;
  while (b) {
    if (b & 1) r = r * a % mod;
    a = a * a % mod;
    b >>= 1;
  }
  return r;
}

ll dp[200005];

int main() {
  cin >> n >> k;
  ll ans = 0;
  for (int i = 1; i <= k; i++) dp[i] = modpow(k / i, n);

  for (int i = k; i > 0; --i)
    for (int j = 2; j < k / i + 1; ++j) dp[i] -= dp[i * j];

  rep(i, k + 1) ans += dp[i] * i, ans %= mod;

  cout << ans << endl;
}
