#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    string s;
    cin >> s;
    int n = s.length();
    long long ans = 0;
    int mod = 2019;
    vector<int> cnt(mod, 0);
    cnt[0] = 1;
    int cur = 0;
    int pow10 = 1;
    for (int i = n - 1; i >= 0; --i) {
        cur = (cur + (s[i] - '0') * pow10) % mod;
        ans += cnt[cur];
        cnt[cur]++;
        pow10 = (pow10 * 10) % mod;
    }
    cout << ans << endl;
    return 0;
}
