#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int N, X, Y;
    cin >> N >> X >> Y;
    
    vector<int> count(N, 0);
    
    for (int i = 1; i <= N; ++i) {
        for (int j = i + 1; j <= N; ++j) {
            int dist = min(j - i, 
                           min(abs(i - X) + 1 + abs(j - Y),
                               abs(i - Y) + 1 + abs(j - X)));
            count[dist]++;
        }
    }
    
    for (int k = 1; k <= N - 1; ++k) {
        cout << count[k] << "\n";
    }
    
    return 0;
}
