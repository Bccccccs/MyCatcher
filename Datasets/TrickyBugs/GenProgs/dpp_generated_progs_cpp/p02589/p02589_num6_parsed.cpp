#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

struct Node {
    int cnt = 0;
    int sub = 0;
    unordered_map<int, int> next;
};

vector<Node> trie(1);

void insert(const string& s) {
    int node = 0;
    for (char ch : s) {
        int c = ch - 'a';
        if (trie[node].next.find(c) == trie[node].next.end()) {
            trie[node].next[c] = trie.size();
            trie.emplace_back();
        }
        node = trie[node].next[c];
        trie[node].sub++;
    }
    trie[node].cnt++;
}

int query(const string& s) {
    int node = 0;
    for (char ch : s) {
        int c = ch - 'a';
        if (trie[node].next.find(c) == trie[node].next.end()) {
            return 0;
        }
        node = trie[node].next[c];
    }
    return trie[node].cnt;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    vector<string> strs(N);
    for (int i = 0; i < N; i++) {
        cin >> strs[i];
    }

    unordered_map<string, int> freq;
    for (const auto& s : strs) {
        freq[s]++;
    }

    vector<pair<string, int>> unique_strs(freq.begin(), freq.end());

    for (const auto& p : unique_strs) {
        insert(p.first);
    }

    long long ans = 0;

    for (const auto& p : unique_strs) {
        const string& s = p.first;
        int cnt = p.second;
        int len = s.length();

        vector<bool> has(26, false);
        for (int i = 1; i < len; i++) {
            has[s[i] - 'a'] = true;
        }

        string x = s.substr(1);
        for (int a = 0; a < 26; a++) {
            if (!has[a]) continue;
            char ac = 'a' + a;
            string candidate = ac + x;
            int q = query(candidate);
            if (q > 0) {
                if (candidate == s) {
                    ans += 1LL * cnt * (cnt - 1);
                } else {
                    ans += 1LL * cnt * q;
                }
            }
        }
    }

    cout << ans << '\n';
    return 0;
}
