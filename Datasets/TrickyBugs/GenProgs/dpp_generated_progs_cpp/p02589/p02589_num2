#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

struct Node {
    int cnt = 0;
    int subcnt = 0;
    unordered_map<char, Node*> next;
};

void insert(Node* root, const string& s) {
    Node* cur = root;
    for (char c : s) {
        if (cur->next.find(c) == cur->next.end()) {
            cur->next[c] = new Node();
        }
        cur = cur->next[c];
        cur->cnt++;
    }
}

int query(Node* root, const string& s) {
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
    vector<string> arr(N);
    for (int i = 0; i < N; i++) {
        cin >> arr[i];
    }

    Node* pref = new Node();
    Node* suff = new Node();

    unordered_map<string, int> freq;
    for (const string& s : arr) {
        freq[s]++;
        insert(pref, s);
        string rev = s;
        reverse(rev.begin(), rev.end());
        insert(suff, rev);
    }

    long long ans = 0;

    for (const auto& entry : freq) {
        const string& s = entry.first;
        int cnt = entry.second;
        int len = s.length();

        vector<bool> has(26, false);
        for (int i = 1; i < len; i++) {
            has[s[i] - 'a'] = true;
        }

        for (char a = 'a'; a <= 'z'; a++) {
            if (!has[a - 'a']) continue;
            string x = s.substr(1);
            string target = x + a;
            int q = query(pref, target);
            if (target == s) q -= cnt;
            ans += 1LL * cnt * q;
        }

        vector<bool> has_rev(26, false);
        for (int i = 0; i < len - 1; i++) {
            has_rev[s[i] - 'a'] = true;
        }

        for (char b = 'a'; b <= 'z'; b++) {
            if (!has_rev[b - 'a']) continue;
            string x = s.substr(0, len - 1);
            string revx = x;
            reverse(revx.begin(), revx.end());
            string revb(1, b);
            string target_rev = revb + revx;
            int q = query(suff, target_rev);
            string orig_target = b + x;
            if (orig_target == s) q -= cnt;
            ans += 1LL * cnt * q;
        }
    }

    cout << ans << '\n';

    return 0;
}
