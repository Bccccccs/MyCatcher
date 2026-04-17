#include <bits/stdc++.h>
using namespace std;

int main(){
  int n; cin>>n;
  vector<int> b(n-1);
  for(int i=0; i<n-1; ++i)cin>>b[i];

  int ans=0;
  for(int i=1; i<n-1; ++i)ans+=min(b[i], b[i-1]);
  ans+=b[0]+b[n-2];

  cout<<ans<<endl;
}
