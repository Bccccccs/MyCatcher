#include <stdio.h>
int n,k,ans,x;
int main () {
  scanf ("%d%d",&n,&k);
  while (n>=1) {
    ans++;
    n/=k;
  }
  printf ("%d\n",ans);
  return 0;
}