#include<bits/stdc++.h>
using namespace std;

void integer(int a){
    cout<<sizeof(a)<<endl;
}
void floating(float a){
    cout<<sizeof(a)<<endl;
}
void character(char a){
    cout<<sizeof(a)<<endl;
}

int main() {

    int a = 2;
    float b = 7.8;
    char z = 'g';

    integer(a);
    floating(b);
    character(z);
}