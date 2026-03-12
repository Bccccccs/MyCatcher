#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int N;
    cin >> N;
    
    vector<long long> H(N);
    for (int i = 0; i < N; ++i) {
        cin >> H[i];
    }
    
    long long operations = 0;
    for (int i = 1; i < N; ++i) {
        if (H[i] < H[i-1]) {
            operations += H[i-1] - H[i];
            H[i] = H[i-1];
        }
    }
    
    cout << operations << '\n';
    
    return 0;
}
