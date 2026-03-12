#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

const int MOD = 200003;
const int G = 2;  // primitive root modulo MOD

long long mod_pow(long long a, long long b, int mod) {
    long long res = 1;
    while (b) {
        if (b & 1) res = res * a % mod;
        a = a * a % mod;
        b >>= 1;
    }
    return res;
}

void ntt(vector<long long>& a, bool invert, const vector<long long>& w, const vector<long long>& r) {
    int n = a.size();
    for (int i = 1, j = 0; i < n; ++i) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) swap(a[i], a[j]);
    }
    for (int len = 2; len <= n; len <<= 1) {
        int half = len >> 1;
        for (int i = 0; i < n; i += len) {
            for (int j = 0; j < half; ++j) {
                long long u = a[i + j];
                long long v = a[i + j + half] * w[j * (n / len)] % MOD;
                a[i + j] = (u + v) % MOD;
                a[i + j + half] = (u - v + MOD) % MOD;
            }
        }
    }
    if (invert) {
        reverse(a.begin() + 1, a.end());
        long long inv_n = r[n];
        for (long long& x : a) x = x * inv_n % MOD;
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int N;
    cin >> N;
    vector<int> A(N);
    for (int i = 0; i < N; ++i) cin >> A[i];
    
    vector<long long> freq(MOD, 0);
    long long zero_count = 0;
    for (int x : A) {
        if (x == 0) zero_count++;
        else freq[x]++;
    }
    
    int m = 1;
    while (m < 2 * MOD) m <<= 1;
    
    vector<long long> w(m), r(m + 1);
    long long w0 = mod_pow(G, (MOD - 1) / m, MOD);
    w[0] = 1;
    for (int i = 1; i < m; ++i) w[i] = w[i - 1] * w0 % MOD;
    r[1] = 1;
    for (int i = 2; i <= m; ++i) r[i] = (MOD - MOD / i) * r[MOD % i] % MOD;
    
    vector<long long> fa(m, 0);
    for (int i = 0; i < MOD; ++i) fa[i] = freq[i];
    
    ntt(fa, false, w, r);
    for (int i = 0; i < m; ++i) fa[i] = fa[i] * fa[i] % MOD;
    ntt(fa, true, w, r);
    
    long long total = 0;
    for (int i = 0; i < m; ++i) {
        long long pairs = fa[i];
        if (i % MOD == 0) {
            pairs = (pairs - zero_count * zero_count % MOD + MOD) % MOD;
        }
        if (pairs % 2 != 0) pairs += MOD;
        pairs /= 2;
        total = (total + pairs * (i % MOD)) % MOD;
    }
    
    total = (total + (zero_count * (zero_count - 1) / 2 % MOD) * MOD) % MOD;
    
    cout << total << '\n';
    return 0;
}
