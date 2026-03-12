#include <iostream>
using namespace std;

int main() {
    int N;
    cin >> N;
    
    int count = 0;
    bool found = false;
    
    for (int i = 0; i < N; ++i) {
        int a, b;
        cin >> a >> b;
        
        if (a == b) {
            count++;
            if (count >= 3) {
                found = true;
            }
        } else {
            count = 0;
        }
    }
    
    if (found) {
        cout << "Yes" << endl;
    } else {
        cout << "No" << endl;
    }
    
    return 0;
}
