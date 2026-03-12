#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

struct Cell {
    int r, c;
};

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;
    int total = N * N;
    vector<int> order(total);
    for (int i = 0; i < total; ++i) {
        cin >> order[i];
        order[i]--; // to 0‑based
    }

    vector<vector<int>> dist(N, vector<int>(N, -1));
    queue<Cell> q;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (i == 0 || i == N - 1 || j == 0 || j == N - 1) {
                dist[i][j] = 1;
                q.push({i, j});
            }
        }
    }

    int dr[] = {1, -1, 0, 0};
    int dc[] = {0, 0, 1, -1};

    while (!q.empty()) {
        Cell cur = q.front(); q.pop();
        for (int d = 0; d < 4; ++d) {
            int nr = cur.r + dr[d];
            int nc = cur.c + dc[d];
            if (nr >= 0 && nr < N && nc >= 0 && nc < N && dist[nr][nc] == -1) {
                dist[nr][nc] = dist[cur.r][cur.c] + 1;
                q.push({nr, nc});
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

    auto unionSets = [&](int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra != rb) parent[rb] = ra;
    };

    auto cellId = [&](int r, int c) { return r * N + c; };

    long long totalInconvenience = 0;
    for (int idx : order) {
        int r = idx / N;
        int c = idx % N;
        occupied[r][c] = true;
        totalInconvenience += dist[r][c];

        for (int d = 0; d < 4; ++d) {
            int nr = r + dr[d];
            int nc = c + dc[d];
            if (nr >= 0 && nr < N && nc >= 0 && nc < N && occupied[nr][nc]) {
                unionSets(cellId(r, c), cellId(nr, nc));
            }
        }

        int root = find(cellId(r, c));
        int minDist = dist[r][c];
        for (int i = 0; i < N; ++i) {
            for (int j = 0; j < N; ++j) {
                if (occupied[i][j] && find(cellId(i, j)) == root) {
                    for (int d = 0; d < 4; ++d) {
                        int ni = i + dr[d];
                        int nj = j + dc[d];
                        if (ni >= 0 && ni < N && nj >= 0 && nj < N && !occupied[ni][nj]) {
                            minDist = min(minDist, dist[ni][nj]);
                        }
                    }
                }
            }
        }

        if (minDist < dist[r][c]) {
            queue<Cell> updateQ;
            vector<vector<bool>> visited(N, vector<bool>(N, false));
            for (int i = 0; i < N; ++i) {
                for (int j = 0; j < N; ++j) {
                    if (occupied[i][j] && find(cellId(i, j)) == root) {
                        visited[i][j] = true;
                        updateQ.push({i, j});
                    }
                }
            }

            while (!updateQ.empty()) {
                Cell cur = updateQ.front(); updateQ.pop();
                for (int d = 0; d < 4; ++d) {
                    int nr = cur.r + dr[d];
                    int nc = cur.c + dc[d];
                    if (nr >= 0 && nr < N && nc >= 0 && nc < N && !occupied[nr][nc] && dist[nr][nc] > minDist + 1) {
                        dist[nr][nc] = minDist + 1;
                        updateQ.push({nr, nc});
                    }
                }
            }
        }
    }

    cout << totalInconvenience << '\n';
    return 0;
}
