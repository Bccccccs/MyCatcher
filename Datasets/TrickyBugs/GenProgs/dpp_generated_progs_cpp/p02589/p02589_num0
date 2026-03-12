#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

struct TrieNode {
    unordered_map<char, TrieNode*> children;
    int cnt = 0;
};

void insert(TrieNode* root, const string& s) {
    TrieNode* node = root;
    for (char c : s) {
        if (!node->children.count(c)) {
            node->children[c] = new TrieNode();
        }
        node = node->children[c];
        node->cnt++;
    }
}

int query(TrieNode* root, const string& s) {
    TrieNode* node = root;
    for (char c : s) {
        if (!node->children.count(c)) return 0;
        node = node->children[c];
    }
    return node->cnt;
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

    TrieNode* root = new TrieNode();
    unordered_map<string, int> freq;

    for (const string& s : S) {
        insert(root, s);
        freq[s]++;
    }

    long long ans = 0;

    for (const string& s : S) {
        int len = s.length();
        vector<bool> has(26, false);
        for (int k = 1; k < len; ++k) {
            has[s[k] - 'a'] = true;
        }
        for (char a = 'a'; a <= 'z'; ++a) {
            if (!has[a - 'a']) continue;
            string x = s.substr(1);
            string target = x + a;
            int cnt = query(root, target);
            ans += cnt;
        }
    }

    for (const auto& p : freq) {
        const string& s = p.first;
        long long c = p.second;
        if (c > 1) {
            int len = s.length();
            vector<bool> has(26, false);
            for (int k = 1; k < len; ++k) {
                has[s[k] - 'a'] = true;
            }
            if (has[s[0] - 'a']) {
                ans -= c * (c - 1);
            }
        }
    }

    cout << ans << '\n';

    return 0;
}
