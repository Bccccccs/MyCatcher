#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
using namespace std;

struct Query {
    int l, r, idx;
};

const int MAXN = 200005;
int arr[MAXN], ans[MAXN], freq[MAXN], distinct;
int block_size;

bool compare(const Query &a, const Query &b) {
    if (a.l / block_size != b.l / block_size)
        return a.l / block_size < b.l / block_size;
    return (a.l / block_size & 1) ? (a.r < b.r) : (a.r > b.r);
}

void add(int pos) {
    freq[arr[pos]]++;
    if (freq[arr[pos]] == 1) distinct++;
}

void remove(int pos) {
    freq[arr[pos]]--;
    if (freq[arr[pos]] == 0) distinct--;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, Q;
    cin >> N >> Q;
    for (int i = 0; i < N; i++) {
        cin >> arr[i];
    }

    vector<Query> queries(Q);
    for (int i = 0; i < Q; i++) {
        int l, r;
        cin >> l >> r;
        l--; r--;
        queries[i] = {l, r, i};
    }

    block_size = sqrt(N);
    sort(queries.begin(), queries.end(), compare);

    int cur_l = 0, cur_r = -1;
    distinct = 0;
    for (const auto &q : queries) {
        while (cur_l > q.l) {
            cur_l--;
            add(cur_l);
        }
        while (cur_r < q.r) {
            cur_r++;
            add(cur_r);
        }
        while (cur_l < q.l) {
            remove(cur_l);
            cur_l++;
        }
        while (cur_r > q.r) {
            remove(cur_r);
            cur_r--;
        }
        ans[q.idx] = distinct;
    }

    for (int i = 0; i < Q; i++) {
        cout << ans[i] << '\n';
    }

    return 0;
}
