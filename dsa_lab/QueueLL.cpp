#include<iostream>
using namespace std;

class Node {
    public:
    int data;
    Node* next;

    public:
    Node(int data1, Node* next1){
        data = data1;
        next = next1;
    }

    Node(int data1){
        data = data1;
        next = nullptr;
    }
};

class Queue {
    private:
    Node* front;
    Node* rear;

    public:
    Queue() {
        front = rear = nullptr;
    }
    void enqueue(int x) {
        Node* newNode = new Node(x);
        if(rear == nullptr){
            front = rear = newNode;
            return;
        }
        rear->next = newNode;
        rear = newNode;
    }

    int dequeue() {
        if(front == nullptr){
            cout<<"Queue is empty"<<endl;
            return -1;
        }
        Node* temp = front;
        int removedData = temp->data;
        front = front->next;
        if(front == nullptr){
            rear = nullptr;
        }

        delete temp;
        return removedData;
    }

    int peek() {
        if(front == nullptr){
            cout<<"Queue is empty";
            return -1;
        }
        return front->data;
    }
    void display() {
        if (front == nullptr) {
            cout << "Queue is empty!\n";
            return;
        }
        Node* temp = front;
        while (temp != nullptr) {
            cout<<temp->data<<"\t";
            temp = temp->next;
        }
        cout<<endl;
    }
};

int main() {

    Queue q1;
    char z;


    do{
        cout<<"#######"<<endl;
        cout<<"Input the commands- \n1. Enqueue(e)\n2. Dequeue(d)\n3. Peek(p)\n4. Display(D)\n5. Exit(x): \n";
        cout<<"#######"<<endl;
        cout<<"Your command: ";
        cin>>z;
        switch(z) {
            case 'e':
            int n;
            cout<<"Enter the element you wanna add to the queue: ";
            cin>>n;
            q1.enqueue(n);
            break;

            case 'd':
            q1.dequeue();
            break;

            case 'p':
            cout<<"Element at the top is: "<<q1.peek()<<endl;
            break;

            case 'D':
            q1.display();
            break;

            default:
            cout<<"Invalid operation\n";
            exit(1);
        }
    }while(z != 'x');


    // q1.enqueue(2);
    // q1.enqueue(12);
    // q1.enqueue(22);
    // q1.enqueue(42);
    // q1.enqueue(23);
    // cout<<q1.peek()<<endl;

}