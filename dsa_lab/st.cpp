// stacks using arrays

#include<bits/stdc++.h>
using namespace std;

class stUsingArr {
    public:
    int top = -1, st[10];

    void push(int x){
        if(top == 10){
            cout<<"Stack overflow"<<endl;
        }
        top++;
        st[top] = x;
    }

    int pop(){
        if(top == -1){
            cout<<"Stack Underflow"<<endl;
            return -1;
        }
        top--;
        return st[top+1];
    }

    int peek(){
        if(top == -1){
            return -1;
        }
        return st[top];
    }

    int size() {
        return top + 1;
    }
};

int main() {

    stUsingArr st1;
    st1.push(2);
    st1.push(7);
    st1.push(17);
    int t = st1.pop();
    cout<<"top element was: "<<t<<endl;
    cout<<"top: "<<st1.peek()<<endl;
    st1.push(71);
    cout<<"top: "<<st1.peek()<<endl;
    cout<<"Size: "<<st1.size()<<endl;
    cout<<st1.pop()<<endl;
    cout<<"size: "<<st1.size()<<endl;
}