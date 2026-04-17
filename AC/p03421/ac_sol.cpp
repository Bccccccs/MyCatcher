#include <bits/stdc++.h>
using namespace std;

int n, a, b;

int main() {
    cin >> n >> a >> b;

    if (a+b > n+1 or a*(long long)b < n) {
        cout << "-1";
        return 0;
    }

    vector<int> v(a-1, 0);
    
    for (int i=1; i<=n-b; i++) v[i%v.size()]++;

    v.push_back(b);

    int k = 1;
    for (int i : v) {
        int l = k + i - 1;
        while (l>=k) cout << l-- << ' ';
        k += i;
    }
}