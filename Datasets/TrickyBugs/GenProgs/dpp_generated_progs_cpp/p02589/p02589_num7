#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

struct TrieNode {
    unordered_map<char, TrieNode*> children;
    int cnt = 0;
    int cnt_special = 0;
};

void insert(TrieNode* root, const string& s, bool count_special) {
    TrieNode* node = root;
    for (char c : s) {
        if (!node->children.count(c)) {
            node->children[c] = new TrieNode();
        }
        node = node->children[c];
    }
    node->cnt++;
    if (count_special) {
        node->cnt_special++;
    }
}

pair<int, int> query(TrieNode* root, const string& s) {
    TrieNode* node = root;
    for (char c : s) {
        if (!node->children.count(c)) {
            return {0, 0};
        }
        node = node->children[c];
    }
    return {node->cnt, node->cnt_special};
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

    TrieNode* root_prefix = new TrieNode();
    TrieNode* root_suffix = new TrieNode();

    vector<int> freq_first(26, 0);
    vector<int> freq_last(26, 0);
    vector<vector<int>> inside_cnt(26, vector<int>(26, 0));

    for (const string& s : strs) {
        int len = s.length();
        if (len >= 2) {
            char first = s[0];
            char last = s[len - 1];
            freq_first[first - 'a']++;
            freq_last[last - 'a']++;

            vector<bool> seen(26, false);
            for (int i = 1; i < len - 1; i++) {
                seen[s[i] - 'a'] = true;
            }
            for (int c = 0; c < 26; c++) {
                if (seen[c]) {
                    inside_cnt[first - 'a'][c]++;
                }
            }
        }
    }

    long long ans = 0;

    for (const string& s : strs) {
        int len = s.length();
        if (len >= 2) {
            char first = s[0];
            char last = s[len - 1];
            string suffix = s.substr(1);
            string prefix = s.substr(0, len - 1);

            insert(root_prefix, prefix, false);
            insert(root_suffix, suffix, true);
        }
    }

    for (const string& s : strs) {
        int len = s.length();
        if (len >= 2) {
            char first = s[0];
            char last = s[len - 1];
            string suffix = s.substr(1);
            string prefix = s.substr(0, len - 1);

            auto res_suffix = query(root_suffix, suffix);
            auto res_prefix = query(root_prefix, prefix);

            long long total_with_suffix = res_suffix.first;
            long long special_with_suffix = res_suffix.second;

            ans += total_with_suffix;

            for (int c = 0; c < 26; c++) {
                if (inside_cnt[first - 'a'][c] > 0) {
                    ans -= special_with_suffix;
                    break;
                }
            }
        }
    }

    cout << ans << '\n';

    return 0;
}
