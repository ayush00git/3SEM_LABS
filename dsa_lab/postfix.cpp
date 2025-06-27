#include <iostream>
using namespace std;

#define MAX 100

class Stack {
    private:
    int a[MAX];
    int top;
    
    public:
    Stack() { 
        top = -1;
    }

    void push(int x) {
        if (top == MAX - 1) {
            cout << "Stack overflow\n";
            return;
        }
        a[++top] = x;
    }

    int pop() {
        if (top == -1) {
            cout << "Stack underflow\n";
            return -1;
        }
        return a[top--];
    }

    int peek() {
        if (top == -1) {
            cout << "Stack is empty\n";
            return -1;
        }
        return a[top];
    }
};

int evaluatePostfix(string exp) {
    Stack st;
    int i = 0;
    while (i < exp.length()) {
        if (exp[i] == ' ') {
            i++;
            continue;
        }
        if (isdigit(exp[i])) {
            int num = 0;
            while (i < exp.length() && isdigit(exp[i])) {
                num = num * 10 + (exp[i] - '0');
                i++;
            }
            st.push(num);
        } else {
            int op2 = st.pop();
            int op1 = st.pop();
            switch (exp[i]) {
                case '+': st.push(op1 + op2); break;
                case '-': st.push(op1 - op2); break;
                case '*': st.push(op1 * op2); break;
                case '/': st.push(op1 / op2); break;
            }
            i++;
        }
    }
    return st.pop();
}

int main() {
    string exp;
    cout<<"Enter the postfix expression: ";
    getline(cin, exp);

    cout<<"Answer: "<< evaluatePostfix(exp)<<endl;

}