#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    cin >> n >> m;

    vector<long long> a(n);
    for (int i = 0; i < n; ++i) {
        cin >> a[i];
    }

    sort(a.begin(), a.end(), greater<long long>());

    long long sum_top_m = 0;
    for (int i = 0; i < m; ++i) {
        sum_top_m += a[i];
    }

    if (a[m - 1] * 4 * m >= sum_top_m) {
        cout << "Yes\n";
    } else {
        cout << "No\n";
    }

    return 0;
}
