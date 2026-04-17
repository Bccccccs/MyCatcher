#include <iostream>
#include <algorithm>
using namespace std;
int main()
{
int n;
cin>>n;
int cp=n;
int sum=0;
while(cp)
{
sum+=cp%10;
cp/=10;
}
bool f=n%sum==0;
cout<<(f?"Yes":"No");
}