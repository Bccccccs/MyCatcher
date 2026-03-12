#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

int main() {
    long long N;
    long long X, M;
    cin >> N >> X >> M;

    if (M == 1 || X == 0) {
        cout << 0 << endl;
        return 0;
    }

    unordered_map<long long, int> index_map;
    vector<long long> value_seq;
    vector<long long> prefix_sum;

    long long current = X % M;
    long long sum = 0;
    int cycle_start = -1;

    for (int i = 0; i < N; ++i) {
        if (index_map.find(current) != index_map.end()) {
            cycle_start = index_map[current];
            break;
        }
        index_map[current] = i;
        value_seq.push_back(current);
        sum += current;
        prefix_sum.push_back(sum);
        current = (current * current) % M;
    }

    if (cycle_start == -1) {
        cout << sum << endl;
        return 0;
    }

    int cycle_len = value_seq.size() - cycle_start;
    long long cycle_sum = prefix_sum.back() - (cycle_start > 0 ? prefix_sum[cycle_start - 1] : 0);

    long long result = 0;
    if (N <= value_seq.size()) {
        result = prefix_sum[N - 1];
    } else {
        result = prefix_sum[cycle_start - 1];
        long long remaining = N - cycle_start;
        long long full_cycles = remaining / cycle_len;
        long long remainder = remaining % cycle_len;

        result += full_cycles * cycle_sum;
        if (remainder > 0) {
            long long rem_sum = prefix_sum[cycle_start + remainder - 1] - (cycle_start > 0 ? prefix_sum[cycle_start - 1] : 0);
            result += rem_sum;
        }
    }

    cout << result << endl;
    return 0;
}
