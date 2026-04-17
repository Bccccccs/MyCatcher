#include<bits/stdc++.h>
using namespace std;
long long n,m;
int main()
{
	cin>>n>>m;
	long long cc=n*2+m;
	cout<<min(cc/4,m/2);
	return 0;
}