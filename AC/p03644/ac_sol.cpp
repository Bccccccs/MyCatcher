#include <iostream>
int N,x=2;
int main() {
  for(std::cin>>N;x<=N;x*=2);
  std::cout<<x/2<<'\n';
}