#include <bits/stdc++.h>
using namespace std;
int dp[20005][100][5];
string s;
int n,k;
int Rec(int index,int zeros,bool flag){
    if(zeros > k)   return 0;
    if(index == n)
        return zeros == k;
    if(dp[index][zeros][flag] + 1)    return dp[index][zeros][flag];
    int Res  =0;
    int Limit = flag?9:s[index];
    for(int i =0; i<=Limit; i++){
        Res+=Rec(index+1,zeros + (i!=0),!flag && i == s[index]?0:1);
    }
    return dp[index][zeros][flag] = Res;
}

int main()
{

    cin>>s>>k;
    n = s.length();
    for(int i = 0 ; i<n; i++)
        s[i] = s[i]-'0';
    memset(dp,-1,sizeof(dp));
    cout<<Rec(0,0,0);





    return 0;
}
