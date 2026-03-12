#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

const int MOD = 200003;
const int G = 2;  // primitive root of MOD (prime)

long long modpow(long long a, long long e) {
    long long res = 1;
    while (e) {
        if (e & 1) res = res * a % MOD;
        a = a * a % MOD;
        e >>= 1;
    }
    return res;
}

void fft(vector<long long>& a, bool invert) {
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

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    vector<int> A(N);
    for (int i = 0; i < N; ++i) {
        cin >> A[i];
    }

    vector<long long> freq(MOD, 0);
    for (int x : A) {
        freq[x]++;
    }

    int sz = 1;
    while (sz < 2 * MOD) sz <<= 1;
    vector<long long> fa(sz, 0);
    for (int i = 0; i < MOD; ++i) {
        fa[i] = freq[i];
    }

    fft(fa, false);
    for (int i = 0; i < sz; ++i) {
        fa[i] = fa[i] * fa[i] % MOD;
    }
    fft(fa, true);

    long long total = 0;
    for (int i = 0; i < sz; ++i) {
        long long pairs = fa[i];
        if (i % MOD == 0) {
            pairs = (pairs - freq[0] * freq[0] % MOD + MOD) % MOD;
        }
        pairs = pairs * modpow(2, MOD - 2) % MOD;
        total = (total + pairs * (i % MOD)) % MOD;
    }

    cout << total << '\n';
    return 0;
}
