#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>

using namespace std;

int main() {
    int N;
    long long K;
    cin >> N >> K;
    
    vector<int> P(N);
    vector<long long> C(N);
    
    for (int i = 0; i < N; ++i) {
        cin >> P[i];
        P[i]--;
    }
    for (int i = 0; i < N; ++i) {
        cin >> C[i];
    }
    
    long long answer = LLONG_MIN;
    
    for (int start = 0; start < N; ++start) {
        int current = start;
        long long cycle_sum = 0;
        int cycle_len = 0;
        
        while (true) {
            current = P[current];
            cycle_sum += C[current];
            cycle_len++;
            if (current == start) break;
        }
        
        long long path_sum = 0;
        int steps = 0;
        current = start;
        
        while (true) {
            current = P[current];
            steps++;
            path_sum += C[current];
            
            if (steps > K) break;
            
            long long cycles = 0;
            if (cycle_sum > 0) {
                cycles = (K - steps) / cycle_len;
            }
            
            long long total = path_sum + cycles * cycle_sum;
            answer = max(answer, total);
            
            if (current == start) break;
        }
    }
    
    cout << answer << endl;
    
    return 0;
}
