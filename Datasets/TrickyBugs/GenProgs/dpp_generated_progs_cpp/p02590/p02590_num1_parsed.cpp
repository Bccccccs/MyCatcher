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
                long long v = a[i + j + half] * w[n / len * j] % MOD;
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

vector<long long> multiply(vector<long long> a, vector<long long> b) {
    int n = 1;
    while (n < a.size() + b.size()) n <<= 1;
    a.resize(n);
    b.resize(n);
    vector<long long> w(n), r(n + 1);
    long long wn = mod_pow(G, (MOD - 1) / n, MOD);
    long long inv_n = mod_pow(n, MOD - 2, MOD);
    w[0] = 1;
    for (int i = 1; i < n; ++i) w[i] = w[i - 1] * wn % MOD;
    r[0] = 1;
    for (int i = 1; i <= n; ++i) r[i] = r[i - 1] * inv_n % MOD;
    ntt(a, false, w, r);
    ntt(b, false, w, r);
    for (int i = 0; i < n; ++i) a[i] = a[i] * b[i] % MOD;
    ntt(a, true, w, r);
    return a;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    int N;
    cin >> N;
    vector<long long> freq(MOD, 0);
    long long total_sum = 0;
    for (int i = 0; i < N; ++i) {
        int x;
        cin >> x;
        freq[x]++;
        total_sum += x;
    }
    vector<long long> poly = freq;
    vector<long long> sq = multiply(poly, poly);
    long long ans = 0;
    for (int i = 0; i < sq.size(); ++i) {
        long long cnt = sq[i];
        if (i < MOD) {
            long long same = freq[i];
            cnt = (cnt - same + MOD) % MOD;
        }
        ans = (ans + cnt * (i % MOD)) % MOD;
    }
    ans = ans * ((MOD + 1) / 2) % MOD;
    cout << ans << '\n';
    return 0;
}
