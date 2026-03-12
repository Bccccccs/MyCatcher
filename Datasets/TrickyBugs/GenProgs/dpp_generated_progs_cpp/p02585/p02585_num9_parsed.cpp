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
        int pos = start;
        long long cycle_sum = 0;
        int cycle_len = 0;

        while (true) {
            cycle_len++;
            pos = P[pos];
            cycle_sum += C[pos];
            if (pos == start) break;
        }

        pos = start;
        long long path_sum = 0;
        int steps = 0;

        while (true) {
            steps++;
            if (steps > K) break;

            pos = P[pos];
            path_sum += C[pos];

            long long cycles = (K - steps) / cycle_len;
            long long total = path_sum;
            if (cycle_sum > 0) {
                total += cycles * cycle_sum;
            }

            answer = max(answer, total);

            if (pos == start) break;
        }
    }

    cout << answer << endl;

    return 0;
}
