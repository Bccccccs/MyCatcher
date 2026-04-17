#include<cstdio>
int main(){
	int n,a,b;
	scanf("%d%d%d",&n,&a,&b);
	if(a>b||(n==1&&a!=b))printf("0\n");
	else if(a==b)printf("1\n");
	else printf("%lld\n",(1ll*b*(n-1)+a)-(1ll*a*(n-1)+b)+1);
	return 0;
}
