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

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int N, K;
    cin >> N >> K;
    vector<long long> pos, neg;
    int zeroCount = 0;
    
    for (int i = 0; i < N; i++) {
        long long x;
        cin >> x;
        if (x > 0) pos.push_back(x);
        else if (x < 0) neg.push_back(x);
        else zeroCount++;
    }
    
    sort(pos.rbegin(), pos.rend());
    sort(neg.begin(), neg.end());
    
    int pn = pos.size();
    int nn = neg.size();
    
    if (pn + nn < K) {
        cout << "0\n";
        return 0;
    }
    
    if (pn == 0) {
        if (K % 2 == 0) {
            if (nn >= K) {
                long long ans = 1;
                for (int i = 0; i < K; i++) {
                    ans = (ans * (neg[nn - 1 - i] % MOD + MOD)) % MOD;
                }
                cout << ans << "\n";
            } else if (zeroCount > 0) {
                cout << "0\n";
            } else {
                long long ans = 1;
                for (int i = 0; i < K; i++) {
                    ans = (ans * (neg[i] % MOD + MOD)) % MOD;
                }
                cout << ans << "\n";
            }
        } else {
            if (zeroCount > 0) {
                cout << "0\n";
            } else {
                long long ans = 1;
                for (int i = 0; i < K; i++) {
                    ans = (ans * (neg[nn - 1 - i] % MOD + MOD)) % MOD;
                }
                cout << ans << "\n";
            }
        }
        return 0;
    }
    
    vector<long long> selected;
    int pi = 0, ni = 0;
    
    if (K % 2 == 1) {
        if (pi < pn) {
            selected.push_back(pos[pi]);
            pi++;
        } else {
            if (zeroCount > 0) {
                cout << "0\n";
                return 0;
            }
            long long ans = 1;
            for (int i = 0; i < K; i++) {
                ans = (ans * (neg[nn - 1 - i] % MOD + MOD)) % MOD;
            }
            cout << ans << "\n";
            return 0;
        }
    }
    
    vector<long long> pairs;
    while (pi + 1 < pn) {
        pairs.push_back(pos[pi] * pos[pi + 1]);
        pi += 2;
    }
    while (ni + 1 < nn) {
        pairs.push_back(neg[ni] * neg[ni + 1]);
        ni += 2;
    }
    
    sort(pairs.rbegin(), pairs.rend());
    
    long long ans = (K % 2 == 1) ? selected[0] % MOD : 1LL;
    int need = K / 2;
    for (int i = 0; i < need && i < (int)pairs.size(); i++) {
        long long p = pairs[i] % MOD;
        ans = (ans * (p + MOD)) % MOD;
    }
    
    if (need > (int)pairs.size()) {
        if (zeroCount > 0) {
            cout << "0\n";
            return 0;
        }
        vector<long long> all;
        for (long long v : pos) all.push_back(v);
        for (long long v : neg) all.push_back(v);
        sort(all.begin(), all.end(), [](long long a, long long b) {
            return abs(a) < abs(b);
        });
        ans = 1;
        for (int i = 0; i < K; i++) {
            long long v = all[i] % MOD;
            ans = (ans * (v + MOD)) % MOD;
        }
    }
    
    cout << ans << "\n";
    return 0;
}
