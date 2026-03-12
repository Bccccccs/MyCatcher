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
            if (i == 0 || i == N-1 || j == 0 || j == N-1) {
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
        if (a != b) {
            parent[b] = a;
        }
    };

    long long total_inconvenience = 0;
    for (int seat : order) {
        int r = seat / N;
        int c = seat % N;
        occupied[r][c] = true;
        total_inconvenience += dist[r][c];

        int idx = r * N + c;
        for (int d = 0; d < 4; ++d) {
            int nr = r + dx[d];
            int nc = c + dy[d];
            if (nr >= 0 && nr < N && nc >= 0 && nc < N && occupied[nr][nc]) {
                union_sets(idx, nr * N + nc);
            }
        }

        if (dist[r][c] > 1) {
            vector<pair<int, int>> component;
            queue<pair<int, int>> bfsq;
            vector<vector<bool>> visited(N, vector<bool>(N, false));
            bfsq.emplace(r, c);
            visited[r][c] = true;
            int root = find(idx);

            while (!bfsq.empty()) {
                auto [x, y] = bfsq.front();
                bfsq.pop();
                component.emplace_back(x, y);
                for (int d = 0; d < 4; ++d) {
                    int nx = x + dx[d];
                    int ny = y + dy[d];
                    if (nx >= 0 && nx < N && ny >= 0 && ny < N && occupied[nx][ny] && !visited[nx][ny] && find(nx * N + ny) == root) {
                        visited[nx][ny] = true;
                        bfsq.emplace(nx, ny);
                    }
                }
            }

            int min_dist = INF;
            for (auto [x, y] : component) {
                for (int d = 0; d < 4; ++d) {
                    int nx = x + dx[d];
                    int ny = y + dy[d];
                    if (nx >= 0 && nx < N && ny >= 0 && ny < N && !occupied[nx][ny]) {
                        min_dist = min(min_dist, dist[nx][ny] + 1);
                    }
                }
                if (x == 0 || x == N-1 || y == 0 || y == N-1) {
                    min_dist = 1;
                }
            }

            if (min_dist < INF) {
                for (auto [x, y] : component) {
                    dist[x][y] = min_dist;
                }
                queue<pair<int, int>> updateq;
                for (auto [x, y] : component) {
                    updateq.emplace(x, y);
                }
                while (!updateq.empty()) {
                    auto [x, y] = updateq.front();
                    updateq.pop();
                    for (int d = 0; d < 4; ++d) {
                        int nx = x + dx[d];
                        int ny = y + dy[d];
                        if (nx >= 0 && nx < N && ny >= 0 && ny < N && occupied[nx][ny] && dist[nx][ny] > dist[x][y] + 1) {
                            dist[nx][ny] = dist[x][y] + 1;
                            updateq.emplace(nx, ny);
                        }
                    }
                }
            }
        }
    }

    cout << total_inconvenience << '\n';
    return 0;
}
