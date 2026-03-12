#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

const int MOD = 200003;
const int G = 2; // primitive root modulo MOD

long long mod_pow(long long a, long long b, int mod) {
    long long res = 1;
    while (b) {
        if (b & 1) res = res * a % mod;
        a = a * a % mod;
        b >>= 1;
    }
    return res;
}

void ntt(vector<long long>& a, bool invert, const vector<long long>& w, const vector<long long>& rpow) {
    int n = a.size();
    for (int i = 1, j = 0; i < n; ++i) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) swap(a[i], a[j]);
    }

    for (int len = 2; len <= n; len <<= 1) {
        int wlen = invert ? w[n - n/len] : w[n/len];
        for (int i = 0; i < n; i += len) {
            long long w = 1;
            for (int j = 0; j < len/2; ++j) {
                long long u = a[i+j];
                long long v = a[i+j+len/2] * w % MOD;
                a[i+j] = (u + v) % MOD;
                a[i+j+len/2] = (u - v + MOD) % MOD;
                w = w * wlen % MOD;
            }
        }
    }

    if (invert) {
        long long inv_n = rpow[n];
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

    int p = MOD - 1;
    vector<int> log_table(p, -1);
    long long g_pow = 1;
    for (int i = 0; i < p; ++i) {
        log_table[g_pow] = i;
        g_pow = g_pow * G % MOD;
    }

    int sz = 1;
    while (sz < 2 * p) sz <<= 1;

    vector<long long> poly(sz, 0);
    for (int i = 1; i < MOD; ++i) {
        if (freq[i] > 0) {
            poly[log_table[i]] += freq[i];
        }
    }

    vector<long long> w(sz + 1), rpow(sz + 1);
    long long primitive_root = mod_pow(G, p / sz, MOD);
    w[0] = 1;
    for (int i = 1; i <= sz; ++i) w[i] = w[i-1] * primitive_root % MOD;
    rpow[0] = 1;
    long long inv_sz = mod_pow(sz, MOD - 2, MOD);
    for (int i = 1; i <= sz; ++i) rpow[i] = rpow[i-1] * inv_sz % MOD;

    ntt(poly, false, w, rpow);
    for (int i = 0; i < sz; ++i) poly[i] = poly[i] * poly[i] % MOD;
    ntt(poly, true, w, rpow);

    long long total = 0;
    for (int i = 0; i < sz; ++i) {
        if (poly[i] == 0) continue;
        int exp_val = i % p;
        long long orig_val = mod_pow(G, exp_val, MOD);
        long long pairs = poly[i];
        if (exp_val == 0) {
            int idx_zero = 0;
            long long cnt_zero = freq[idx_zero];
            pairs -= cnt_zero * cnt_zero;
        }
        total = (total + orig_val * (pairs / 2)) % MOD;
    }

    long long zero_contrib = 0;
    if (zero_count > 0) {
        for (int i = 1; i < MOD; ++i) {
            if (freq[i] > 0) {
                zero_contrib = (zero_contrib + zero_count * freq[i] % MOD * i) % MOD;
            }
        }
    }

    total = (total + zero_contrib) % MOD;
    cout << total << '\n';

    return 0;
}
