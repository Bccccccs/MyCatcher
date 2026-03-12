#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <limits>
using namespace std;

const long long INF = numeric_limits<long long>::max() / 2;

struct Edge {
    int to;
    int costCoin;
    long long costTime;
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
    int n, m, s;
    cin >> n >> m >> s;
    
    vector<vector<Edge>> graph(n);
    for (int i = 0; i < m; ++i) {
        int u, v, a;
        long long b;
        cin >> u >> v >> a >> b;
        u--; v--;
        graph[u].push_back({v, a, b});
        graph[v].push_back({u, a, b});
    }
    
    vector<int> c(n), d(n);
    for (int i = 0; i < n; ++i) {
        cin >> c[i] >> d[i];
    }
    
    int maxCoin = 50 * 50;
    if (s > maxCoin) s = maxCoin;
    
    vector<vector<long long>> dist(n, vector<long long>(maxCoin + 1, INF));
    priority_queue<State, vector<State>, greater<State>> pq;
    
    dist[0][s] = 0;
    pq.push({0, s, 0});
    
    while (!pq.empty()) {
        State cur = pq.top();
        pq.pop();
        
        if (cur.time > dist[cur.city][cur.coin]) continue;
        
        int newCoin = min(cur.coin + c[cur.city], maxCoin);
        long long newTime = cur.time + d[cur.city];
        if (newTime < dist[cur.city][newCoin]) {
            dist[cur.city][newCoin] = newTime;
            pq.push({cur.city, newCoin, newTime});
        }
        
        for (const Edge& e : graph[cur.city]) {
            if (cur.coin >= e.costCoin) {
                int nextCoin = cur.coin - e.costCoin;
                long long nextTime = cur.time + e.costTime;
                if (nextTime < dist[e.to][nextCoin]) {
                    dist[e.to][nextCoin] = nextTime;
                    pq.push({e.to, nextCoin, nextTime});
                }
            }
        }
    }
    
    for (int i = 1; i < n; ++i) {
        long long ans = INF;
        for (int coin = 0; coin <= maxCoin; ++coin) {
            ans = min(ans, dist[i][coin]);
        }
        cout << ans << endl;
    }
    
    return 0;
}
