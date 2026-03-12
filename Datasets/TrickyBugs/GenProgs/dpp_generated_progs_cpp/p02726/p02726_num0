#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int N, X, Y;
    cin >> N >> X >> Y;

    vector<int> ans(N, 0);

    for (int i = 1; i <= N; ++i) {
        for (int j = i + 1; j <= N; ++j) {
            int d = j - i;
            int d2 = abs(X - i) + 1 + abs(Y - j);
            int d3 = abs(Y - i) + 1 + abs(X - j);
            int dist = min(d, min(d2, d3));
            ans[dist]++;
        }
    }

    for (int k = 1; k <= N - 1; ++k) {
        cout << ans[k] << endl;
    }

    return 0;
}
