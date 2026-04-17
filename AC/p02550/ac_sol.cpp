#include <iostream>
#include <vector>
using namespace std;

int main(){
  long long N, X, M;
  cin >> N >> X >> M;
  vector<bool> appeared(M,false);
  long long ans = 0;
  vector<long long> A;
  for(long long i = 0; i < N; ++i){
    ans += X;
    A.push_back(X);
    appeared[X] = true;
    X = (X*X)%M;
    if(appeared[X]){
      long long s = X, c = 1;
      while(A.back() != X){
        ++c;
        s += A.back();
        A.pop_back();
      }
      // ans += s*(N-i)/c;
      // N %= c;
      long long d = (N-i-1)/c;
      ans += d*s;
      i += d*c;
      for(; i+1 < N; ++i){
        ans += X;
        X = (X*X)%M;
      }
      break;
    }
  }
  cout << ans << endl;
}
