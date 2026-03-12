#include <iostream>
#include <vector>
#include <unordered_map>
#include <algorithm>
using namespace std;

int main() {
    long long N, X, M;
    cin >> N >> X >> M;

    if (M == 1) {
        cout << 0 << endl;
        return 0;
    }

    unordered_map<long long, int> index_map;
    vector<long long> value_seq;
    vector<long long> prefix_sum;

    long long current = X % M;
    long long sum = 0;
    int cycle_start = -1;

    for (int i = 0; i < min(N, M + 10LL); ++i) {
        if (index_map.find(current) != index_map.end()) {
            cycle_start = index_map[current];
            break;
        }
        index_map[current] = i;
        value_seq.push_back(current);
        sum += current;
        prefix_sum.push_back(sum);
        current = (current * current) % M;
        if (N == value_seq.size()) {
            cout << sum << endl;
            return 0;
        }
    }

    if (cycle_start == -1) {
        cout << sum << endl;
        return 0;
    }

    int cycle_len = value_seq.size() - cycle_start;
    long long cycle_sum = prefix_sum.back() - (cycle_start > 0 ? prefix_sum[cycle_start - 1] : 0);

    long long result = 0;
    if (cycle_start > 0) {
        result += prefix_sum[cycle_start - 1];
        N -= cycle_start;
    }

    long long full_cycles = N / cycle_len;
    result += full_cycles * cycle_sum;

    long long remainder = N % cycle_len;
    for (int i = 0; i < remainder; ++i) {
        result += value_seq[cycle_start + i];
    }

    cout << result << endl;
    return 0;
}
