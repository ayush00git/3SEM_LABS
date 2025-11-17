#include<iostream>
#include<string.h>
using namespace std;

class Student {
    string name;
    float gpa;
    string rollNum;

    public:
    Student(string name1 = "", float gpa1 = 0.0, string rollNum1 = ""){
        name = name1;
        gpa = gpa1;
        rollNum = rollNum1;
    }
    void read() {
        cout<<"Enter your name: ";
        cin>>name;

        cout<<"Enter your gpa: ";
        cin>>gpa;

        cout<<"Enter you roll number: ";
        cin>>rollNum;
    }

    void display(){
        cout<<"Name: "<<name<<"\nGPA: "<<gpa<<"\nRoll Number: "<<rollNum<<endl;
    }

    Student operator+ (const Student& s) {
        Student temp;
        temp.name = name + " " + s.name;
        temp.gpa = gpa + s.gpa;
        temp.rollNum = rollNum + " " + s.rollNum;
        return temp;
    }

};

class Complex {
    int real, imag;

    public:
    Complex(int r = 0, int i = 0) : real(r), imag(i) {}

    Complex operator- (const Complex& c) {
        return Complex(c.real - real, c.imag - imag);
    }

    void display() {
        cout<<real<<" + "<<imag<<"i"<<endl;
    }
};

int main() {

    Student s1;
    Student s2;

    s1.read();
    s2.read();
    // s1.display();

    Student s3 = s1 + s2;
    s3.display();

    cout<<endl<<"Complex number subtraction"<<endl;

    Complex c1(7, 4);
    Complex c2(4, 2);

    Complex result = c2 - c1;
    cout<<"result: ";
    result.display();
    
}