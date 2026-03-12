#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

struct Node {
    unordered_map<char, int> next;
    int cnt = 0;
    int sub = 0;
};

vector<Node> trie(1);

void insert(const string &s) {
    int v = 0;
    for (char c : s) {
        if (!trie[v].next.count(c)) {
            trie[v].next[c] = trie.size();
            trie.emplace_back();
        }
        v = trie[v].next[c];
        trie[v].cnt++;
    }
}

int query(const string &s) {
    int v = 0;
    for (char c : s) {
        if (!trie[v].next.count(c)) return 0;
        v = trie[v].next[c];
    }
    return trie[v].cnt;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    vector<string> S(N);
    for (int i = 0; i < N; ++i) {
        cin >> S[i];
    }

    unordered_map<string, int> freq;
    for (const string &s : S) {
        freq[s]++;
    }

    long long ans = 0;

    for (const auto &entry : freq) {
        const string &s = entry.first;
        int cnt = entry.second;
        int len = s.length();

        vector<bool> has(26, false);
        for (int i = 1; i < len; ++i) {
            has[s[i] - 'a'] = true;
        }

        for (char a = 'a'; a <= 'z'; ++a) {
            if (!has[a - 'a']) continue;
            string x = s.substr(1);
            string target = x + a;
            if (freq.count(target)) {
                ans += 1LL * cnt * freq[target];
            }
        }
    }

    cout << ans << '\n';
    return 0;
}
