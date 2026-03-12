#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

struct Node {
    int cnt;
    unordered_map<char, Node*> next;
    Node() : cnt(0) {}
};

void insert(Node* root, const string& s) {
    Node* cur = root;
    for (char c : s) {
        if (cur->next.find(c) == cur->next.end()) {
            cur->next[c] = new Node();
        }
        cur = cur->next[c];
    }
    cur->cnt++;
}

int count_prefix(Node* root, const string& s) {
    Node* cur = root;
    for (char c : s) {
        if (cur->next.find(c) == cur->next.end()) return 0;
        cur = cur->next[c];
    }
    return cur->cnt;
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

    Node* trie = new Node();
    for (const string& s : strs) {
        insert(trie, s);
    }

    long long ans = 0;
    unordered_map<string, int> suffix_count;
    vector<pair<string, char>> suffix_with_first_char;

    for (const string& s : strs) {
        if (s.length() < 2) continue;
        char first_char = s[0];
        string rest = s.substr(1);
        suffix_count[rest]++;
        suffix_with_first_char.emplace_back(rest, first_char);
    }

    unordered_map<string, vector<char>> suffix_to_first_chars;
    for (const auto& p : suffix_with_first_char) {
        suffix_to_first_chars[p.first].push_back(p.second);
    }

    for (const string& s : strs) {
        if (s.length() < 2) continue;
        string prefix = s.substr(0, s.length() - 1);
        char last_char = s.back();

        if (suffix_count.find(prefix) == suffix_count.end()) continue;

        const vector<char>& first_chars = suffix_to_first_chars[prefix];
        int total = first_chars.size();

        vector<int> freq(26, 0);
        for (char fc : first_chars) {
            freq[fc - 'a']++;
        }

        int invalid = 0;
        for (char fc : first_chars) {
            if (fc == last_char) {
                invalid++;
            }
        }

        ans += total - invalid;
    }

    cout << ans << '\n';

    return 0;
}
