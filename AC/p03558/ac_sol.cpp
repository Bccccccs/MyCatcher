#include <iostream>
#include<bits/stdc++.h>
#define ll long long
using namespace std;
const ll INF =1e9+7;
ll a[200000],b[2000][2000];
int main()
{
    ll i,n,m,j,k,l;
    queue<int>q;
    scanf("%lld",&n);
    a[1]=1;
    q.push(1);
    for(i=1;i<=n;i++)
    {
        a[i]=INF;
    }
    a[1]=1;
    a[0]=INF;
    while(!q.empty())
    {
        ll nn=q.front();
        q.pop();
        ll ne=nn*10%n;
        for(i=0;i<10;i++)
        {
            if(a[ne]>a[nn]+i)
            {
                a[ne]=a[nn]+i;
                q.push(ne);
            }
            ne=(ne+1)%n;
        }
    }
    printf("%lld",a[0]);
    return 0;
}
 