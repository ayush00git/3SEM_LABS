#include<iostream>
using namespace std;

void db_ptr(int rows, int cols) {

    int** dynamicArr = new int*[rows];

    dynamicArr[0] = new int[cols];
    dynamicArr[1] = new int[cols];
    dynamicArr[2] = new int[cols]; 
    
    for(int i = 0; i < 3; i++) {
        for(int j = 0; j < 3; j++) {
            cout<<"Enter a element "<<(i + 1)<<", "<<(j + 1)<<": ";
            cin>>*(*(dynamicArr + i) + j);
        }
    }

    for(int i = 0; i < 3; i++) {
        for(int j = 0; j < 3; j++) {
            cout<<*(*(dynamicArr + i) + j)<<"\t";
        }
        cout<<endl;
    }
}

int main() {
    db_ptr(3, 3);
}