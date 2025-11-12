#include<bits/stdc++.h>
using namespace std;

struct Node {
    Node* next;
    int data;
};

class Stack {

    Node* top;

    public:
    Stack() {
        top = NULL;
    }

    void push(int x){
        Node* newNode = new Node();
        newNode->data = x;
        newNode->next = top;
        top = newNode;
    }

    void pop() {
        if (top == NULL) {
            cout << "Stack Underflow\n";
            return;
        }
        Node* temp = top;   
        top = top->next;    
        delete temp;
    }

    int peek() {
        if (top == NULL) {
            cout << "Stack is Empty\n";
            return -1;
        }
        return top->data;
    }

    void display() {
        if (top == NULL) {
            cout << "Stack is Empty\n";
            return;
        }
        Node* temp = top;
        cout << "Stack elements: ";
        while (temp != NULL) {
            cout << temp->data << " ";
            temp = temp->next;
        }
        cout << endl;
    }
};


int main() {
    Stack st;

    int op;
    cout<<"Enter the operation:\n"<<"1. Push an element\n"<<"2. Pop\n"<<"3. Peek\n"<<"4. Display\n"<<"5. Exit\n";
    cin>>op;
    
    do{
        switch (op)
        {
        case 1:
            int n;
            cout<<"Enter an element: ";
            cin>>n;
            st.push(n);
            break;
    
        case 2:
            st.pop();
            break;
    
        case 3:
            int top = st.peek();
            cout<<"Top element: "<<top<<endl;
            break;
    
        case 4:
            st.display();
            break;
        
        case5:
            exit;
    
        default:
            cout<<"Invalid input"<<endl;
            break;
        }
    }while(op != 5);

}