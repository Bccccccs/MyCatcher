#include <iostream>
using namespace std;
int main() {
	int n;
	cin >> n;
	string s, str, str2;
	cin >> s;
	str = s.substr(0, n/2);
	str2 = s.substr(n/2, n);
	if (str == str2) cout << "Yes\n";
	else cout << "No\n";
	return 0;
}
