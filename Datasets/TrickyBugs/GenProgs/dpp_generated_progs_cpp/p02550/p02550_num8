#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

int main() {
    long long N, X, M;
    cin >> N >> X >> M;

    if (M == 1) {
        cout << 0 << endl;
        return 0;
    }

    unordered_map<long long, int> seen;
    vector<long long> prefix_sum;
    long long current = X % M;
    long long sum = 0;
    int idx = 0;

    while (seen.find(current) == seen.end() && idx < N) {
        seen[current] = idx;
        sum += current;
        prefix_sum.push_back(sum);
        current = (current * current) % M;
        idx++;
    }

    if (idx == N) {
        cout << sum << endl;
        return 0;
    }

    int cycle_start = seen[current];
    int cycle_len = idx - cycle_start;

    long long cycle_sum = 0;
    if (cycle_len > 0) {
        if (cycle_start > 0) {
            cycle_sum = prefix_sum[idx - 1] - prefix_sum[cycle_start - 1];
        } else {
            cycle_sum = prefix_sum[idx - 1];
        }
    }

    long long result = 0;
    if (cycle_start > 0) {
        result = prefix_sum[cycle_start - 1];
        N -= cycle_start;
    }

    if (cycle_len > 0) {
        long long full_cycles = N / cycle_len;
        long long remainder = N % cycle_len;

        result += full_cycles * cycle_sum;

        if (remainder > 0) {
            long long rem_sum = 0;
            if (cycle_start + remainder - 1 >= 0) {
                if (cycle_start > 0) {
                    rem_sum = prefix_sum[cycle_start + remainder - 1] - prefix_sum[cycle_start - 1];
                } else {
                    rem_sum = prefix_sum[cycle_start + remainder - 1];
                }
            }
            result += rem_sum;
        }
    } else {
        result = prefix_sum[N - 1];
    }

    cout << result << endl;
    return 0;
}
