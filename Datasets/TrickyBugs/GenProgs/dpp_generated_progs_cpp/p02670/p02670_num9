#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <climits>

using namespace std;

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

    vector<vector<int>> dist(N, vector<int>(N, 0));
    queue<pair<int, int>> q;

    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            dist[i][j] = min(min(i, N - 1 - i), min(j, N - 1 - j));
            if (dist[i][j] == 0) {
                q.emplace(i, j);
            }
        }
    }

    vector<vector<bool>> occupied(N, vector<bool>(N, false));
    long long total_inconvenience = 0;

    for (int idx : order) {
        int r = idx / N;
        int c = idx % N;
        total_inconvenience += dist[r][c];
        occupied[r][c] = true;

        queue<pair<int, int>> local_q;
        local_q.emplace(r, c);

        while (!local_q.empty()) {
            auto [x, y] = local_q.front();
            local_q.pop();
            for (int d = 0; d < 4; ++d) {
                int nx = x + dx[d];
                int ny = y + dy[d];
                if (nx >= 0 && nx < N && ny >= 0 && ny < N) {
                    if (dist[nx][ny] > dist[x][y] + (occupied[x][y] ? 0 : 1)) {
                        dist[nx][ny] = dist[x][y] + (occupied[x][y] ? 0 : 1);
                        local_q.emplace(nx, ny);
                    }
                }
            }
        }
    }

    cout << total_inconvenience << '\n';
    return 0;
}
