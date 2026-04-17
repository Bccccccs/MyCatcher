#include <iostream>
#include <string>
#include <set>

using namespace std;

int main() {
	string s;
	cin >> s;

	set<int> alpha;
	for (auto c : s) {
		alpha.insert(c);
	}

	cout << (s.size() == alpha.size() ? "yes" : "no") << endl;
	return 0;
}
