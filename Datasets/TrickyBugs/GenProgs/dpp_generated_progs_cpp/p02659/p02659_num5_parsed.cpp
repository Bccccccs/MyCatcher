#include <iostream>
#include <string>
using namespace std;

int main() {
    long long A;
    string B;
    cin >> A >> B;

    long long B_int = (B[0] - '0') * 100 + (B[2] - '0') * 10 + (B[3] - '0');
    long long result = A * B_int / 100;
    cout << result << endl;
    return 0;
}
