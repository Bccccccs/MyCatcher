#include <stdio.h>

int main(){
  int N;
  char S[101],T[101];
  scanf("%d",&N);
  scanf("%s %s",S,T);
  for(int i=0;i<N;i++)printf("%c%c",S[i],T[i]);
  printf("\n");
}