#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

const int MOD = 1000000007;

int modPow(int a, int e, int mod) {
    int res = 1;
    while (e) {
        if (e & 1) res = 1LL * res * a % mod;
        a = 1LL * a * a % mod;
        e >>= 1;
    }
    return res;
}

int modInv(int a, int mod) {
    return modPow(a, mod - 2, mod);
}

int main() {
    int N, K;
    cin >> N >> K;

    vector<int> fact(N + 2), invFact(N + 2);
    fact[0] = 1;
    for (int i = 1; i <= N + 1; ++i) {
        fact[i] = 1LL * fact[i - 1] * i % MOD;
    }
    invFact[N + 1] = modInv(fact[N + 1], MOD);
    for (int i = N; i >= 0; --i) {
        invFact[i] = 1LL * invFact[i + 1] * (i + 1) % MOD;
    }

    auto comb = [&](int n, int r) -> int {
        if (r < 0 || r > n) return 0;
        return 1LL * fact[n] * invFact[r] % MOD * invFact[n - r] % MOD;
    };

    int ans = 0;
    for (int i = K; i <= N + 1; ++i) {
        long long min_sum = 1LL * i * (i - 1) / 2;
        long long max_sum = 1LL * i * (2 * N - i + 1) / 2;
        long long count = max_sum - min_sum + 1;
        ans = (ans + count % MOD) % MOD;
    }

    cout << ans << endl;
    return 0;
}
