#include<iostream>
using namespace std;

class Queue {
    private:
    int *a;
    int front, rear, capacity;

    public:
    Queue(int size) {
        capacity = size;
        a = new int[capacity];
        front = -1;
        rear = -1;
    }

    ~Queue() { 
        delete[] a;
    }
    void enqueue(int n) {
        if(rear == capacity - 1){
            cout<<"Stack overflow"<<endl;
            return;
        }
        if(front == -1){
            front = 0;
        }
        cout<<n<<" enqueued"<<endl;
        a[++rear] = n;
    }

    void dequeue() {
        if(front == -1 || front > rear){
            cout<<"Stack underflow"<<endl;
            return;
        }
        cout<<a[front]<<" dequeued"<<endl;
        front++;
    }

    int peek() {
        if(front == -1 || front > rear){
            cout<<"Stack is empty"<<endl;
        }
        return a[front];
    }

    void display() {
        if(front == -1 || front > rear){
            cout<<"Stack is empty"<<endl;
            return;
        }
        for(int i = front; i <= rear; i++){
            cout<<a[i]<<'\t';
        }
        cout<<endl;
    }
};

int main() {
    Queue q1(5);
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
    
    cout<<endl;
}