#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <climits>
using namespace std;

struct Cell {
    int r, c;
};

int N;
vector<vector<int>> dist;
vector<vector<bool>> occupied;
const int dr[4] = {-1, 1, 0, 0};
const int dc[4] = {0, 0, -1, 1};

void bfs() {
    queue<Cell> q;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (!occupied[i][j]) {
                dist[i][j] = 0;
                q.push({i, j});
            }
        }
    }
    while (!q.empty()) {
        Cell cur = q.front(); q.pop();
        for (int d = 0; d < 4; ++d) {
            int nr = cur.r + dr[d];
            int nc = cur.c + dc[d];
            if (nr >= 0 && nr < N && nc >= 0 && nc < N) {
                if (dist[nr][nc] > dist[cur.r][cur.c] + 1) {
                    dist[nr][nc] = dist[cur.r][cur.c] + 1;
                    q.push({nr, nc});
                }
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    
    cin >> N;
    int total = N * N;
    vector<int> order(total);
    for (int i = 0; i < total; ++i) {
        cin >> order[i];
        order[i]--;
    }
    
    occupied.assign(N, vector<bool>(N, false));
    dist.assign(N, vector<int>(N, INT_MAX));
    
    long long ans = 0;
    for (int idx : order) {
        int r = idx / N;
        int c = idx % N;
        if (dist[r][c] == INT_MAX) {
            bfs();
        }
        ans += dist[r][c];
        occupied[r][c] = true;
        dist[r][c] = 0;
        queue<Cell> q;
        q.push({r, c});
        while (!q.empty()) {
            Cell cur = q.front(); q.pop();
            for (int d = 0; d < 4; ++d) {
                int nr = cur.r + dr[d];
                int nc = cur.c + dc[d];
                if (nr >= 0 && nr < N && nc >= 0 && nc < N) {
                    if (dist[nr][nc] > dist[cur.r][cur.c] + 1) {
                        dist[nr][nc] = dist[cur.r][cur.c] + 1;
                        q.push({nr, nc});
                    }
                }
            }
        }
    }
    
    cout << ans << '\n';
    return 0;
}
