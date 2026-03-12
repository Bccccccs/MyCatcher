#include <iostream>
#include <vector>
#include <algorithm>
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

    long long threshold = sum_top_m / (4 * m);
    if (sum_top_m % (4 * m) != 0) {
        threshold++;
    }

    if (a[m - 1] >= threshold) {
        cout << "Yes\n";
    } else {
        cout << "No\n";
    }

    return 0;
}
