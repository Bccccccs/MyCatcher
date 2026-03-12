#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>
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
    return (res + MOD) % MOD;
}

long long modinv(long long a) {
    return modpow(a, MOD - 2);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, K;
    cin >> N >> K;
    vector<long long> pos, neg;
    int zero_count = 0;

    for (int i = 0; i < N; ++i) {
        long long x;
        cin >> x;
        if (x > 0) pos.push_back(x);
        else if (x < 0) neg.push_back(x);
        else zero_count++;
    }

    sort(pos.rbegin(), pos.rend());
    sort(neg.begin(), neg.end());

    int ps = pos.size();
    int ns = neg.size();

    if (ps + ns < K) {
        cout << "0\n";
        return 0;
    }

    if (ps == 0) {
        if (K % 2 == 1) {
            if (zero_count > 0) {
                cout << "0\n";
                return 0;
            } else {
                sort(neg.rbegin(), neg.rend());
                long long res = 1;
                for (int i = 0; i < K; ++i) {
                    res = (res * (neg[i] % MOD + MOD)) % MOD;
                }
                cout << res << "\n";
                return 0;
            }
        } else {
            long long res = 1;
            for (int i = 0; i < K; ++i) {
                res = (res * (neg[i] % MOD + MOD)) % MOD;
            }
            cout << res << "\n";
            return 0;
        }
    }

    vector<long long> candidates;
    int pi = 0, ni = 0;
    while (pi + ni < K) {
        if (pi < ps && ni < ns) {
            if (pos[pi] >= -neg[ni]) {
                candidates.push_back(pos[pi]);
                pi++;
            } else {
                candidates.push_back(neg[ni]);
                ni++;
            }
        } else if (pi < ps) {
            candidates.push_back(pos[pi]);
            pi++;
        } else {
            candidates.push_back(neg[ni]);
            ni++;
        }
    }

    if (ni % 2 == 0) {
        long long res = 1;
        for (long long v : candidates) {
            res = (res * (v % MOD + MOD)) % MOD;
        }
        cout << res << "\n";
        return 0;
    }

    long long cand_prod = 1;
    for (long long v : candidates) {
        cand_prod = (cand_prod * (v % MOD + MOD)) % MOD;
    }

    long long best = cand_prod;

    if (pi > 0 && ni < ns) {
        long long try1 = cand_prod;
        if (pi > 0) {
            try1 = (try1 * modinv(pos[pi - 1] % MOD + MOD)) % MOD;
            try1 = (try1 * (neg[ni] % MOD + MOD)) % MOD;
        }
        if (try1 > best) best = try1;
    }

    if (ni > 0 && pi < ps) {
        long long try2 = cand_prod;
        if (ni > 0) {
            try2 = (try2 * modinv(neg[ni - 1] % MOD + MOD)) % MOD;
            try2 = (try2 * (pos[pi] % MOD + MOD)) % MOD;
        }
        if (try2 > best) best = try2;
    }

    if (best < 0 && zero_count > 0) {
        best = 0;
    }

    cout << best << "\n";
    return 0;
}
