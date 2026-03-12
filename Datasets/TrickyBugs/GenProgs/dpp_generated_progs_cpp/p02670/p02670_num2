#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

const int INF = 1e9;
const int dx[4] = {1, -1, 0, 0};
const int dy[4] = {0, 0, 1, -1};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    int total = N * N;
    vector<int> order(total);
    for (int i = 0; i < total; ++i) {
        cin >> order[i];
        order[i]--;
    }

    vector<vector<int>> dist(N, vector<int>(N, INF));
    queue<pair<int, int>> q;

    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (i == 0 || i == N - 1 || j == 0 || j == N - 1) {
                dist[i][j] = 1;
                q.emplace(i, j);
            }
        }
    }

    while (!q.empty()) {
        auto [x, y] = q.front();
        q.pop();
        for (int d = 0; d < 4; ++d) {
            int nx = x + dx[d];
            int ny = y + dy[d];
            if (nx >= 0 && nx < N && ny >= 0 && ny < N && dist[nx][ny] > dist[x][y] + 1) {
                dist[nx][ny] = dist[x][y] + 1;
                q.emplace(nx, ny);
            }
        }
    }

    vector<vector<bool>> occupied(N, vector<bool>(N, false));
    vector<vector<int>> curDist = dist;
    long long ans = 0;

    for (int idx : order) {
        int x = idx / N;
        int y = idx % N;
        ans += curDist[x][y] - 1;
        occupied[x][y] = true;

        queue<pair<int, int>> updateQ;
        curDist[x][y] = 0;
        updateQ.emplace(x, y);

        while (!updateQ.empty()) {
            auto [cx, cy] = updateQ.front();
            updateQ.pop();
            for (int d = 0; d < 4; ++d) {
                int nx = cx + dx[d];
                int ny = cy + dy[d];
                if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                    int nd = curDist[cx][cy] + (occupied[nx][ny] ? 0 : 1);
                    if (nd < curDist[nx][ny]) {
                        curDist[nx][ny] = nd;
                        updateQ.emplace(nx, ny);
                    }
                }
            }
        }
    }

    cout << ans << "\n";
    return 0;
}
