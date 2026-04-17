#include <iostream>
using namespace std;
int main(void){
    // Your code here!
    int n,m;
    cin>>n>>m;
    for(int i=m/n;i>=1;i--){
        if(m%i==0){
            cout<<i<<endl;
            return 0;
        }
    }
}
