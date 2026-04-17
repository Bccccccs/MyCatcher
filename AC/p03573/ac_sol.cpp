#include<iostream>
using namespace std;
int main(){
 int a,b,c,d;
 cin>>a>>b>>c;
 if(a==b){
 d=c;
 }
 else if(a==c){
 d=b;
 }
 else if(b==c){
 d=a;
 }
 cout<<d;
}