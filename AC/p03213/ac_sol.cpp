#include <bits/stdc++.h>
#define rp(i,n) for(int i=0; i<n; i++)
using namespace std;
using ll=long long;
using P=pair<int,int>;
using G=vector<vector<int>>;

int howmany(int x,int p){
    if(x<p) return 0;
    return x/p+howmany(x/p,p);
}
int main(){
    int n;
    cin >> n;
    int prime[15]={2,3,5,7,11,13,17,19,23,29,31,37,41,43,47};
    int a=0,b=0,c=0,d=0,e=0;
    for(int i=0; i<15; i++){
        int m=howmany(n,prime[i]);
        if(m>=2) a++;
        if(m>=4) b++;
        if(m>=14) c++;
        if(m>=24) d++;
        if(m>=74) e++;
    }
    int ans=(a-2)*b*(b-1)/2+(b-1)*c+(a-1)*d+e;
    cout << ans << endl;
    return 0;
}