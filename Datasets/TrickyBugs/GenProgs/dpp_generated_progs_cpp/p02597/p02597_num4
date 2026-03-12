#include <iostream>
#include <string>
using namespace std;

int main() {
    int N;
    string S;
    cin >> N >> S;

    int totalR = 0;
    for (char c : S) {
        if (c == 'R') totalR++;
    }

    int misplacedR = 0;
    for (int i = 0; i < totalR; i++) {
        if (S[i] == 'W') misplacedR++;
    }

    cout << misplacedR << endl;
    return 0;
}
