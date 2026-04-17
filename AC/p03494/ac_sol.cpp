#include <bits/stdc++.h>
using namespace std;

int main() {
  int n,a,k;
  int ans=1000000;
  cin >>n;
  for(int i=0;i<n;i++){
    cin >> a;
    k=0;
    while(a%2==0){
      k++;
      a/=2;
    }
    ans=min(ans,k);
  }
  
  
  cout << ans << "\n";
}