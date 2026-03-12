#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

const int MOD = 1000000007;

int modpow(int a, int e) {
    int res = 1;
    while (e) {
        if (e & 1) res = 1LL * res * a % MOD;
        a = 1LL * a * a % MOD;
        e >>= 1;
    }
    return res;
}

int modinv(int a) {
    return modpow(a, MOD - 2);
}

int main() {
    int N, K;
    cin >> N >> K;
    
    vector<int> fact(N + 2), invfact(N + 2);
    fact[0] = 1;
    for (int i = 1; i <= N + 1; ++i) {
        fact[i] = 1LL * fact[i - 1] * i % MOD;
    }
    invfact[N + 1] = modinv(fact[N + 1]);
    for (int i = N; i >= 0; --i) {
        invfact[i] = 1LL * invfact[i + 1] * (i + 1) % MOD;
    }
    
    auto comb = [&](int n, int k) -> int {
        if (k < 0 || k > n) return 0;
        return 1LL * fact[n] * invfact[k] % MOD * invfact[n - k] % MOD;
    };
    
    int ans = 0;
    for (int i = K; i <= N + 1; ++i) {
        long long min_sum = 1LL * i * (i - 1) / 2;
        long long max_sum = 1LL * i * (2 * N - i + 1) / 2;
        long long possible_sums = max_sum - min_sum + 1;
        possible_sums %= MOD;
        ans = (ans + possible_sums) % MOD;
    }
    
    cout << ans << endl;
    return 0;
}
