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
        int cur = start;
        long long cycle_sum = 0;
        int cycle_len = 0;

        while (true) {
            cur = P[cur];
            cycle_sum += C[cur];
            cycle_len++;
            if (cur == start) break;
        }

        long long path_sum = 0;
        int steps = 0;
        cur = start;

        while (true) {
            cur = P[cur];
            steps++;
            path_sum += C[cur];

            if (steps > K) break;

            long long score = path_sum;
            if (cycle_sum > 0) {
                long long full_cycles = (K - steps) / cycle_len;
                score += full_cycles * cycle_sum;
            }
            answer = max(answer, score);

            if (cur == start) break;
        }
    }

    cout << answer << endl;
    return 0;
}
