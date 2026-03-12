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
    long long current_max = H[0];
    
    for (int i = 1; i < N; ++i) {
        if (H[i] < current_max) {
            operations += current_max - H[i];
        } else {
            current_max = H[i];
        }
    }
    
    cout << operations << '\n';
    
    return 0;
}
