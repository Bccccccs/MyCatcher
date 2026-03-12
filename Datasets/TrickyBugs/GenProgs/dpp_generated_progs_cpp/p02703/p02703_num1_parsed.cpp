#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <limits>
using namespace std;

const long long INF = numeric_limits<long long>::max() / 4;

struct Edge {
    int to, a, b;
};

struct State {
    int city;
    long long time;
    int coins;
    bool operator>(const State& other) const {
        return time > other.time;
    }
};

int main() {
    int n, m;
    long long s;
    cin >> n >> m >> s;

    vector<vector<Edge>> graph(n);
    for (int i = 0; i < m; ++i) {
        int u, v, a, b;
        cin >> u >> v >> a >> b;
        u--; v--;
        graph[u].push_back({v, a, b});
        graph[v].push_back({u, a, b});
    }

    vector<int> c(n), d(n);
    for (int i = 0; i < n; ++i) {
        cin >> c[i] >> d[i];
    }

    int maxCoins = 50 * 50 + 50;
    if (s > maxCoins) s = maxCoins;

    vector<vector<long long>> dist(n, vector<long long>(maxCoins + 1, INF));
    priority_queue<State, vector<State>, greater<State>> pq;

    dist[0][s] = 0;
    pq.push({0, 0, (int)s});

    while (!pq.empty()) {
        State cur = pq.top();
        pq.pop();

        if (cur.time > dist[cur.city][cur.coins]) continue;

        int nc = min(maxCoins, cur.coins + c[cur.city]);
        if (dist[cur.city][nc] > cur.time + d[cur.city]) {
            dist[cur.city][nc] = cur.time + d[cur.city];
            pq.push({cur.city, dist[cur.city][nc], nc});
        }

        for (const Edge& e : graph[cur.city]) {
            if (cur.coins >= e.a) {
                int newCoins = cur.coins - e.a;
                long long newTime = cur.time + e.b;
                if (dist[e.to][newCoins] > newTime) {
                    dist[e.to][newCoins] = newTime;
                    pq.push({e.to, newTime, newCoins});
                }
            }
        }
    }

    for (int i = 1; i < n; ++i) {
        long long ans = INF;
        for (int coins = 0; coins <= maxCoins; ++coins) {
            ans = min(ans, dist[i][coins]);
        }
        cout << ans << endl;
    }

    return 0;
}
