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
    
    sort(pos.begin(), pos.end());
    sort(neg.begin(), neg.end());
    
    int pc = pos.size(), nc = neg.size();
    
    if (pc == 0) {
        if (K % 2 == 1) {
            sort(neg.rbegin(), neg.rend());
            long long res = 1;
            for (int i = 0; i < K; ++i) {
                res = (res * ((neg[i] % MOD + MOD) % MOD)) % MOD;
            }
            cout << res << '\n';
        } else {
            sort(neg.begin(), neg.end());
            long long res = 1;
            for (int i = 0; i < K; ++i) {
                res = (res * ((neg[i] % MOD + MOD) % MOD)) % MOD;
            }
            cout << res << '\n';
        }
        return 0;
    }
    
    if (N == K) {
        long long res = 1;
        for (long long v : pos) res = (res * (v % MOD + MOD) % MOD) % MOD;
        for (long long v : neg) res = (res * (v % MOD + MOD) % MOD) % MOD;
        cout << (res + MOD) % MOD << '\n';
        return 0;
    }
    
    vector<long long> candidates;
    for (long long v : pos) candidates.push_back(v);
    for (long long v : neg) candidates.push_back(v);
    sort(candidates.begin(), candidates.end(), [](long long a, long long b) {
        return abs(a) > abs(b);
    });
    
    long long res = 1;
    int neg_cnt = 0;
    long long last_neg = 1, last_pos = 1;
    bool has_zero = false;
    
    for (int i = 0; i < K; ++i) {
        if (candidates[i] < 0) {
            neg_cnt++;
            last_neg = candidates[i];
        } else if (candidates[i] > 0) {
            last_pos = candidates[i];
        } else {
            has_zero = true;
        }
        res = (res * ((candidates[i] % MOD + MOD) % MOD)) % MOD;
    }
    
    if (neg_cnt % 2 == 0) {
        cout << res << '\n';
        return 0;
    }
    
    if (has_zero) {
        cout << "0\n";
        return 0;
    }
    
    long long cand1 = -1, cand2 = -1;
    for (int i = K; i < N; ++i) {
        if (candidates[i] >= 0) {
            cand1 = candidates[i];
            break;
        }
    }
    for (int i = K - 1; i >= 0; --i) {
        if (candidates[i] < 0) {
            cand2 = candidates[i];
            break;
        }
    }
    
    long long opt1 = -1, opt2 = -1;
    if (cand1 != -1 && cand2 != -1) {
        long long inv_last_neg = modinv((last_neg % MOD + MOD) % MOD);
        opt1 = (res * inv_last_neg) % MOD;
        opt1 = (opt1 * (cand1 % MOD)) % MOD;
    }
    
    long long cand3 = -1, cand4 = -1;
    for (int i = K; i < N; ++i) {
        if (candidates[i] < 0) {
            cand3 = candidates[i];
            break;
        }
    }
    for (int i = K - 1; i >= 0; --i) {
        if (candidates[i] >= 0) {
            cand4 = candidates[i];
            break;
        }
    }
    
    if (cand3 != -1 && cand4 != -1) {
        long long inv_last_pos = modinv((last_pos % MOD + MOD) % MOD);
        opt2 = (res * inv_last_pos) % MOD;
        opt2 = (opt2 * ((cand3 % MOD + MOD) % MOD)) % MOD;
    }
    
    if (opt1 == -1 && opt2 == -1) {
        long long fallback = 1;
        sort(candidates.begin(), candidates.end(), greater<long long>());
        for (int i = 0; i < K; ++i) {
            fallback = (fallback * ((candidates[i] % MOD + MOD) % MOD)) % MOD;
        }
        cout << fallback << '\n';
    } else if (opt1 == -1) {
        cout << opt2 << '\n';
    } else if (opt2 == -1) {
        cout << opt1 << '\n';
    } else {
        long long abs_last_neg = abs(last_neg);
        long long abs_cand1 = abs(cand1);
        long long abs_last_pos = abs(last_pos);
        long long abs_cand3 = abs(cand3);
        
        if (abs_last_neg * abs_cand1 >= abs_last_pos * abs_cand3) {
            cout << opt1 << '\n';
        } else {
            cout << opt2 << '\n';
        }
    }
    
    return 0;
}
