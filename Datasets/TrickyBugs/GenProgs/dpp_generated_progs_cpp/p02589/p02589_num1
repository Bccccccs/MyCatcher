#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

struct Node {
    unordered_map<char, int> next;
    int cnt = 0;
    int has_letter[26] = {0};
};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    vector<string> strs(N);
    for (int i = 0; i < N; ++i) {
        cin >> strs[i];
    }

    vector<Node> trie(1);
    vector<int> node_id(N);

    for (int i = 0; i < N; ++i) {
        int cur = 0;
        for (char c : strs[i]) {
            if (trie[cur].next.find(c) == trie[cur].next.end()) {
                trie[cur].next[c] = trie.size();
                trie.emplace_back();
            }
            cur = trie[cur].next[c];
        }
        node_id[i] = cur;
        trie[cur].cnt++;
    }

    for (int i = 0; i < N; ++i) {
        int cur = 0;
        for (char c : strs[i]) {
            trie[cur].has_letter[c - 'a'] = 1;
            cur = trie[cur].next[c];
        }
    }

    long long ans = 0;
    for (int i = 0; i < N; ++i) {
        string& s = strs[i];
        int len = s.size();
        int cur = 0;
        for (int pos = 0; pos < len - 1; ++pos) {
            char c = s[pos];
            if (trie[cur].next.find(c) == trie[cur].next.end()) {
                break;
            }
            cur = trie[cur].next[c];
            char last_char = s.back();
            if (trie[cur].has_letter[last_char - 'a']) {
                int target_node = node_id[i];
                if (trie[target_node].cnt > 0) {
                    ans += trie[target_node].cnt;
                }
            }
        }
    }

    for (int i = 0; i < N; ++i) {
        string& s = strs[i];
        int len = s.size();
        if (len == 1) continue;
        char first_char = s[0];
        string suffix = s.substr(1);
        int cur = 0;
        bool ok = true;
        for (char c : suffix) {
            if (trie[cur].next.find(c) == trie[cur].next.end()) {
                ok = false;
                break;
            }
            cur = trie[cur].next[c];
        }
        if (ok) {
            for (char c = 'a'; c <= 'z'; ++c) {
                if (c == first_char) continue;
                if (trie[cur].has_letter[c - 'a']) {
                    int target = trie[cur].next[c];
                    ans += trie[target].cnt;
                }
            }
        }
    }

    cout << ans << '\n';
    return 0;
}
