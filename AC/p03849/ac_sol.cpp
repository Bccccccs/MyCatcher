#include <bits/stdc++.h>
using namespace std;

const int64_t MOD = 1e9+7;

void add(int64_t& a, int64_t b){
    a = (a+b)%MOD;
}
int nth_bit(int64_t num , int n) {
    return (num >> n) & 1;
}

int main() {
    int64_t N;
    cin >> N;

    int64_t dp[61][3] = {0};
    dp[60][0] = 1;

    for(int d = 59; d >= 0; d--) {
        for(int s = 0; s <= 2; s++) {
            for (int k = 0; k <= 2; k++) {
                int s2 = min(2, 2*s+nth_bit(N, d) - k);
                if (s2 >= 0) add(dp[d][s2], dp[d+1][s]);
            }

        }
    }


    int64_t ans = (dp[0][0] + dp[0][1] + dp[0][2]) % MOD;
    cout << ans << endl;
    return 0;
}