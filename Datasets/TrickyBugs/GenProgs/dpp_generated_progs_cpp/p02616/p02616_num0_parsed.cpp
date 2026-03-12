#include <iostream>
#include <vector>
#include <algorithm>
#include <queue>
using namespace std;

const long long MOD = 1000000007LL;

long long modpow(long long a, long long e) {
    long long res = 1;
    a %= MOD;
    while (e > 0) {
        if (e & 1) res = (res * a) % MOD;
        a = (a * a) % MOD;
        e >>= 1;
    }
    return res;
}

long long modinv(long long a) {
    return modpow(a, MOD - 2);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, K;
    cin >> N >> K;
    vector<long long> pos, neg;
    for (int i = 0; i < N; ++i) {
        long long x;
        cin >> x;
        if (x >= 0) pos.push_back(x);
        else neg.push_back(x);
    }

    sort(pos.begin(), pos.end());
    sort(neg.begin(), neg.end());

    if (pos.size() == 0) {
        if (K % 2 == 1) {
            sort(neg.rbegin(), neg.rend());
            long long ans = 1;
            for (int i = 0; i < K; ++i) {
                ans = (ans * (neg[i] % MOD + MOD)) % MOD;
            }
            cout << ans << '\n';
        } else {
            long long ans = 1;
            for (int i = 0; i < K; ++i) {
                ans = (ans * (neg[i] % MOD + MOD)) % MOD;
            }
            cout << ans << '\n';
        }
        return 0;
    }

    vector<long long> candidates;
    if (K % 2 == 1) {
        if (pos.empty()) {
            long long ans = 1;
            sort(neg.rbegin(), neg.rend());
            for (int i = 0; i < K; ++i) {
                ans = (ans * (neg[i] % MOD + MOD)) % MOD;
            }
            cout << ans << '\n';
            return 0;
        }
        candidates.push_back(pos.back());
        pos.pop_back();
        K--;
    }

    vector<long long> pairs;
    for (size_t i = 0; i + 1 < pos.size(); i += 2) {
        pairs.push_back(pos[i] * pos[i + 1]);
    }
    for (size_t i = 0; i + 1 < neg.size(); i += 2) {
        pairs.push_back(neg[i] * neg[i + 1]);
    }

    sort(pairs.rbegin(), pairs.rend());

    long long ans = (candidates.empty() ? 1 : (candidates[0] % MOD + MOD) % MOD);
    int need = K / 2;
    for (int i = 0; i < need && i < (int)pairs.size(); ++i) {
        long long p = pairs[i] % MOD;
        if (p < 0) p += MOD;
        ans = (ans * p) % MOD;
    }

    if (need > (int)pairs.size()) {
        vector<long long> all;
        for (long long v : pos) all.push_back(v);
        for (long long v : neg) all.push_back(v);
        sort(all.begin(), all.end(), [](long long a, long long b) {
            return abs(a) < abs(b);
        });
        ans = 1;
        for (int i = 0; i < K + (candidates.empty() ? 0 : 1); ++i) {
            long long v = all[i] % MOD;
            if (v < 0) v += MOD;
            ans = (ans * v) % MOD;
        }
    }

    cout << ans << '\n';
    return 0;
}
