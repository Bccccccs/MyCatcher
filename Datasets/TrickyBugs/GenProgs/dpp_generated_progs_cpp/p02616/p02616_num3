#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>
using namespace std;

const long long MOD = 1000000007LL;

long long modpow(long long a, long long e) {
    long long res = 1;
    a %= MOD;
    while (e) {
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
    
    sort(pos.rbegin(), pos.rend());
    sort(neg.begin(), neg.end());
    
    int ps = pos.size();
    int ns = neg.size();
    
    if (ps == 0) {
        if (K % 2 == 1) {
            sort(neg.rbegin(), neg.rend());
            long long res = 1;
            for (int i = 0; i < K; ++i) {
                res = (res * (neg[i] % MOD + MOD)) % MOD;
            }
            cout << res << '\n';
        } else {
            long long res = 1;
            for (int i = 0; i < K; ++i) {
                res = (res * (neg[i] % MOD + MOD)) % MOD;
            }
            cout << res << '\n';
        }
        return 0;
    }
    
    vector<long long> selected;
    int pi = 0, ni = 0;
    
    while (selected.size() < K) {
        if (pi >= ps) {
            selected.push_back(neg[ni++]);
        } else if (ni >= ns) {
            selected.push_back(pos[pi++]);
        } else {
            if (pos[pi] >= -neg[ni]) {
                selected.push_back(pos[pi++]);
            } else {
                selected.push_back(neg[ni++]);
            }
        }
    }
    
    int neg_cnt = 0;
    for (long long v : selected) if (v < 0) ++neg_cnt;
    
    if (neg_cnt % 2 == 0) {
        long long res = 1;
        for (long long v : selected) {
            v %= MOD;
            if (v < 0) v += MOD;
            res = (res * v) % MOD;
        }
        cout << res << '\n';
        return 0;
    }
    
    long long x1 = -1, x2 = -1;
    long long y1 = -1, y2 = -1;
    
    for (int i = 0; i < selected.size(); ++i) {
        if (selected[i] < 0) x1 = selected[i];
        else y1 = selected[i];
    }
    
    if (pi < ps && ni > 0) {
        x2 = pos[pi];
        y2 = neg[ni - 1];
    }
    
    long long a1 = -1, a2 = -1;
    if (x1 != -1 && y2 != -1) {
        a1 = x1 * y2;
    }
    if (y1 != -1 && x2 != -1) {
        a2 = y1 * x2;
    }
    
    bool replace = false;
    if (a1 != -1 && a2 != -1) {
        if (x2 * y1 > y2 * x1) replace = true;
    } else if (a2 != -1) {
        replace = true;
    }
    
    if (replace) {
        bool rem_pos = false, rem_neg = false;
        for (int i = 0; i < selected.size(); ++i) {
            if (selected[i] >= 0 && !rem_pos) {
                selected[i] = x2;
                rem_pos = true;
            }
            if (selected[i] < 0 && !rem_neg) {
                selected[i] = y2;
                rem_neg = true;
            }
        }
    } else {
        bool rem_pos = false, rem_neg = false;
        for (int i = 0; i < selected.size(); ++i) {
            if (selected[i] < 0 && !rem_neg) {
                selected[i] = y2;
                rem_neg = true;
            }
            if (selected[i] >= 0 && !rem_pos) {
                selected[i] = x2;
                rem_pos = true;
            }
        }
    }
    
    long long res = 1;
    for (long long v : selected) {
        v %= MOD;
        if (v < 0) v += MOD;
        res = (res * v) % MOD;
    }
    cout << res << '\n';
    
    return 0;
}
