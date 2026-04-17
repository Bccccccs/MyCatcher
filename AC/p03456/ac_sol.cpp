#include <iostream>
#include <vector>
#include <algorithm>
#include <math.h>
#include <string>
using namespace std;

int main(){
string a,b;cin>>a>>b;
double c=stoi(a+b);
if(sqrt(c)==int(sqrt(c)))cout<<"Yes";
else cout<<"No";

}
