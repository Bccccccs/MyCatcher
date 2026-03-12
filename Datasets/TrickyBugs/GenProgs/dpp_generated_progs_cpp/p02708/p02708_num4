#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

const long long MOD = 1000000007;

long long mod_pow(long long base, long long exp, long long mod) {
    long long result = 1;
    while (exp > 0) {
        if (exp & 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp >>= 1;
    }
    return result;
}

long long mod_inv(long long x, long long mod) {
    return mod_pow(x, mod - 2, mod);
}

vector<long long> fact;
vector<long long> inv_fact;

void precompute_factorials(int n) {
    fact.resize(n + 1);
    inv_fact.resize(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; i++) {
        fact[i] = fact[i - 1] * i % MOD;
    }
    inv_fact[n] = mod_inv(fact[n], MOD);
    for (int i = n - 1; i >= 0; i--) {
        inv_fact[i] = inv_fact[i + 1] * (i + 1) % MOD;
    }
}

long long comb(int n, int r) {
    if (r < 0 || r > n) return 0;
    return fact[n] * inv_fact[r] % MOD * inv_fact[n - r] % MOD;
}

int main() {
    int N, K;
    cin >> N >> K;

    precompute_factorials(N);

    long long ans = 0;
    for (int i = K; i <= N + 1; i++) {
        long long min_sum = (long long)i * (i - 1) / 2;
        long long max_sum = (long long)i * (2 * N - i + 1) / 2;
        long long count = max_sum - min_sum + 1;
        ans = (ans + count) % MOD;
    }

    cout << ans << endl;

    return 0;
}
