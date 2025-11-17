// Write a C++ program to overload the binary '+' operator to add two objects of 
// a class Distance, where each object stores meters and centimeters.

#include<iostream>
using namespace std;

class Distance {
    public:
    int unit;

    Distance(int unit = 0) {
        this->unit = unit;
    }

    void display() {
        cout<<unit<<endl;
    }

    Distance operator+ (const Distance& a) {
        Distance temp;
        temp.unit = unit + a.unit;
        return temp;
    }
    
};

class Counter {
    public:
    int cntr = 0;

    Counter operator++ () {
        ++cntr;
        return *this;
    }

};

class Complex {
    public:
    int real;
    int imag;

    Complex(int real = 0, int imag = 0) {
        this->real = real;
        this->imag = imag; 
    }

    void display() {
        cout<<real<<" + i"<<imag<<endl;
    }

    Complex operator- (const Complex& a) {
        Complex temp;
        temp.real = a.real - real;
        temp.imag = a.imag - imag;
        return temp;
    }

};

// To demonstrate example of friend function with class and to concatenate 
// two strings using operators.

class Name {
    public:
    string str;

    Name(string s) {
        str = s;
    }

    void display() {
        cout<<str<<endl;
    }

    friend Name operator+ (const Name& a, const Name& b);
};

Name operator+ (const Name& a, const Name& b) {
    return Name(a.str + " " + b.str);
}

int main() {

    Name a("Ayush");
    Name b("Kumar");
    Name c = a + b;
    c.display();
    
}