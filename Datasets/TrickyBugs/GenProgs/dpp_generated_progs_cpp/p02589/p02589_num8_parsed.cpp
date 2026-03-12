#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

struct Node {
    int cnt = 0;
    int sub = 0;
    Node* ch[26] = {nullptr};
};

Node* root = new Node();

void insert(const string& s) {
    Node* cur = root;
    for (char c : s) {
        int idx = c - 'a';
        if (!cur->ch[idx]) cur->ch[idx] = new Node();
        cur = cur->ch[idx];
        cur->cnt++;
    }
}

void dfs(Node* u) {
    if (!u) return;
    u->sub = u->cnt;
    for (int i = 0; i < 26; ++i) {
        if (u->ch[i]) {
            dfs(u->ch[i]);
            u->sub += u->ch[i]->sub;
        }
    }
}

int query(const string& s) {
    Node* cur = root;
    for (char c : s) {
        int idx = c - 'a';
        if (!cur->ch[idx]) return 0;
        cur = cur->ch[idx];
    }
    return cur->sub;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    vector<string> arr(N);
    for (int i = 0; i < N; ++i) {
        cin >> arr[i];
        insert(arr[i]);
    }
    dfs(root);

    unordered_map<string, int> freq;
    for (const string& s : arr) freq[s]++;

    long long ans = 0;

    for (const string& s : arr) {
        int len = s.size();
        vector<bool> has(26, false);
        for (int i = 0; i < len - 1; ++i) {
            has[s[i] - 'a'] = true;
            string suffix = s.substr(i + 1);
            int add = query(suffix);
            if (has[s.back() - 'a']) {
                add -= freq[suffix];
            }
            ans += add;
        }
    }

    cout << ans << '\n';
    return 0;
}
