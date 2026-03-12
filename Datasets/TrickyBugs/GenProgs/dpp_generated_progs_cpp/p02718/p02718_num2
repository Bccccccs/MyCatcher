#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdint>

int main() {
    int n, m;
    std::cin >> n >> m;
    std::vector<int64_t> votes(n);
    for (int i = 0; i < n; ++i) {
        std::cin >> votes[i];
    }
    std::sort(votes.begin(), votes.end(), std::greater<int64_t>());
    int64_t sum_top_m = 0;
    for (int i = 0; i < m; ++i) {
        sum_top_m += votes[i];
    }
    int64_t threshold_votes = votes[m - 1];
    if (threshold_votes * 4 * m >= sum_top_m) {
        std::cout << "Yes\n";
    } else {
        std::cout << "No\n";
    }
    return 0;
}
