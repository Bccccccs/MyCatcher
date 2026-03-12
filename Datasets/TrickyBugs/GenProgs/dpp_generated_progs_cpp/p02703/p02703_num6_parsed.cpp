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
    long long money;
    long long time;
    bool operator>(const State& other) const {
        return time > other.time;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

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

    vector<int> c(n + 1), d(n + 1);
    for (int i = 1; i <= n; ++i) {
        cin >> c[i] >> d[i];
    }

    long long maxMoney = s;
    for (int i = 1; i <= n; ++i) {
        maxMoney += c[i] * 2500LL;
    }
    if (maxMoney > 10000LL) maxMoney = 10000LL;

    vector<vector<long long>> dist(n + 1, vector<long long>(maxMoney + 1, INF));
    priority_queue<State, vector<State>, greater<State>> pq;

    dist[1][s] = 0;
    pq.push({1, s, 0});

    while (!pq.empty()) {
        State cur = pq.top();
        pq.pop();

        if (cur.time > dist[cur.city][cur.money]) continue;

        int city = cur.city;
        long long money = cur.money;
        long long time = cur.time;

        if (money + c[city] <= maxMoney) {
            long long nm = money + c[city];
            long long nt = time + d[city];
            if (nt < dist[city][nm]) {
                dist[city][nm] = nt;
                pq.push({city, nm, nt});
            }
        }

        for (const Edge& e : graph[city]) {
            if (money >= e.a) {
                long long nm = money - e.a;
                long long nt = time + e.b;
                if (nt < dist[e.to][nm]) {
                    dist[e.to][nm] = nt;
                    pq.push({e.to, nm, nt});
                }
            }
        }
    }

    for (int i = 2; i <= n; ++i) {
        long long ans = INF;
        for (long long money = 0; money <= maxMoney; ++money) {
            ans = min(ans, dist[i][money]);
        }
        cout << ans << "\n";
    }

    return 0;
}
