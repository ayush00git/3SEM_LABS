// implement these in a single program
// 1. tell even or odd using bitwise operator
// 2. swap 2 numbers wo using the third variable
// 3. print the fibonacci series
// 4. fond the quotient and remainder of a number
// 5. find the ascii value of a character

#include<iostream>
using namespace std;

// even/odd
bool eo(int n){
    if(n & 1) return false;
    else return true;
}
// swap
void swap(int a, int b){
    a = a + b;
    b = a - b;
    a = a - b;
    cout<<"a = "<<a<<" and b = "<<b<<endl;
}
// fibonacci series
void fibo(int fib[], int n){
    fib[0] = 1;
    fib[1] = 1;

    if(n == 1 || n == 2){
        cout<<fib[0]<<" "<<fib[1]<<" ";
    }else{
        cout<<fib[0]<<" "<<fib[1]<<" ";
        for(int i = 2; i < n; i++){
            fib[i] = fib[i - 1] + fib[i - 2];
            cout<<fib[i]<<" ";
        }
    }
    cout<<endl;
}
// Quotient and Remainder
void qo_rem(int a, int b){
    cout<<"Quotient: "<<a / b<<endl;
    cout<<"Remainder: "<<a % b<<endl;
}
// ascii value
void ascii(char z){
    cout<<"ASCII value of "<<z<<" is "<<(int)z<<endl;
}

int main(){

    // eo call
    cout<<"Even/Odd: "<<endl;
    int n;
    cout<<"Enter a number: ";
    cin>>n;
    if(eo(n)){
        cout<<"Even number"<<endl;
    }else{
        cout<<"Odd number"<<endl;
    }

    // swap call
    cout<<"Swap: "<<endl;
    int a, b;
    cout<<"Enter a = ";
    cin>>a;
    cout<<"Enter b = ";
    cin>>b;

    swap(a, b);

    // fibo call
    cout<<"Fibonacci: "<<endl;
    int f;
    cout<<"Enter the number till you need the fibonacci series: ";
    cin>>f;
    int fib[f];
    fibo(fib, f);

    // quo_rem call
    cout<<"Quotient and Remainder(x wrt y): "<<endl;
    int x, y;
    cout<<"Enter x: ";
    cin>>x;    
    cout<<"Enter y: ";
    cin>>y;
    qo_rem(x, y);

    // ascii call
    cout<<"ASCII: "<<endl;
    char z;
    cout<<"Enter a character: ";
    cin>>z;
    ascii(z);
}