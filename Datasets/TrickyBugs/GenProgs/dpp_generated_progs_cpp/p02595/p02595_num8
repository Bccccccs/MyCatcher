#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    long long D;
    cin >> N >> D;

    vector<long long> distances;
    distances.reserve(N);

    for (int i = 0; i < N; ++i) {
        long long x, y;
        cin >> x >> y;
        distances.push_back(x * x + y * y);
    }

    sort(distances.begin(), distances.end());

    long long D_sq = D * D;
    auto it = upper_bound(distances.begin(), distances.end(), D_sq);
    int count = it - distances.begin();

    cout << count << "\n";

    return 0;
}
