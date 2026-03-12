#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

int main() {
    long long N, X, M;
    cin >> N >> X >> M;

    if (M == 1) {
        cout << 0 << endl;
        return 0;
    }

    vector<long long> value(M + 1, -1);
    vector<long long> sum(M + 1, 0);
    long long a = X;
    long long total_sum = 0;
    long long steps = 0;

    while (steps < N && value[a] == -1) {
        value[a] = steps;
        total_sum += a;
        sum[steps + 1] = total_sum;
        steps++;
        a = (a * a) % M;
    }

    if (steps == N) {
        cout << total_sum << endl;
        return 0;
    }

    long long cycle_start = value[a];
    long long cycle_len = steps - cycle_start;
    long long cycle_sum = total_sum - sum[cycle_start];

    long long remaining = N - steps;
    long long full_cycles = remaining / cycle_len;
    long long extra = remaining % cycle_len;

    total_sum += full_cycles * cycle_sum;

    a = X;
    for (long long i = 0; i < cycle_start + extra; ++i) {
        if (i >= cycle_start) {
            total_sum += a;
        }
        a = (a * a) % M;
    }

    cout << total_sum << endl;
    return 0;
}
