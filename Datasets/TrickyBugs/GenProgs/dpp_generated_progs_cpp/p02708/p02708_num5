#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

const int MOD = 1000000007;

vector<int> fact, inv_fact;

int mod_pow(int a, int e) {
    int res = 1;
    while (e) {
        if (e & 1) res = 1LL * res * a % MOD;
        a = 1LL * a * a % MOD;
        e >>= 1;
    }
    return res;
}

void precompute(int n) {
    fact.resize(n + 1);
    inv_fact.resize(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; i++) {
        fact[i] = 1LL * fact[i - 1] * i % MOD;
    }
    inv_fact[n] = mod_pow(fact[n], MOD - 2);
    for (int i = n - 1; i >= 0; i--) {
        inv_fact[i] = 1LL * inv_fact[i + 1] * (i + 1) % MOD;
    }
}

int comb(int n, int k) {
    if (k < 0 || k > n) return 0;
    return 1LL * fact[n] * inv_fact[k] % MOD * inv_fact[n - k] % MOD;
}

int main() {
    int N, K;
    cin >> N >> K;
    precompute(N + 1);
    
    int ans = 0;
    for (int i = K; i <= N + 1; i++) {
        long long min_sum = 1LL * i * (i - 1) / 2;
        long long max_sum = 1LL * i * (2 * N - i + 1) / 2;
        int ways = (max_sum - min_sum + 1) % MOD;
        ans = (ans + ways) % MOD;
    }
    
    cout << ans << endl;
    return 0;
}
