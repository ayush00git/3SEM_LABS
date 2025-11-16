// function template to perform linear search in an array

#include<iostream>
using namespace std;

template<typename T>
int linear_search(T a[], int n, T x) {
    for(int i = 0; i < n; i++) {
        if(a[i] == x) {
            return i;
        }
    }
    return -1;
}

int main() {

    int a[] = {1, 5, 8, 3, 7, 4, 2};
    float b[] = {2.4, 3.4, 2.3, 4.9, 2.2, 4.4, 2.1};
    char c[] = {'z', 'z', 'x'};
    cout<<linear_search(a, 7, 4)<<endl;
    cout<<linear_search(b, 7, 2.3f)<<endl;

    try {
        int x = 10;
        int y = 0;
        
        if(y == 0) {
            throw "can't divide by zero";
        }
        cout<<"Result: "<<x / y<<endl; 
    }
    catch(const char* msg) {
        cout<<"Error: "<<msg<<endl;
    }
}