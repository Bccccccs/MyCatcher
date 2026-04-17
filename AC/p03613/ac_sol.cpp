#include <bits/stdc++.h>

using namespace std;

int n;
int a[100001];
int main() {
  cin >> n;
  for(int i = 0; i < n; i++) {
    int x;
    cin >> x;
    if(x > 0) a[x-1]++;
    a[x]++;
    a[x+1]++;
  }
  int ans = 0;
  for(int i = 0; i < 100001; i++) {
    ans = max(ans,a[i]);
  }

  cout << ans << endl;
}

  
  
