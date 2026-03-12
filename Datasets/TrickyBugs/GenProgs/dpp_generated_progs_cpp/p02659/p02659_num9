#include <iostream>
#include <string>
using namespace std;

int main() {
    long long A;
    string B;
    cin >> A >> B;

    int whole = (B[0] - '0');
    int tenth = (B[2] - '0');
    int hundredth = (B[3] - '0');
    long long B_integer = whole * 100 + tenth * 10 + hundredth;

    long long result = A * B_integer / 100;
    cout << result << endl;

    return 0;
}
