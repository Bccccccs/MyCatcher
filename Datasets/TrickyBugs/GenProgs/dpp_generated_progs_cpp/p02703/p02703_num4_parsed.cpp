#include <iostream>
#include <vector>
#include <queue>
#include <tuple>
#include <algorithm>
#include <climits>
using namespace std;

struct Edge {
    int to, a, b;
};

struct Exchange {
    int c, d;
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
    
    vector<Exchange> exch(n + 1);
    for (int i = 1; i <= n; i++) {
        cin >> exch[i].c >> exch[i].d;
    }
    
    const int MAX_COIN = 2500;
    int coin_limit = min(s + (n - 1) * 50, MAX_COIN);
    
    vector<vector<long long>> dist(n + 1, vector<long long>(coin_limit + 1, LLONG_MAX));
    using State = tuple<long long, int, int>;
    priority_queue<State, vector<State>, greater<State>> pq;
    
    dist[1][min(s, coin_limit)] = 0;
    pq.push({0, 1, min(s, coin_limit)});
    
    while (!pq.empty()) {
        auto [time, city, coins] = pq.top();
        pq.pop();
        
        if (time > dist[city][coins]) continue;
        
        int new_coins = min(coins + exch[city].c, coin_limit);
        long long new_time = time + exch[city].d;
        if (new_time < dist[city][new_coins]) {
            dist[city][new_coins] = new_time;
            pq.push({new_time, city, new_coins});
        }
        
        for (auto& e : graph[city]) {
            if (coins >= e.a) {
                int nc = coins - e.a;
                long long nt = time + e.b;
                if (nt < dist[e.to][nc]) {
                    dist[e.to][nc] = nt;
                    pq.push({nt, e.to, nc});
                }
            }
        }
    }
    
    for (int i = 2; i <= n; i++) {
        long long ans = LLONG_MAX;
        for (int c = 0; c <= coin_limit; c++) {
            ans = min(ans, dist[i][c]);
        }
        cout << ans << endl;
    }
    
    return 0;
}
