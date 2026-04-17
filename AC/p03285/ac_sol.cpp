#include <iostream>
using namespace std;
 
int
main()
{
int N;
 
cin >> N;
 
int n = 0;
while(n <= N)
{
if((N-n) % 7 == 0)
{
cout << "Yes\n";
return 0;
}
n += 4;
}
 
cout << "No\n";
 
return 0;
}