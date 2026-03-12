#include <iostream>
#include <vector>
#include <algorithm>
#include <queue>
#include <functional>
#include <cmath>
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
    int zeroCount = 0;
    for (int i = 0; i < N; ++i) {
        long long x;
        cin >> x;
        if (x > 0) pos.push_back(x);
        else if (x < 0) neg.push_back(x);
        else zeroCount++;
    }

    sort(pos.begin(), pos.end());
    sort(neg.begin(), neg.end());

    if (pos.size() + neg.size() < K) {
        cout << "0\n";
        return 0;
    }

    if (pos.size() == 0) {
        if (K % 2 == 1) {
            if (zeroCount > 0) {
                cout << "0\n";
                return 0;
            } else {
                long long res = 1;
                sort(neg.begin(), neg.end(), greater<long long>());
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
    for (long long v : pos) candidates.push_back(v);
    for (long long v : neg) candidates.push_back(v);

    sort(candidates.begin(), candidates.end(), [](long long a, long long b) {
        return abs(a) > abs(b);
    });

    long long res = 1;
    int negCnt = 0;
    int lastNeg = -1, lastPos = -1;
    int firstNeg = -1, firstPos = -1;

    for (int i = 0; i < K; ++i) {
        long long val = candidates[i];
        res = (res * (val % MOD + MOD)) % MOD;
        if (val < 0) {
            negCnt++;
            lastNeg = i;
            if (firstNeg == -1) firstNeg = i;
        } else {
            lastPos = i;
            if (firstPos == -1) firstPos = i;
        }
    }

    if (negCnt % 2 == 0) {
        cout << res << "\n";
        return 0;
    }

    long long best = res;

    if (lastPos != -1 && firstNeg != -1 && firstNeg < K) {
        long long cand1 = res;
        cand1 = (cand1 * modinv((candidates[lastPos] % MOD + MOD) % MOD)) % MOD;
        if (K < candidates.size()) {
            for (int j = K; j < candidates.size(); ++j) {
                if (candidates[j] < 0) {
                    cand1 = (cand1 * (candidates[j] % MOD + MOD)) % MOD;
                    best = max(best, cand1);
                    break;
                }
            }
        }
    }

    if (lastNeg != -1 && firstPos != -1 && firstPos < K) {
        long long cand2 = res;
        cand2 = (cand2 * modinv((candidates[lastNeg] % MOD + MOD) % MOD)) % MOD;
        if (K < candidates.size()) {
            for (int j = K; j < candidates.size(); ++j) {
                if (candidates[j] > 0) {
                    cand2 = (cand2 * (candidates[j] % MOD + MOD)) % MOD;
                    best = max(best, cand2);
                    break;
                }
            }
        }
    }

    if (best < 0 && zeroCount > 0) best = 0;
    cout << (best % MOD + MOD) % MOD << "\n";
    return 0;
}
