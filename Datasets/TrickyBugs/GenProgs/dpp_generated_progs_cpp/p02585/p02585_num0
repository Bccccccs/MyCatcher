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

        if (cycle_sum > 0 && K > cycle_len) {
            long long full_cycles = K / cycle_len;
            long long remainder = K % cycle_len;
            long long candidate1 = (full_cycles - 1) * cycle_sum;
            long long candidate2 = full_cycles * cycle_sum;
            long long max_mid = LLONG_MIN;
            long long temp_sum = 0;
            int temp_steps = 0;
            current = start;
            while (temp_steps < cycle_len) {
                current = P[current];
                temp_sum += C[current];
                temp_steps++;
                if (temp_steps <= remainder) {
                    max_mid = max(max_mid, temp_sum);
                }
            }
            answer = max(answer, max(candidate1 + cycle_sum + max_mid, candidate2 + max_mid));
        } else {
            int steps_limit = min((long long)cycle_len, K);
            long long temp_sum = 0;
            current = start;
            for (int s = 0; s < steps_limit; ++s) {
                current = P[current];
                temp_sum += C[current];
                answer = max(answer, temp_sum);
            }
        }
    }

    cout << answer << endl;
    return 0;
}
