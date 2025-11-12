#include <iostream>
#include <cstring>
#include <cctype>   
using namespace std;

class Stack {
private:
    int top;
    int capacity;
    int* arr;
public:
    Stack(int size) {
        capacity = size;
        arr = new int[capacity];
        top = -1;
    }
    ~Stack() {
        delete[] arr;
    }

    void push(int value) {
        if (top == capacity - 1) {
            cout << "Stack Overflow\n";
            return;
        }
        arr[++top] = value;
    }

    int pop() {
        if (top == -1) {
            cout << "Stack Underflow\n";
            return -1;
        }
        return arr[top--];
    }
};

int evaluatePostfix(const char* expression) {
    int len = strlen(expression);
    Stack stack(len);

    for (int i = 0; i < len; i++) {
        char ch = expression[i];

        if (ch == ' ') continue;

        if (isdigit(ch)) {
            int num = 0;
            while (i < len && isdigit(expression[i])) {
                num = num * 10 + (expression[i] - '0');
                i++;
            }
            i--;
            stack.push(num);
        }

        else if (ch == '+' || ch == '-' || ch == '*' || ch == '/') {
            int val2 = stack.pop();
            int val1 = stack.pop();

            switch (ch) {
                case '+': stack.push(val1 + val2); break;
                case '-': stack.push(val1 - val2); break;
                case '*': stack.push(val1 * val2); break;
                case '/': stack.push(val1 / val2); break;
            }
        }
    }
    return stack.pop();
}


int main() {
    char expression[100];
    cout << "Enter postfix expression : ";
    cin >> expression;

    cout << "Result = " << evaluatePostfix(expression) << endl;
    return 0;
}
