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

    unordered_map<long long, int> seen;
    vector<long long> value;
    vector<long long> prefix_sum;

    long long cur = X % M;
    long long sum = 0;
    int idx = 0;

    while (seen.find(cur) == seen.end()) {
        seen[cur] = idx;
        value.push_back(cur);
        sum += cur;
        prefix_sum.push_back(sum);
        cur = (cur * cur) % M;
        idx++;
        if (idx == N) {
            cout << sum << endl;
            return 0;
        }
    }

    int cycle_start = seen[cur];
    int cycle_len = idx - cycle_start;

    long long cycle_sum = 0;
    if (cycle_start > 0) {
        cycle_sum = prefix_sum[idx - 1] - prefix_sum[cycle_start - 1];
    } else {
        cycle_sum = prefix_sum[idx - 1];
    }

    long long ans = 0;
    if (cycle_start > 0) {
        ans = prefix_sum[cycle_start - 1];
        N -= cycle_start;
    }

    long long full_cycles = N / cycle_len;
    long long remainder = N % cycle_len;

    ans += full_cycles * cycle_sum;

    if (remainder > 0) {
        long long rem_sum = prefix_sum[cycle_start + remainder - 1];
        if (cycle_start > 0) rem_sum -= prefix_sum[cycle_start - 1];
        ans += rem_sum;
    }

    cout << ans << endl;
    return 0;
}
