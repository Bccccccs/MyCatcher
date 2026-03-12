#include <iostream>
#include <string>
using namespace std;

int main() {
    long long A;
    string B;
    cin >> A >> B;
    
    long long integer_part = (B[0] - '0');
    long long decimal_part = (B[2] - '0') * 10 + (B[3] - '0');
    long long B_integer = integer_part * 100 + decimal_part;
    
    long long result = A * B_integer / 100;
    cout << result << endl;
    
    return 0;
}
