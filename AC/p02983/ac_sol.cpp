#include <bits/stdc++.h>
using namespace std;

int main() {
  long long l,r;
  cin >> l >> r;
  r = min(r,l+2019);
  int ans = 2018;
  for(long long i = l;i <= r;i++){
    for(long long j = i+1;j <= r;j++){
      int x = (i*j)%2019;
      ans = min(ans,x);
    }
  }
  cout << ans << endl;
  return 0;
}
