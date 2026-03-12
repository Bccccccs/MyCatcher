#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

struct Node {
    unordered_map<char, int> next;
    int cnt = 0;
};

vector<Node> trie(1);

int insert(const string &s) {
    int node = 0;
    for (char c : s) {
        if (!trie[node].next.count(c)) {
            trie[node].next[c] = trie.size();
            trie.emplace_back();
        }
        node = trie[node].next[c];
    }
    trie[node].cnt++;
    return node;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    vector<string> strs(N);
    vector<int> endNode(N);
    for (int i = 0; i < N; i++) {
        cin >> strs[i];
        endNode[i] = insert(strs[i]);
    }

    vector<int> freq(26, 0);
    for (int i = 0; i < N; i++) {
        freq[strs[i][0] - 'a']++;
    }

    long long ans = 0;
    for (int i = 0; i < N; i++) {
        const string &s = strs[i];
        int len = s.size();
        vector<bool> inside(26, false);
        int node = 0;
        for (int j = 0; j < len - 1; j++) {
            char c = s[j];
            if (!trie[node].next.count(c)) break;
            node = trie[node].next[c];
            inside[s[j + 1] - 'a'] = true;
        }
        for (int ch = 0; ch < 26; ch++) {
            if (!inside[ch]) continue;
            char b = 'a' + ch;
            if (!trie[node].next.count(b)) continue;
            int target = trie[node].next[b];
            ans += trie[target].cnt;
        }
        if (len > 1) {
            bool aInside = false;
            char a = s[0];
            for (int j = 1; j < len; j++) {
                if (s[j] == a) {
                    aInside = true;
                    break;
                }
            }
            if (aInside) {
                ans += freq[s.back() - 'a'];
            }
        }
    }

    cout << ans << '\n';
    return 0;
}
