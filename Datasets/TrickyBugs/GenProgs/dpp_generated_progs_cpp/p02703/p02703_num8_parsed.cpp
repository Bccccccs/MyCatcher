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
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    long long s;
    cin >> n >> m >> s;

    vector<vector<Edge>> graph(n);
    for (int i = 0; i < m; ++i) {
        int u, v, a, b;
        cin >> u >> v >> a >> b;
        --u; --v;
        graph[u].push_back({v, a, b});
        graph[v].push_back({u, a, b});
    }

    vector<Exchange> exch(n);
    for (int i = 0; i < n; ++i) {
        cin >> exch[i].c >> exch[i].d;
    }

    int maxCoins = 50 * 50 + 50;
    if (s > maxCoins) s = maxCoins;

    vector<vector<long long>> dist(n, vector<long long>(maxCoins + 1, INF));
    priority_queue<State, vector<State>, greater<State>> pq;

    dist[0][s] = 0;
    pq.push({0, s, 0});

    while (!pq.empty()) {
        State cur = pq.top();
        pq.pop();

        if (cur.time > dist[cur.city][cur.coins]) continue;

        int cc = exch[cur.city].c;
        int dd = exch[cur.city].d;
        if (cur.coins < maxCoins) {
            long long newCoins = min((long long)maxCoins, cur.coins + cc);
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

    for (int i = 1; i < n; ++i) {
        long long ans = INF;
        for (int coin = 0; coin <= maxCoins; ++coin) {
            ans = min(ans, dist[i][coin]);
        }
        cout << ans << "\n";
    }

    return 0;
}
