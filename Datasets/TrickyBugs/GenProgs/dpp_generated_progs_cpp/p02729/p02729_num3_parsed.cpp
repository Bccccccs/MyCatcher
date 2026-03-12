#include <iostream>
using namespace std;

int main() {
    long long n, m;
    cin >> n >> m;
    long long red_pairs = n * (n - 1) / 2;
    long long blue_pairs = m * (m - 1) / 2;
    cout << red_pairs + blue_pairs << endl;
    return 0;
}
