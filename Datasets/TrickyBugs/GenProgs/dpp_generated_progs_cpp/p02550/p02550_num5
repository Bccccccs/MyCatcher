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

    vector<long long> value;
    unordered_map<long long, int> pos;
    long long cur = X % M;
    long long sum = 0;
    int start_cycle = -1;

    for (int i = 0; i < N; ++i) {
        if (pos.find(cur) != pos.end()) {
            start_cycle = pos[cur];
            break;
        }
        pos[cur] = i;
        value.push_back(cur);
        sum += cur;
        cur = (cur * cur) % M;
        if (cur == 0) {
            cout << sum << endl;
            return 0;
        }
    }

    if (start_cycle == -1) {
        cout << sum << endl;
        return 0;
    }

    int cycle_len = value.size() - start_cycle;
    long long cycle_sum = 0;
    for (int i = start_cycle; i < value.size(); ++i) {
        cycle_sum += value[i];
    }

    long long remain = N - value.size();
    if (remain <= 0) {
        cout << sum << endl;
        return 0;
    }

    long long full_cycles = remain / cycle_len;
    long long extra = remain % cycle_len;

    sum += full_cycles * cycle_sum;
    for (int i = 0; i < extra; ++i) {
        sum += value[start_cycle + i];
    }

    cout << sum << endl;
    return 0;
}
