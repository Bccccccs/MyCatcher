#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <limits>
using namespace std;

const long long INF = 1e18;

struct Edge {
    int to, a, b;
};

struct Exchange {
    int c, d;
};

struct State {
    int city;
    long long coins;
    long long time;
    bool operator>(const State& other) const {
        return time > other.time;
    }
};

int main() {
    int n, m;
    long long s;
    cin >> n >> m >> s;

    vector<vector<Edge>> graph(n + 1);
    for (int i = 0; i < m; ++i) {
        int u, v, a, b;
        cin >> u >> v >> a >> b;
        graph[u].push_back({v, a, b});
        graph[v].push_back({u, a, b});
    }

    vector<Exchange> exch(n + 1);
    for (int i = 1; i <= n; ++i) {
        cin >> exch[i].c >> exch[i].d;
    }

    long long maxCoins = 0;
    for (int i = 1; i <= n; ++i) {
        for (const auto& e : graph[i]) {
            maxCoins = max(maxCoins, (long long)e.a);
        }
    }
    maxCoins = max(maxCoins, s);
    int coinLimit = min(maxCoins + 50 * n, 5000LL);
    coinLimit = min(coinLimit, 5000);

    vector<vector<long long>> dist(n + 1, vector<long long>(coinLimit + 1, INF));
    priority_queue<State, vector<State>, greater<State>> pq;

    dist[1][min(s, (long long)coinLimit)] = 0;
    pq.push({1, min(s, (long long)coinLimit), 0});

    while (!pq.empty()) {
        State cur = pq.top();
        pq.pop();

        if (cur.time != dist[cur.city][cur.coins]) continue;

        int cc = exch[cur.city].c;
        int dd = exch[cur.city].d;
        if (cur.coins + cc <= coinLimit) {
            long long newCoins = cur.coins + cc;
            long long newTime = cur.time + dd;
            if (newTime < dist[cur.city][newCoins]) {
                dist[cur.city][newCoins] = newTime;
                pq.push({cur.city, newCoins, newTime});
            }
        }

        for (const Edge& e : graph[cur.city]) {
            if (cur.coins >= e.a) {
                long long newCoins = cur.coins - e.a;
                long long newTime = cur.time + e.b;
                if (newTime < dist[e.to][newCoins]) {
                    dist[e.to][newCoins] = newTime;
                    pq.push({e.to, newCoins, newTime});
                }
            }
        }
    }

    for (int i = 2; i <= n; ++i) {
        long long ans = INF;
        for (int coins = 0; coins <= coinLimit; ++coins) {
            ans = min(ans, dist[i][coins]);
        }
        cout << ans << "\n";
    }

    return 0;
}
