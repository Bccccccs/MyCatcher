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
    
    int pcnt = pos.size();
    int ncnt = neg.size();
    
    if (pcnt == 0) {
        if (K % 2 == 1) {
            sort(neg.begin(), neg.end(), greater<long long>());
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
    int sign = 1;
    int last_neg = -1, last_pos = -1;
    int cnt = 0;
    for (int i = 0; i < N && cnt < K; ++i) {
        long long v = candidates[i];
        res = (res * (abs(v) % MOD)) % MOD;
        if (v < 0) {
            sign = -sign;
            last_neg = i;
        } else {
            last_pos = i;
        }
        ++cnt;
    }
    
    if (sign == 1) {
        cout << res << '\n';
        return 0;
    }
    
    long long ans = res;
    bool improved = false;
    
    int next_pos = -1;
    for (int i = K; i < N; ++i) {
        if (candidates[i] >= 0) {
            next_pos = i;
            break;
        }
    }
    int next_neg = -1;
    for (int i = K; i < N; ++i) {
        if (candidates[i] < 0) {
            next_neg = i;
            break;
        }
    }
    
    if (last_neg != -1 && next_pos != -1) {
        long long old_val = abs(candidates[last_neg]);
        long long new_val = abs(candidates[next_pos]);
        long long temp = (res * modinv(old_val % MOD)) % MOD;
        temp = (temp * (new_val % MOD)) % MOD;
        ans = max(ans, temp);
        improved = true;
    }
    
    if (last_pos != -1 && next_neg != -1) {
        long long old_val = abs(candidates[last_pos]);
        long long new_val = abs(candidates[next_neg]);
        long long temp = (res * modinv(old_val % MOD)) % MOD;
        temp = (temp * (new_val % MOD)) % MOD;
        ans = max(ans, temp);
        improved = true;
    }
    
    if (!improved) {
        sort(candidates.begin(), candidates.end(), greater<long long>());
        res = 1;
        for (int i = 0; i < K; ++i) {
            res = (res * ((candidates[i] % MOD + MOD) % MOD)) % MOD;
        }
        ans = res;
    }
    
    cout << (ans + MOD) % MOD << '\n';
    return 0;
}
