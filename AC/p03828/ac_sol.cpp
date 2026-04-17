#include <bits/stdc++.h>
#define int long long
#define inf 1000000007
using namespace std;
int cnt[1000];

signed main() {
	int n,ans=1;
	cin>>n;
	for(int i=2;i<=n;i++){
		int x=i,a=2;
		while(a*a<=x){
			if(x%a==0){
				cnt[a]++;
				cnt[a]%=inf;
				//cout<<a<<endl;
				x/=a;
			}
			else{
				a++;
			}
		}
		cnt[x]++;
		cnt[x]%=inf;
		//cout<<x<<endl;
	}
	for(int i=1;i<=1000;i++){
		ans*=(cnt[i]+1)%inf;
		ans%=inf;
		//cout<<cnt[i]<<endl;
	}
	cout<<ans<<endl;
}
