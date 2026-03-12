#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

int main() {
    long long N;
    long long X, M;
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
        if (current == 0) {
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

    long long total = 0;
    if (N <= value_seq.size()) {
        total = prefix_sum[N - 1];
    } else {
        total = prefix_sum[cycle_start - 1];
        long long remaining = N - cycle_start;
        total += (remaining / cycle_len) * cycle_sum;
        long long extra = remaining % cycle_len;
        if (extra > 0) {
            total += prefix_sum[cycle_start + extra - 1] - (cycle_start > 0 ? prefix_sum[cycle_start - 1] : 0);
        }
    }

    cout << total << endl;
    return 0;
}
