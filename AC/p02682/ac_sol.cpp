#include<iostream>
using namespace std;
int main(){
	long long a,b,c,d;
	cin>>a>>b>>c>>d;
	cout<<max(0LL,min(a,d))-max(0LL,d-b-a);
	return 0;
}
