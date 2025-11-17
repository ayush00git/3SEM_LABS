// To demonstrate example of friend function with class and to concatenate 
// two strings using operators.
// Write a program to demonstrate the single inheritance, multilevel inheritance, multiple inheritances, hybrid inheritance and 
// hierarchical inheritance.

#include<iostream>
#include<string>
using namespace std;

class Names {
    private:
    string str;

    public:
    Names(string s = "") : str(s) {}

    friend Names operator+ (const Names& n1, const Names& n2);

    void display() {
        cout<<str<<endl;
    }

};

Names operator+ (const Names& n, const Names& m) {
    return Names(n.str + m.str);
}

class Parent {
    public:
    void display() {
        cout<<"Parent class"<<endl;
    }
};

class GrandParent { 
    public:
    void display() {
        cout<<"Grandparent class"<<endl;
    }
};

class Child : public Parent {
    public:
    void display() {
        cout<<"Child class"<<endl;
    }
};

class Kid : public Child { 
    public:
    void display() {
        cout<<"Kid class"<<endl;
    }
};

class Neighbour : public Parent, public GrandParent {
    public:
    void display() {
        cout<<"Neighbour class"<<endl;
    }
};

class Kid2 : public Parent {
    public:
    void display() {
        cout<<"Kid 2 class"<<endl;
    }
};

class Hey : public Child, public Kid2 {
    public:
    void display() {
        cout<<"Hey class"<<endl;
    }
};

int main() {
    Names n1("Hey");
    Names n2(" Buddy!");
    Names n;

    n = n1 + n2;
    n.display();

}