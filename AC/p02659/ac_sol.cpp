#include<bits/stdc++.h>
using namespace std;
int main() {
  int64_t a,c;
  double b;
  cin>>a>>b;
  c=(b+0.001)*100;
  c=c*a/100;
  cout<<c<<endl;
}