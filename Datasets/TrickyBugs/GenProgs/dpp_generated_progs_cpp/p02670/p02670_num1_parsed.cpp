#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <climits>
using namespace std;

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

    vector<vector<int>> dist(N, vector<int>(N, 0));
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
            if (nx >= 0 && nx < N && ny >= 0 && ny < N && dist[nx][ny] == 0) {
                dist[nx][ny] = dist[x][y] + 1;
                q.emplace(nx, ny);
            }
        }
    }

    vector<vector<bool>> occupied(N, vector<bool>(N, false));
    vector<vector<int>> curDist = dist;
    priority_queue<pair<int, pair<int, int>>, vector<pair<int, pair<int, int>>>, greater<>> pq;

    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            pq.emplace(curDist[i][j], make_pair(i, j));
        }
    }

    long long totalInconvenience = 0;

    for (int idx : order) {
        int x = idx / N;
        int y = idx % N;

        while (true) {
            auto [d, pos] = pq.top();
            auto [cx, cy] = pos;
            if (!occupied[cx][cy] && curDist[cx][cy] == d) {
                break;
            }
            pq.pop();
        }

        auto [d, pos] = pq.top();
        pq.pop();
        totalInconvenience += d;

        occupied[x][y] = true;
        curDist[x][y] = 0;
        pq.emplace(0, make_pair(x, y));

        queue<pair<int, int>> bfsQ;
        bfsQ.emplace(x, y);

        while (!bfsQ.empty()) {
            auto [cx, cy] = bfsQ.front();
            bfsQ.pop();
            int cd = curDist[cx][cy];
            for (int dir = 0; dir < 4; ++dir) {
                int nx = cx + dx[dir];
                int ny = cy + dy[dir];
                if (nx >= 0 && nx < N && ny >= 0 && ny < N && curDist[nx][ny] > cd + 1) {
                    curDist[nx][ny] = cd + 1;
                    bfsQ.emplace(nx, ny);
                    pq.emplace(cd + 1, make_pair(nx, ny));
                }
            }
        }
    }

    cout << totalInconvenience << '\n';
    return 0;
}
