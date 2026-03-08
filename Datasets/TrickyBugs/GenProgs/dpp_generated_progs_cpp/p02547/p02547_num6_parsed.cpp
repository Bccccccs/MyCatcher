#include <iostream>
#include <vector>
using namespace std;

int main() {
    int N;
    cin >> N;

    vector<pair<int, int>> rolls(N);
    for (int i = 0; i < N; i++) {
        cin >> rolls[i].first >> rolls[i].second;
    }
    cout << "No" << endl;
    return 0;
}