#include <iostream>
using namespace std;

// Array-based Queue
class ArrayQueue {
    int *a;
    int front, rear, capacity;
public:
    ArrayQueue(int size) {
        capacity = size;
        a = new int[capacity];
        front = -1;
        rear = -1;
    }
    ~ArrayQueue() { delete[] a; }
    void enqueue(int n) {
        if (rear == capacity - 1) {
            cout << "Queue overflow" << endl;
            return;
        }
        if (front == -1) front = 0;
        cout << n << " enqueued" << endl;
        a[++rear] = n;
    }
    void dequeue() {
        if (front == -1 || front > rear) {
            cout << "Queue underflow" << endl;
            return;
        }
        cout << a[front] << " dequeued" << endl;
        front++;
    }
    int peek() {
        if (front == -1 || front > rear) {
            cout << "Queue is empty" << endl;
            return -1;
        }
        return a[front];
    }
    void display() {
        if (front == -1 || front > rear) {
            cout << "Queue is empty" << endl;
            return;
        }
        for (int i = front; i <= rear; i++) {
            cout << a[i] << '\t';
        }
        cout << endl;
    }
};

// Linked List Node
class Node {
public:
    int data;
    Node* next;
    Node(int data1, Node* next1 = nullptr) {
        data = data1;
        next = next1;
    }
};

// Linked List-based Queue
class LinkedListQueue {
    Node* front;
    Node* rear;
public:
    LinkedListQueue() { front = rear = nullptr; }
    void enqueue(int x) {
        Node* newNode = new Node(x);
        if (rear == nullptr) {
            front = rear = newNode;
            return;
        }
        rear->next = newNode;
        rear = newNode;
    }
    void dequeue() {
        if (front == nullptr) {
            cout << "Queue is empty" << endl;
            return;
        }
        Node* temp = front;
        cout << temp->data << " dequeued" << endl;
        front = front->next;
        if (front == nullptr) rear = nullptr;
        delete temp;
    }
    int peek() {
        if (front == nullptr) {
            cout << "Queue is empty" << endl;
            return -1;
        }
        return front->data;
    }
    void display() {
        if (front == nullptr) {
            cout << "Queue is empty!" << endl;
            return;
        }
        Node* temp = front;
        while (temp != nullptr) {
            cout << temp->data << '\t';
            temp = temp->next;
        }
        cout << endl;
    }
};

int main() {
    cout << "Choose queue implementation: (1) Array (2) Linked List\nEnter 1 or 2: ";
    int choice;
    cin >> choice;
    char z;
    int n;
    if (choice == 1) {
        int size;
        cout << "Enter queue size: ";
        cin >> size;
        ArrayQueue q1(size);
        do {
            cout << "#######" << endl;
            cout << "Input the commands- \n1. Enqueue(e)\n2. Dequeue(d)\n3. Peek(p)\n4. Display(D)\n5. Exit(x): \n";
            cout << "#######" << endl;
            cout << "Your command: ";
            cin >> z;
            switch (z) {
                case 'e':
                    cout << "Enter the element you wanna add to the queue: ";
                    cin >> n;
                    q1.enqueue(n);
                    break;
                case 'd':
                    q1.dequeue();
                    break;
                case 'p':
                    cout << "Element at the top is: " << q1.peek() << endl;
                    break;
                case 'D':
                    q1.display();
                    break;
                default:
                    if (z != 'x') cout << "Invalid operation\n";
            }
        } while (z != 'x');
    } else if (choice == 2) {
        LinkedListQueue q1;
        do {
            cout << "#######" << endl;
            cout << "Input the commands- \n1. Enqueue(e)\n2. Dequeue(d)\n3. Peek(p)\n4. Display(D)\n5. Exit(x): \n";
            cout << "#######" << endl;
            cout << "Your command: ";
            cin >> z;
            switch (z) {
                case 'e':
                    cout << "Enter the element you wanna add to the queue: ";
                    cin >> n;
                    q1.enqueue(n);
                    break;
                case 'd':
                    q1.dequeue();
                    break;
                case 'p':
                    cout << "Element at the top is: " << q1.peek() << endl;
                    break;
                case 'D':
                    q1.display();
                    break;
                default:
                    if (z != 'x') cout << "Invalid operation\n";
            }
        } while (z != 'x');
    } else {
        cout << "Invalid choice!" << endl;
    }
    cout << endl;
}