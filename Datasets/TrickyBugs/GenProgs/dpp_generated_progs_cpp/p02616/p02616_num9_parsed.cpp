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
            long long ans = 1;
            for (int i = 0; i < K; ++i) {
                ans = (ans * (neg[i] % MOD + MOD) % MOD) % MOD;
            }
            cout << ans << '\n';
        } else {
            long long ans = 1;
            for (int i = 0; i < K; ++i) {
                ans = (ans * (neg[i] % MOD + MOD) % MOD) % MOD;
            }
            cout << ans << '\n';
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
        long long ans = 1;
        for (long long v : selected) {
            v %= MOD;
            if (v < 0) v += MOD;
            ans = (ans * v) % MOD;
        }
        cout << ans << '\n';
        return 0;
    }
    
    long long replace_neg = -1, replace_pos = -1;
    long long remove_neg = -1, remove_pos = -1;
    
    for (int i = 0; i < selected.size(); ++i) {
        if (selected[i] < 0) remove_neg = selected[i];
        else remove_pos = selected[i];
    }
    
    long long cand1 = -1, cand2 = -1;
    
    if (pi < ps && remove_neg != -1) {
        cand1 = pos[pi];
    }
    if (ni < ns && remove_pos != -1) {
        cand2 = neg[ni];
    }
    
    if (cand1 == -1 && cand2 == -1) {
        sort(pos.begin(), pos.end());
        sort(neg.rbegin(), neg.rend());
        long long ans = 1;
        for (int i = 0; i < K; ++i) {
            if (i < pos.size()) {
                ans = (ans * (pos[i] % MOD + MOD) % MOD) % MOD;
            } else {
                ans = (ans * (neg[i - pos.size()] % MOD + MOD) % MOD) % MOD;
            }
        }
        cout << ans << '\n';
        return 0;
    }
    
    if (cand1 == -1) {
        for (int i = 0; i < selected.size(); ++i) {
            if (selected[i] == remove_pos) {
                selected[i] = cand2;
                break;
            }
        }
    } else if (cand2 == -1) {
        for (int i = 0; i < selected.size(); ++i) {
            if (selected[i] == remove_neg) {
                selected[i] = cand1;
                break;
            }
        }
    } else {
        long long val1 = cand1 * remove_neg;
        long long val2 = cand2 * remove_pos;
        if (val1 > val2) {
            for (int i = 0; i < selected.size(); ++i) {
                if (selected[i] == remove_neg) {
                    selected[i] = cand1;
                    break;
                }
            }
        } else {
            for (int i = 0; i < selected.size(); ++i) {
                if (selected[i] == remove_pos) {
                    selected[i] = cand2;
                    break;
                }
            }
        }
    }
    
    long long ans = 1;
    for (long long v : selected) {
        v %= MOD;
        if (v < 0) v += MOD;
        ans = (ans * v) % MOD;
    }
    cout << ans << '\n';
    
    return 0;
}
