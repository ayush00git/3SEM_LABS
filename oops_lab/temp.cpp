// implement these in a single program
// 1. tell even or odd using bitwise operator
// 2. swap 2 numbers wo using the third variable
// 3. print the fibonacci series
// 4. fond the quotient and remainder of a number
// 5. find the ascii value of a character


#include<bits/stdc++.h>
using namespace std;

void even_odd(int n) {
    if(n & 1) cout<<"odd"<<endl;
    else cout<<"Even";
}

pair<int, int> swap(int a, int b) {
    a = a + b;
    b = a - b;
    a = a - b;

    return {a, b};
}

void fibonacci(int n) {
    int a[n];
    a[0] = 0;
    a[1] = 1;

    if(n == 1) cout<<"1"<<endl;
    else if(n == 0) cout<<"0"<<endl;
    else if(n < 0) cout<<"Error";

    if(n > 1) {
        cout<<a[0]<<"\t"<<a[1]<<"\t";
        for(int i = 2; i < n; i++) {
            a[i] = a[i - 1] + a[i - 2];
            cout<<a[i]<<"\t";
        }
    }
}

void prime_range(int a, int b) {

    for(int i = a; i < b; i++) {
        bool isPrime = true;

        if(i == 0 || i == 1) {
            isPrime = false;
        }

        for(int j = 2; j < sqrt(i); j++) {
            if(i % j == 0) {
                isPrime = false;
            }
        }
        if(isPrime) cout<<i<<'\t';
    }
}

bool palindrome(int n) {
    int rev = 0;
    int og = n;

    while(n != 0) {
        rev = rev * 10 + n % 10;
        n /= 10;
    }

    if(og == rev) return 1;
    else return 0;
}

int max_ele(int a[], int n) {
    int max = a[0];
    for(int i = 1; i < n; i++) {
        if(max < a[i]) {
            max = a[i];
        }
    }
    return max;
}

// Display the maximum marks in 3 different classes with 3, 5, 7 students in each class, 
// make a 2D array (with dynamic memory allocation).

void marks() {
    int student[3] = {3, 5, 7};

    int** classes = new int*[3];

    classes[0] = new int[3];
    classes[1] = new int[5];
    classes[2] = new int[7];

    for(int i = 0; i < 3; i++) {
        for(int j = 0; j < student[i]; j++) {
            cout<<"Enter stud "<<(j + 1)<<": ";
            cin>>*(*(classes + i) + j);
        }
    }

    int maxM = classes[0][0];
    for(int i = 0; i < 3; i++) {
        for(int j = 0; j < student[i]; j++) {
            if(maxM < classes[i][j]) {
                maxM = classes[i][j];
            }
        }
    }
    cout<<"Maximum marks: "<<maxM<<endl;

    for(int i = 0; i < 3; i++){
        delete[] classes[i];
    }
    delete[] classes;
}   

class Student {

    public:
    string name;
    int marks;

    Student(string name = " ", int marks = 0) {
        this->name = name;
        this->marks = marks;
    }

    void read() {
        cout<<"Enter a name: ";
        cin>>name;

        cout<<"Enter the marks: ";
        cin>>marks;
    }

    void display() {
        cout<<"Name: "<<name<<" Marks: "<<marks<<endl;
    }

    Student operator+ (const Student& b) {
        Student temp;
        temp.name = name + " " + b.name;
        temp.marks = marks + b.marks;
        return temp;
    }
};

int main() {
    even_odd(4);
    cout<<endl;

    pair<int, int> g = swap(5, 1);
    cout<<"First: "<<g.first<<" and Second: "<<g.second<<endl;

    fibonacci(7);
    cout<<endl;

    prime_range(3, 17); // 5 7 9 11 13 
    cout<<endl;

    if(palindrome(2112)) {
        cout<<"It's palindrome\n";
    }else{
        cout<<"Not palindrome\n";
    }

    int a[] = {1, 5, 2, 344, 19, 12};
    int el = max_ele(a, 6);
    cout<<el<<endl;

    // marks();

    Student b;
    b.read();

    Student c;
    c.read();

    Student d = b + c;
    d.display();
    
}