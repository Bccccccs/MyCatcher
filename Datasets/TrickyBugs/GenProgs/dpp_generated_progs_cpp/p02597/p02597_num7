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
    
    int rInWrongPlace = 0;
    for (int i = 0; i < totalR; i++) {
        if (S[i] == 'W') rInWrongPlace++;
    }
    
    cout << rInWrongPlace << endl;
    return 0;
}
