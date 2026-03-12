#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <limits>
using namespace std;

const long long INF = 1e18;
const int MAX_COIN = 2500; // n * max(c_i) <= 50 * 50 = 2500

struct Edge {
    int to, a, b;
};

struct State {
    int city;
    int coin;
    long long time;
    bool operator>(const State& other) const {
        return time > other.time;
    }
};

int main() {
    int n, m;
    long long s;
    cin >> n >> m >> s;

    vector<vector<Edge>> graph(n);
    for (int i = 0; i < m; i++) {
        int u, v, a, b;
        cin >> u >> v >> a >> b;
        u--; v--;
        graph[u].push_back({v, a, b});
        graph[v].push_back({u, a, b});
    }

    vector<int> c(n), d(n);
    for (int i = 0; i < n; i++) {
        cin >> c[i] >> d[i];
    }

    int maxCoin = MAX_COIN;
    vector<vector<long long>> dist(n, vector<long long>(maxCoin + 1, INF));
    priority_queue<State, vector<State>, greater<State>> pq;

    int startCoin = min((long long)maxCoin, s);
    dist[0][startCoin] = 0;
    pq.push({0, startCoin, 0});

    while (!pq.empty()) {
        State cur = pq.top();
        pq.pop();
        int u = cur.city;
        int coin = cur.coin;
        long long time = cur.time;
        if (time > dist[u][coin]) continue;

        // Exchange at city u
        if (coin < maxCoin) {
            int newCoin = min(maxCoin, coin + c[u]);
            long long newTime = time + d[u];
            if (newTime < dist[u][newCoin]) {
                dist[u][newCoin] = newTime;
                pq.push({u, newCoin, newTime});
            }
        }

        // Travel along edges
        for (const Edge& e : graph[u]) {
            if (coin >= e.a) {
                int newCoin = coin - e.a;
                long long newTime = time + e.b;
                if (newTime < dist[e.to][newCoin]) {
                    dist[e.to][newCoin] = newTime;
                    pq.push({e.to, newCoin, newTime});
                }
            }
        }
    }

    for (int i = 1; i < n; i++) {
        long long ans = INF;
        for (int coin = 0; coin <= maxCoin; coin++) {
            ans = min(ans, dist[i][coin]);
        }
        cout << ans << endl;
    }

    return 0;
}
