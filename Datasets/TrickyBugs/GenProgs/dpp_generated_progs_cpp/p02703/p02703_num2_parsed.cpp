#include <iostream>
#include <vector>
#include <queue>
#include <tuple>
#include <algorithm>
#include <climits>
using namespace std;

const int MAXN = 55;
const int MAX_COIN = 2505; // n * max(c_i) = 50 * 50 = 2500, plus some margin
const long long INF = 1e18;

struct Edge {
    int to, a, b;
};

struct Node {
    int city, coins;
    long long time;
    bool operator>(const Node& other) const {
        return time > other.time;
    }
};

int main() {
    int n, m, s;
    cin >> n >> m >> s;

    vector<vector<Edge>> graph(n + 1);
    for (int i = 0; i < m; i++) {
        int u, v, a, b;
        cin >> u >> v >> a >> b;
        graph[u].push_back({v, a, b});
        graph[v].push_back({u, a, b});
    }

    vector<int> c(n + 1), d(n + 1);
    for (int i = 1; i <= n; i++) {
        cin >> c[i] >> d[i];
    }

    int maxCoin = min(s + n * 50, MAX_COIN - 5);
    vector<vector<long long>> dist(n + 1, vector<long long>(maxCoin + 1, INF));
    priority_queue<Node, vector<Node>, greater<Node>> pq;

    dist[1][min(s, maxCoin)] = 0;
    pq.push({1, min(s, maxCoin), 0});

    while (!pq.empty()) {
        auto [city, coins, curTime] = pq.top();
        pq.pop();

        if (curTime > dist[city][coins]) continue;

        // Option 1: exchange at current city
        int newCoins = min(coins + c[city], maxCoin);
        if (dist[city][newCoins] > curTime + d[city]) {
            dist[city][newCoins] = curTime + d[city];
            pq.push({city, newCoins, dist[city][newCoins]});
        }

        // Option 2: travel to adjacent cities
        for (const auto& e : graph[city]) {
            if (coins >= e.a) {
                int nc = coins - e.a;
                long long nt = curTime + e.b;
                if (dist[e.to][nc] > nt) {
                    dist[e.to][nc] = nt;
                    pq.push({e.to, nc, nt});
                }
            }
        }
    }

    for (int i = 2; i <= n; i++) {
        long long ans = INF;
        for (int coin = 0; coin <= maxCoin; coin++) {
            ans = min(ans, dist[i][coin]);
        }
        cout << ans << "\n";
    }

    return 0;
}
