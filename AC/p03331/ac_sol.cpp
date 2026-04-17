#include<algorithm>
#include<iostream>
#include<string>
using namespace std;

int main() {
	int n;
	cin >> n;
	int cnt = 0;
	while (n > 0) {
		cnt += n % 10;
		n /= 10;
	}
	if (cnt == 1) {
		cout << 10 << endl;
	}
	else {
		cout << cnt << endl;
	}
	
}