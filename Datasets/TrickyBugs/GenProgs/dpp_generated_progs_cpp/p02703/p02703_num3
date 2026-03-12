#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <limits>
using namespace std;

const long long INF = numeric_limits<long long>::max() / 2;

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
            maxCoins = max(maxCoins, s + (long long)e.a);
        }
    }
    for (int i = 1; i <= n; ++i) {
        if (exch[i].c > 0) {
            maxCoins = max(maxCoins, s + (long long)exch[i].c);
        }
    }
    maxCoins = min(maxCoins, s + 50LL * 50LL * 2);

    vector<vector<long long>> dist(n + 1, vector<long long>(maxCoins + 1, INF));
    priority_queue<State, vector<State>, greater<State>> pq;

    dist[1][min(s, maxCoins)] = 0;
    pq.push({1, min(s, maxCoins), 0});

    while (!pq.empty()) {
        State cur = pq.top();
        pq.pop();

        if (cur.time > dist[cur.city][cur.coins]) continue;

        int cc = exch[cur.city].c;
        int cd = exch[cur.city].d;
        if (cc > 0 && cur.coins < maxCoins) {
            long long newCoins = min((long long)maxCoins, cur.coins + cc);
            long long newTime = cur.time + cd;
            if (newTime < dist[cur.city][newCoins]) {
                dist[cur.city][newCoins] = newTime;
                pq.push({cur.city, newCoins, newTime});
            }
        }

        for (const auto& e : graph[cur.city]) {
            if (cur.coins >= e.a) {
                long long newCoins = min((long long)maxCoins, cur.coins - e.a);
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
        for (long long coins = 0; coins <= maxCoins; ++coins) {
            ans = min(ans, dist[i][coins]);
        }
        cout << ans << "\n";
    }

    return 0;
}
