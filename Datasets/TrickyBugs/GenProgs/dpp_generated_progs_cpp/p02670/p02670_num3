#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

const int INF = 1e9;
const int dx[4] = {1, -1, 0, 0};
const int dy[4] = {0, 0, 1, -1};

int main() {
    ios_base::sync_with_stdio(false);
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
    vector<int> parent(total);
    for (int i = 0; i < total; ++i) parent[i] = i;

    function<int(int)> find = [&](int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    };

    auto union_sets = [&](int a, int b) {
        a = find(a);
        b = find(b);
        if (a != b) parent[b] = a;
    };

    auto cell_id = [&](int x, int y) {
        return x * N + y;
    };

    long long total_inconvenience = 0;

    for (int idx : order) {
        int x = idx / N;
        int y = idx % N;
        total_inconvenience += dist[x][y];
        occupied[x][y] = true;

        for (int d = 0; d < 4; ++d) {
            int nx = x + dx[d];
            int ny = y + dy[d];
            if (nx >= 0 && nx < N && ny >= 0 && ny < N && occupied[nx][ny]) {
                union_sets(cell_id(x, y), cell_id(nx, ny));
            }
        }

        int root = find(cell_id(x, y));
        if (dist[x][y] > 1) {
            queue<pair<int, int>> bfs_q;
            vector<pair<int, int>> component;
            vector<vector<bool>> visited(N, vector<bool>(N, false));

            bfs_q.emplace(x, y);
            visited[x][y] = true;
            component.emplace_back(x, y);

            while (!bfs_q.empty()) {
                auto [cx, cy] = bfs_q.front();
                bfs_q.pop();
                for (int d = 0; d < 4; ++d) {
                    int nx = cx + dx[d];
                    int ny = cy + dy[d];
                    if (nx >= 0 && nx < N && ny >= 0 && ny < N && occupied[nx][ny] && !visited[nx][ny] && find(cell_id(nx, ny)) == root) {
                        visited[nx][ny] = true;
                        bfs_q.emplace(nx, ny);
                        component.emplace_back(nx, ny);
                    }
                }
            }

            int min_dist = INF;
            for (auto [cx, cy] : component) {
                for (int d = 0; d < 4; ++d) {
                    int nx = cx + dx[d];
                    int ny = cy + dy[d];
                    if (nx >= 0 && nx < N && ny >= 0 && ny < N && !occupied[nx][ny]) {
                        min_dist = min(min_dist, dist[nx][ny] + 1);
                    }
                }
                if (cx == 0 || cx == N - 1 || cy == 0 || cy == N - 1) {
                    min_dist = 1;
                }
            }

            if (min_dist < INF) {
                queue<pair<int, int>> update_q;
                for (auto [cx, cy] : component) {
                    if (dist[cx][cy] > min_dist) {
                        dist[cx][cy] = min_dist;
                        update_q.emplace(cx, cy);
                    }
                }

                while (!update_q.empty()) {
                    auto [cx, cy] = update_q.front();
                    update_q.pop();
                    for (int d = 0; d < 4; ++d) {
                        int nx = cx + dx[d];
                        int ny = cy + dy[d];
                        if (nx >= 0 && nx < N && ny >= 0 && ny < N && occupied[nx][ny] && dist[nx][ny] > dist[cx][cy] + 1) {
                            dist[nx][ny] = dist[cx][cy] + 1;
                            update_q.emplace(nx, ny);
                        }
                    }
                }
            }
        }
    }

    cout << total_inconvenience << '\n';
    return 0;
}
