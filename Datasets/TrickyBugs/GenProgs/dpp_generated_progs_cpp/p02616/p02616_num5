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
    vector<long long> arr(N);
    for (int i = 0; i < N; ++i) {
        cin >> arr[i];
    }

    if (N == K) {
        long long ans = 1;
        for (int i = 0; i < N; ++i) {
            ans = (ans * (arr[i] % MOD + MOD) % MOD) % MOD;
        }
        cout << ans << '\n';
        return 0;
    }

    vector<long long> pos, neg;
    for (long long v : arr) {
        if (v >= 0) pos.push_back(v);
        else neg.push_back(v);
    }

    sort(pos.rbegin(), pos.rend());
    sort(neg.begin(), neg.end());

    int pn = pos.size();
    int nn = neg.size();

    if (pn == 0 && K % 2 == 1) {
        sort(neg.rbegin(), neg.rend());
        long long ans = 1;
        for (int i = 0; i < K; ++i) {
            ans = (ans * (neg[i] % MOD + MOD) % MOD) % MOD;
        }
        cout << ans << '\n';
        return 0;
    }

    vector<long long> candidates;
    int pi = 0, ni = 0;
    while (K > 0) {
        if (K == 1) {
            if (pi < pn) candidates.push_back(pos[pi++]);
            else candidates.push_back(neg[ni++]);
            K--;
        } else {
            long long pos_pair = -1e18;
            long long neg_pair = -1e18;
            if (pi + 1 < pn) {
                pos_pair = pos[pi] * pos[pi + 1];
            }
            if (ni + 1 < nn) {
                neg_pair = neg[ni] * neg[ni + 1];
            }
            if (pos_pair >= neg_pair && pi + 1 < pn) {
                candidates.push_back(pos[pi]);
                candidates.push_back(pos[pi + 1]);
                pi += 2;
                K -= 2;
            } else if (ni + 1 < nn) {
                candidates.push_back(neg[ni]);
                candidates.push_back(neg[ni + 1]);
                ni += 2;
                K -= 2;
            } else {
                if (pi < pn) {
                    candidates.push_back(pos[pi++]);
                    K--;
                } else {
                    candidates.push_back(neg[ni++]);
                    K--;
                }
            }
        }
    }

    long long ans = 1;
    bool all_negative = true;
    for (long long v : candidates) {
        ans = (ans * (v % MOD + MOD) % MOD) % MOD;
        if (v >= 0) all_negative = false;
    }

    if (all_negative && pn > 0) {
        long long best = 1;
        vector<long long> mod_arr(N);
        for (int i = 0; i < N; ++i) mod_arr[i] = (arr[i] % MOD + MOD) % MOD;
        sort(arr.begin(), arr.end(), [](long long a, long long b) {
            return abs(a) < abs(b);
        });
        for (int i = 0; i < K; ++i) {
            best = (best * mod_arr[i]) % MOD;
        }
        cout << best << '\n';
        return 0;
    }

    cout << ans << '\n';
    return 0;
}
