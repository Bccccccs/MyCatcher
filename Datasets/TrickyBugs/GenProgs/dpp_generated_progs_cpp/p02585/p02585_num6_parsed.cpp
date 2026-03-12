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

        if (cycle_sum > 0 && K > cycle_len) {
            long long full_cycles = K / cycle_len;
            long long remainder = K % cycle_len;
            long long candidate1 = (full_cycles - 1) * cycle_sum;
            long long candidate2 = full_cycles * cycle_sum;
            long long max_mid = LLONG_MIN;
            long long temp_sum = 0;

            for (int i = 0; i < cycle_len; ++i) {
                cur = P[cur];
                temp_sum += C[cur];
                if (i < remainder) max_mid = max(max_mid, temp_sum);
                if (i < cycle_len) max_mid = max(max_mid, temp_sum);
            }

            answer = max(answer, max(candidate1 + max_mid, candidate2 + max_mid));
        } else {
            long long temp_sum = 0;
            cur = start;
            for (int i = 0; i < min((long long)cycle_len, K); ++i) {
                cur = P[cur];
                temp_sum += C[cur];
                answer = max(answer, temp_sum);
            }
        }
    }

    cout << answer << endl;
    return 0;
}
