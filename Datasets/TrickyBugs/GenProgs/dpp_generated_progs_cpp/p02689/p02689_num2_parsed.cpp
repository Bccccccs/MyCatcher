#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, M;
    cin >> N >> M;

    vector<int> h(N + 1);
    for (int i = 1; i <= N; ++i) {
        cin >> h[i];
    }

    vector<vector<int>> adj(N + 1);
    for (int i = 0; i < M; ++i) {
        int a, b;
        cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    int good_count = 0;
    for (int i = 1; i <= N; ++i) {
        bool good = true;
        for (int neighbor : adj[i]) {
            if (h[i] <= h[neighbor]) {
                good = false;
                break;
            }
        }
        if (good) {
            ++good_count;
        }
    }

    cout << good_count << endl;
    return 0;
}
