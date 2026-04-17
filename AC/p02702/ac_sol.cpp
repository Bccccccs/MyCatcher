#include<bits//stdc++.h>
using namespace std;
#define rrep(i,n) for(int i = n -1;i >= 0;i--)
typedef long long int ll;
ll  ans = 0, h = 1, now = 0;
int main() {
    string s; cin >> s;
    vector<int> as(2020, 0); as[0]++;
    rrep(i, s.size()) {
        now = (now + (s[i] - '0') * h) % 2019;
        h = h * 10 % 2019;
        ans += as[now];
        as[now]++;
    }cout << ans << endl;
}
