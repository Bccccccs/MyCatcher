#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

const int MOD = 200003;
const int G = 2;  // primitive root modulo MOD
const int MAXN = 1 << 19;  // power of two >= 2*MOD

long long pow_mod(long long a, long long b, long long mod) {
    long long res = 1;
    while (b) {
        if (b & 1) res = res * a % mod;
        a = a * a % mod;
        b >>= 1;
    }
    return res;
}

void fft(vector<long long> &a, bool invert) {
    int n = a.size();
    for (int i = 1, j = 0; i < n; i++) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1)
            j ^= bit;
        j ^= bit;
        if (i < j)
            swap(a[i], a[j]);
    }
    for (int len = 2; len <= n; len <<= 1) {
        long long wlen = pow_mod(G, (MOD - 1) / len, MOD);
        if (invert)
            wlen = pow_mod(wlen, MOD - 2, MOD);
        for (int i = 0; i < n; i += len) {
            long long w = 1;
            for (int j = 0; j < len / 2; j++) {
                long long u = a[i + j];
                long long v = a[i + j + len / 2] * w % MOD;
                a[i + j] = (u + v) % MOD;
                a[i + j + len / 2] = (u - v + MOD) % MOD;
                w = w * wlen % MOD;
            }
        }
    }
    if (invert) {
        long long inv_n = pow_mod(n, MOD - 2, MOD);
        for (long long &x : a)
            x = x * inv_n % MOD;
    }
}

vector<long long> multiply(vector<long long> const &a, vector<long long> const &b) {
    vector<long long> fa(a.begin(), a.end()), fb(b.begin(), b.end());
    int n = 1;
    while (n < a.size() + b.size())
        n <<= 1;
    fa.resize(n);
    fb.resize(n);
    fft(fa, false);
    fft(fb, false);
    for (int i = 0; i < n; i++)
        fa[i] = fa[i] * fb[i] % MOD;
    fft(fa, true);
    return fa;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    int N;
    cin >> N;
    vector<long long> freq(MOD, 0);
    long long total_sum = 0;
    for (int i = 0; i < N; i++) {
        int x;
        cin >> x;
        freq[x]++;
        total_sum += x;
    }
    vector<long long> poly = freq;
    vector<long long> conv = multiply(poly, poly);
    long long sum_sq = 0;
    for (int i = 0; i < MOD; i++) {
        sum_sq += freq[i] * i % MOD * i % MOD;
        if (sum_sq >= MOD) sum_sq %= MOD;
    }
    long long ans = 0;
    for (int i = 0; i < conv.size(); i++) {
        long long pairs = conv[i];
        if (i < MOD) {
            pairs = (pairs - freq[i % MOD] + MOD) % MOD;
        } else {
            int idx = i % MOD;
            pairs = (pairs - freq[idx] + MOD) % MOD;
        }
        if (pairs % 2 != 0) pairs += MOD;
        pairs /= 2;
        ans = (ans + pairs * (i % MOD)) % MOD;
    }
    ans = (ans - sum_sq + MOD) % MOD;
    long long inv2 = (MOD + 1) / 2;
    ans = ans * inv2 % MOD;
    cout << ans << "\n";
    return 0;
}
