#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    
    int N;
    std::cin >> N;
    
    std::vector<long long> H(N);
    for (int i = 0; i < N; ++i) {
        std::cin >> H[i];
    }
    
    long long operations = 0;
    for (int i = 1; i < N; ++i) {
        if (H[i] < H[i - 1]) {
            operations += H[i - 1] - H[i];
            H[i] = H[i - 1];
        }
    }
    
    std::cout << operations << '\n';
    
    return 0;
}
