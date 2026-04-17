#include<cstdio>
using namespace std;
typedef long long LL;
LL n,num=1;
int ans1,ans2;
int main()
{
	scanf("%lld",&n);
	for(LL x=n;x;x/=10) ans1+=x%10,num*=10;
	num/=10;
	for(LL x=n/num*num-1;x;x/=10) ans2+=x%10;
	printf("%d",ans1>ans2?ans1:ans2);
	return 0;
}