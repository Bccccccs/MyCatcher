#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

const int MOD = 1000000007;

int modPow(long long a, long long e) {
    long long res = 1;
    while (e) {
        if (e & 1) res = res * a % MOD;
        a = a * a % MOD;
        e >>= 1;
    }
    return (int)res;
}

int main() {
    int N, K;
    cin >> N >> K;
    
    vector<int> fact(N + 2), invFact(N + 2);
    fact[0] = 1;
    for (int i = 1; i <= N + 1; i++) {
        fact[i] = (long long)fact[i - 1] * i % MOD;
    }
    invFact[N + 1] = modPow(fact[N + 1], MOD - 2);
    for (int i = N; i >= 0; i--) {
        invFact[i] = (long long)invFact[i + 1] * (i + 1) % MOD;
    }
    
    auto comb = [&](int n, int r) -> int {
        if (r < 0 || r > n) return 0;
        return (long long)fact[n] * invFact[r] % MOD * invFact[n - r] % MOD;
    };
    
    long long ans = 0;
    for (int i = K; i <= N + 1; i++) {
        long long min_sum = (long long)i * (i - 1) / 2;
        long long max_sum = (long long)i * (2 * N - i + 1) / 2;
        long long cnt = max_sum - min_sum + 1;
        ans = (ans + cnt % MOD) % MOD;
    }
    
    cout << ans << endl;
    return 0;
}
