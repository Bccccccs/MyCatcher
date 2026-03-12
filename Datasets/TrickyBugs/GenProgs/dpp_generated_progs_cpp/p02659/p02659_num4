#include <iostream>
#include <string>

int main() {
    long long A;
    std::string B;
    std::cin >> A >> B;

    long long B_int = 0;
    bool after_decimal = false;
    int decimal_places = 0;

    for (char c : B) {
        if (c == '.') {
            after_decimal = true;
            continue;
        }
        B_int = B_int * 10 + (c - '0');
        if (after_decimal) {
            decimal_places++;
        }
    }

    long long result = A * B_int;
    for (int i = 0; i < decimal_places; i++) {
        result /= 10;
    }

    std::cout << result << std::endl;
    return 0;
}
