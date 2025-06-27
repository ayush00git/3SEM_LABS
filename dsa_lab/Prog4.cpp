#include <bits/stdc++.h>
using namespace std;

class Student {
public:
    string name;
    int rollNo;
    float gpa;

    Student() {}  

    Student(int rN, string n, float m) {
        rollNo = rN;
        name = n;
        gpa = m;
    }

    void display() {
        cout<<"Name: "<<name<<"\nRoll number: "<<rollNo<<"\ngpa: "<<gpa<<endl;
    }
};

struct Node {
    Student data;   
    Node* next;
};

Node* head = NULL;
Node* tail = NULL;  

void insertAtBegin(Student s) {
    Node* newNode = new Node();
    newNode->data = s;
    newNode->next = head;
    head = newNode;

    if (tail == NULL) 
        tail = newNode;
}

void insertAtEnd(Student s) {
    Node* newNode = new Node();
    newNode->data = s;
    newNode->next = NULL;

    if (head == NULL) {
        head = tail = newNode;
    } else {
        tail->next = newNode;
        tail = newNode;
    }
}

void insertAtPos(Student s, int pos) {
    Node* newNode = new Node();
    newNode->data = s;

    if (pos == 1) {
        newNode->next = head;
        head = newNode;
        if (tail == NULL) {
            tail = newNode;
        }
        return;
    }

    Node* temp = head;
    for (int i = 1; temp != NULL && i < pos - 1; i++){
        temp = temp->next;
    }

    if (temp == NULL) {
        cout << "Out of range"<<endl;
        delete newNode;
        return;
    }

    newNode->next = temp->next;
    temp->next = newNode;

    if (temp == tail) {
        tail = newNode;
    }
}

void deleteAtBegin() {
    if (head == NULL) {
        cout << "List is empty"<<endl;
        return;
    }
    Node* temp = head;
    head = head->next;
    if (head == NULL) tail = NULL; 
    delete temp;
}

void deleteAtEnd() {
    if (head == NULL) {
        cout << "List is empty"<<endl;
        return;
    }
    if (head->next == NULL) {
        delete head;
        head = tail = NULL;
        return;
    }
    Node* temp = head;
    while (temp->next != tail) 
        temp = temp->next;
    delete tail;
    tail = temp;
    tail->next = NULL;
}

void deleteAtPos(int pos) {
    if (head == NULL) {
        cout << "List is empty"<<endl;
        return;
    }

    if (pos == 1) {
        Node* temp = head;
        head = head->next;
        if (head == NULL) tail = NULL;
        delete temp;
        return;
    }

    Node* temp = head;
    for (int i = 1; temp != NULL && i < pos - 1; i++)
        temp = temp->next;

    if (temp == NULL || temp->next == NULL) {
        cout << "Position out of range\n";
        return;
    }

    Node* del = temp->next;
    temp->next = del->next;

    if (del == tail) 
        tail = temp;

    delete del;
}

void display() {
    if (head == NULL) {
        cout << "List is empty"<<endl;
        return;
    }
    Node* temp = head;
    while (temp != NULL) {
        temp->data.display();
        cout << " -> ";
        temp = temp->next;
    }
    cout << "NULL\n";
}

int main() {
    int choice, rollNo, pos;
    string name;
    float gpa;

    do {
        cout<<"Enter(1 to 8): "<<endl;
        cout << "1. Insert at Beginning"<<endl;
        cout << "2. Insert at End"<<endl;
        cout << "3. Insert at Position"<<endl;
        cout << "4. Delete at Beginning"<<endl;
        cout << "5. Delete at End"<<endl;
        cout << "6. Delete at Position"<<endl;
        cout << "7. Display"<<endl;
        cout << "8. Exit"<<endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "Enter Roll No, Name, gpa: ";
                cin >> rollNo >> name >> gpa;
                insertAtBegin(Student(rollNo, name, gpa));
                break;
            case 2:
                cout << "Enter Roll No, Name, gpa: ";
                cin >> rollNo >> name >> gpa;
                insertAtEnd(Student(rollNo, name, gpa));
                break;
            case 3:
                cout << "Enter Roll No, Name, gpa and Position: ";
                cin >> rollNo >> name >> gpa >> pos;
                insertAtPos(Student(rollNo, name, gpa), pos);
                break;
            case 4:
                deleteAtBegin();
                break;
            case 5:
                deleteAtEnd();
                break;
            case 6:
                cout << "Enter position: ";
                cin >> pos;
                deleteAtPos(pos);
                break;
            case 7:
                display();
                break;
            case 8:
                cout << "Exiting..."<<endl;
                break;
            default:
                cout << "Invalid choice!"<<endl;
        }
    } while (choice != 8);

    return 0;
}