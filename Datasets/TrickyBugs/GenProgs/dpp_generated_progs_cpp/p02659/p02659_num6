#include <iostream>
#include <string>
#include <cstdint>

int main() {
    int64_t A;
    std::string B;
    std::cin >> A >> B;

    int64_t integer_part = (B[0] - '0');
    int64_t decimal_part = (B[2] - '0') * 10 + (B[3] - '0');

    int64_t total = integer_part * 100 + decimal_part;

    int64_t result = A * total / 100;

    std::cout << result << std::endl;

    return 0;
}
