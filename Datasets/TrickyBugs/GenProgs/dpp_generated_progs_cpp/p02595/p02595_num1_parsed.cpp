#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int N;
    long long D;
    std::cin >> N >> D;

    std::vector<long long> distances;
    distances.reserve(N);

    for (int i = 0; i < N; ++i) {
        long long x, y;
        std::cin >> x >> y;
        distances.push_back(x * x + y * y);
    }

    std::sort(distances.begin(), distances.end());

    long long D_sq = D * D;
    int count = std::upper_bound(distances.begin(), distances.end(), D_sq) - distances.begin();

    std::cout << count << '\n';

    return 0;
}
