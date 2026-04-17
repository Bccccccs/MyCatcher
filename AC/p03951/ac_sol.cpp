#include <iostream>
#include <string>
using namespace std;
int main() {
  int N;
  string a, b;
  cin >> N >> a >> b;
  for(int i = 0; i <= N; ++i) {
    if(a.substr(i, N - i) == b.substr(0, N - i)){
	  cout << N + i << endl;
      return 0;
    }
  }
}
