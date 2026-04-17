#include<bits/stdc++.h>
using namespace std;

typedef long long ll;

int N, K;
ll mod = 1000000007;
vector<int> V;
ll dp[2][200010];
ll tmp[2][200010];

int main()
{
    cin >> N >> K;


    for(int i = 1; i * i <= N; i++)
    {
        V.push_back(i);
        V.push_back(N / i);
    }

    sort(V.begin(), V.end());
    V.erase(unique(V.begin(), V.end()), V.end());

    dp[1][0] = 1;
    for(int i = 0; i < 200010; i++)tmp[1][i] = 1;
    for(int i = 0; i < K; i++)
    {
        for(int j = 0; j < V.size(); j++)
        {
            dp[i % 2][j] = tmp[1 - i % 2][(int)(V.size()) - 1 - j] *
                           (V[j] - (j - 1 >= 0 ? V[j - 1] : 0)) % mod;
            if(j == 0)tmp[i % 2][j] = dp[i % 2][j];
            else tmp[i % 2][j] = (tmp[i % 2][j - 1] + dp[i % 2][j]) % mod;
        }
    }

    cout << tmp[1 - K % 2][(int)(V.size()) - 1] << endl;

    return 0;
}
