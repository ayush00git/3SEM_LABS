#include <bits/stdc++.h>
using namespace std;

// Prime in range function declaration and definition
void prime_in_range(int start, int end){
    
    for(int i = start; i < end; i++){
        bool isPrime = true;
        if(i == 1 || i == 0){
            isPrime = false;
        }
        for(int j = 2; j < i; j++){
            if(i % j == 0){
                isPrime = false;
                break;
            }
        }
        if(isPrime){
            cout<<i<<"\t";
        }
    }

}

// Palindrome function declaration and definition
bool palindrome(int n){
    int rev = 0;
    int og = n;
    while(n != 0){
        rev = rev * 10 + n % 10;
        n /= 10;
    }
    if(og == rev) return true;
    else return false;
}

int main() {

    // Prime number
    cout<<"Prime number in a range: "<<endl;
    int a, b;
    cout<<"Enter the starting index: ";
    cin>>a;
    cout<<"Enter the ending index: ";
    cin>>b;

    cout<<"The prime numbers within the range "<<a<<" to "<<b<<" are:"<<endl; 
    // function call
    prime_in_range(a, b);
    cout<<endl;

    // Palindrome number
    cout<<"Palindrome number check: "<<endl;
    int num;
    cout<<"Enter the number you wanna check palindrome: ";
    cin>>num;

    if(palindrome(num)){
        cout<<num<<" is a palindrome number"<<endl;
    }else{
        cout<<num<<" is not a palindrome number"<<endl;
    }
}