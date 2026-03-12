#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

const int MOD = 200003;
const int G = 2;  // primitive root modulo MOD

long long modpow(long long a, long long e, long long mod) {
    long long res = 1;
    while (e) {
        if (e & 1) res = res * a % mod;
        a = a * a % mod;
        e >>= 1;
    }
    return res;
}

void ntt(vector<long long>& a, bool invert, const vector<long long>& w, const vector<long long>& r) {
    int n = a.size();
    for (int i = 0; i < n; ++i) {
        int rev = 0;
        for (int j = 0; (1 << j) < n; ++j) {
            if (i & (1 << j)) rev |= (n >> (j + 1));
        }
        if (i < rev) swap(a[i], a[rev]);
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
        for (int i = 0; i < n; ++i) {
            a[i] = a[i] * r[n] % MOD;
        }
    }
}

vector<long long> multiply(vector<long long> a, vector<long long> b) {
    int n = 1;
    while (n < (int)a.size() + (int)b.size() - 1) n <<= 1;
    a.resize(n);
    b.resize(n);
    vector<long long> w(n + 1), r(n + 1);
    long long w0 = modpow(G, (MOD - 1) / n, MOD);
    long long r0 = modpow(n, MOD - 2, MOD);
    w[0] = 1;
    r[0] = 1;
    for (int i = 1; i <= n; ++i) {
        w[i] = w[i - 1] * w0 % MOD;
        r[i] = r[i - 1] * r0 % MOD;
    }
    ntt(a, false, w, r);
    ntt(b, false, w, r);
    for (int i = 0; i < n; ++i) {
        a[i] = a[i] * b[i] % MOD;
    }
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
    for (int i = 0; i < (int)sq.size(); ++i) {
        long long cnt = sq[i];
        if (i < MOD && freq[i] > 0) {
            cnt -= freq[i];
        }
        ans += (cnt % MOD) * i;
    }
    ans %= MOD;
    ans = ans * ((MOD + 1) / 2) % MOD;
    cout << ans << '\n';
    return 0;
}
