#include<bits/stdc++.h>
using namespace std;

int main(){
  int n,max=0,b=0;
  cin >> n;
  int a[n];
  for(int i=0;i<n;i++){
    cin >> a[i];
    if(max<a[i]){
      max = a[i];
      b = i;
    }
  }
  sort(a,a+n);
 for(int i=0;i<n;i++){
   if(i!=b)
     cout << max << endl;
   else
     cout << a[n-2] << endl;
 }
}