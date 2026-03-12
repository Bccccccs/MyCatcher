#include <iostream>
#include <vector>
#include <algorithm>
#include <queue>
#include <functional>
#include <cmath>
using namespace std;

const long long MOD = 1000000007LL;

long long mod_pow(long long a, long long b, long long mod) {
    long long res = 1;
    a %= mod;
    while (b > 0) {
        if (b & 1) res = (res * a) % mod;
        a = (a * a) % mod;
        b >>= 1;
    }
    return res;
}

long long mod_inv(long long a, long long mod) {
    return mod_pow(a, mod - 2, mod);
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int N, K;
    cin >> N >> K;
    
    vector<long long> pos, neg, zero;
    for (int i = 0; i < N; ++i) {
        long long x;
        cin >> x;
        if (x > 0) pos.push_back(x);
        else if (x < 0) neg.push_back(x);
        else zero.push_back(x);
    }
    
    sort(pos.rbegin(), pos.rend());
    sort(neg.begin(), neg.end());
    
    int psz = pos.size();
    int nsz = neg.size();
    int zsz = zero.size();
    
    if (psz + nsz < K) {
        cout << "0\n";
        return 0;
    }
    
    if (psz == 0) {
        if (K % 2 == 1) {
            if (zsz > 0) {
                cout << "0\n";
                return 0;
            } else {
                sort(neg.rbegin(), neg.rend());
                long long res = 1;
                for (int i = 0; i < K; ++i) {
                    res = (res * (neg[i] % MOD + MOD) % MOD) % MOD;
                }
                cout << res << "\n";
                return 0;
            }
        } else {
            long long res = 1;
            for (int i = 0; i < K; ++i) {
                res = (res * (neg[i] % MOD + MOD) % MOD) % MOD;
            }
            cout << res << "\n";
            return 0;
        }
    }
    
    vector<long long> chosen;
    int pi = 0, ni = 0;
    
    if (K % 2 == 1) {
        chosen.push_back(pos[pi]);
        pi++;
        K--;
    }
    
    while (K > 0) {
        if (K >= 2) {
            long long pos_pair = -1e18;
            long long neg_pair = -1e18;
            
            if (pi + 1 < psz) {
                pos_pair = pos[pi] * pos[pi + 1];
            }
            if (ni + 1 < nsz) {
                neg_pair = neg[ni] * neg[ni + 1];
            }
            
            if (pos_pair > neg_pair) {
                chosen.push_back(pos[pi]);
                chosen.push_back(pos[pi + 1]);
                pi += 2;
            } else if (ni + 1 < nsz) {
                chosen.push_back(neg[ni]);
                chosen.push_back(neg[ni + 1]);
                ni += 2;
            } else {
                chosen.push_back(pos[pi]);
                chosen.push_back(pos[pi + 1]);
                pi += 2;
            }
            K -= 2;
        }
    }
    
    bool all_zero = true;
    for (long long v : chosen) {
        if (v != 0) all_zero = false;
    }
    if (all_zero && zsz > 0) {
        cout << "0\n";
        return 0;
    }
    
    long long res = 1;
    for (long long v : chosen) {
        v %= MOD;
        if (v < 0) v += MOD;
        res = (res * v) % MOD;
    }
    
    cout << res << "\n";
    
    return 0;
}
