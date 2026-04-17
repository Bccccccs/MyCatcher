#include<iostream>
using namespace std;
int main() {
  char c;
  int N = 0;
  while(scanf("%c",&c) == 1) {
    if('0'<=c && c<='9')N += (c - '0');
  }
  cout << (N%9 == 0?"Yes":"No") << endl;
}