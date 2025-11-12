#include<bits/stdc++.h>
using namespace std;

class Stack {
    int arr[100];
    int top;
    int capacity;

    public:

    Stack(int size) {
        capacity = size;
        top = -1;
    }

    void push(int x){
        if(top == capacity - 1){
            cout<<"Stack overflow"<<endl;
        }else{
            arr[++top] = x;
        }
    }

    void pop(int x){
        if(top == -1){
            cout<<"Stack Underflow"<<endl;
        }else{
            top--;
        }
    }

    int peek(){
        if(top == -1){
            cout<<"Stack is empty"<<endl;
            return -1;
        }else{
            return arr[top];
        }
    }

    void display() {
        if (top == -1) {
            cout << "Stack is Empty\n";
            return;
        }else{
            cout<<"Stack elements: "<<endl;
            for (int i = 0; i <= top; i++) {
                cout << arr[i] << "\t";
            }
            cout << endl;
        }
    }
};  


int main() {

    Stack s1(4);
    s1.push(2);
    s1.push(2);
    s1.push(2);
    s1.pop(2);
    int top = s1.peek();
    cout<<"Top element is: "<<top<<endl;

    s1.display();
}