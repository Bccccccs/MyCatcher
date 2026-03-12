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

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    vector<string> strs(N);
    for (int i = 0; i < N; ++i) {
        cin >> strs[i];
    }

    sort(strs.begin(), strs.end(), [](const string& a, const string& b) {
        return a.size() < b.size();
    });

    long long ans = 0;
    vector<int> freq(26, 0);

    for (const string& s : strs) {
        int len = s.size();
        fill(freq.begin(), freq.end(), 0);
        for (int i = 1; i < len; ++i) {
            freq[s[i] - 'a']++;
        }

        int node = 0;
        for (int i = 1; i < len; ++i) {
            int c = s[i] - 'a';
            if (trie[node].next.count(c) == 0) {
                trie[node].next[c] = trie.size();
                trie.emplace_back();
            }
            node = trie[node].next[c];
            if (freq[s[i] - 'a'] > 0) {
                trie[node].sub++;
            }
        }
        trie[node].cnt++;

        node = 0;
        for (int i = 0; i < len - 1; ++i) {
            int c = s[i] - 'a';
            if (trie[node].next.count(c) == 0) break;
            node = trie[node].next[c];
            if (i < len - 1 && s.back() == s[i]) {
                ans += trie[node].cnt;
            }
        }

        node = 0;
        for (int i = 0; i < len - 1; ++i) {
            int c = s[i] - 'a';
            if (trie[node].next.count(c) == 0) break;
            node = trie[node].next[c];
            if (i == len - 2) {
                ans += trie[node].sub;
            }
        }
    }

    cout << ans << '\n';
    return 0;
}
