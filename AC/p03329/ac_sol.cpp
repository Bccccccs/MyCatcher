#include<iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    int ans = 1e9+1;
    for(int i = 0; i <= n; i++) {
        int a = i, b = n - i;
        int cnt = 0;
        while(a > 0) cnt += a%6, a /= 6; 
        while(b > 0) cnt += b%9, b /= 9;
        ans = min(ans, cnt);
    }

    cout << ans << endl;

    return 0;
}