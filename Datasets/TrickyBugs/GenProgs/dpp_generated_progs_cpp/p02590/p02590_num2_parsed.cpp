#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

const int MOD = 200003;
const int G = 2; // primitive root modulo MOD

long long modpow(long long a, long long e) {
    long long res = 1;
    while (e) {
        if (e & 1) res = res * a % MOD;
        a = a * a % MOD;
        e >>= 1;
    }
    return res;
}

void ntt(vector<long long>& a, bool invert) {
    int n = a.size();
    for (int i = 1, j = 0; i < n; ++i) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1)
            j ^= bit;
        j ^= bit;
        if (i < j)
            swap(a[i], a[j]);
    }

    for (int len = 2; len <= n; len <<= 1) {
        long long wlen = modpow(G, (MOD - 1) / len);
        if (invert)
            wlen = modpow(wlen, MOD - 2);
        for (int i = 0; i < n; i += len) {
            long long w = 1;
            for (int j = 0; j < len / 2; ++j) {
                long long u = a[i + j];
                long long v = a[i + j + len / 2] * w % MOD;
                a[i + j] = (u + v) % MOD;
                a[i + j + len / 2] = (u - v + MOD) % MOD;
                w = w * wlen % MOD;
            }
        }
    }

    if (invert) {
        long long inv_n = modpow(n, MOD - 2);
        for (long long& x : a)
            x = x * inv_n % MOD;
    }
}

vector<long long> multiply(vector<long long> const& a, vector<long long> const& b) {
    vector<long long> fa(a.begin(), a.end()), fb(b.begin(), b.end());
    int n = 1;
    while (n < a.size() + b.size())
        n <<= 1;
    fa.resize(n);
    fb.resize(n);
    ntt(fa, false);
    ntt(fb, false);
    for (int i = 0; i < n; ++i)
        fa[i] = fa[i] * fb[i] % MOD;
    ntt(fa, true);
    return fa;
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

    vector<long long> conv = multiply(freq, freq);

    long long ans = 0;
    for (int i = 0; i < conv.size(); ++i) {
        long long pairs = conv[i];
        if (i < MOD) {
            long long cnt = freq[i];
            pairs = (pairs - cnt + MOD) % MOD;
            pairs = pairs * modpow(2, MOD - 2) % MOD;
        } else {
            pairs = 0;
        }
        ans = (ans + pairs * (i % MOD)) % MOD;
    }

    cout << ans << '\n';
    return 0;
}
