#include <iostream>
#include <cmath>
using namespace std;

int main()
{
  int X;
  cin >> X;

  int ans = 1;
  for(int i = 2; i < X; ++i) {
    for(int j = 2; pow(i, j) <= X; ++j) {
      ans = max(ans, int(pow(i, j)));
    }
  }

  cout << ans << endl;
}
