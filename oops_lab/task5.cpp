// Dynamic memory allocation using double pointer in a 2D array.

#include<iostream>
using namespace std;

void db_ptr(int rows, int cols){
    
    int** dynamicArray = new int*[rows];

    for(int i = 0; i < rows; ++i){
        dynamicArray[i] = new int[cols];
    }

    for(int i = 0; i < rows; ++i){
        for(int j = 0; j < cols; ++j){
            cout<<i+1<<", "<<j+1<<" position: ";
            cin>>dynamicArray[i][j];
        }
    }
    // priting the 2d array
    for(int i = 0; i < rows; ++i){
        for(int j = 0; j < cols; ++j){
            cout << *(*(dynamicArray + i) + j) << "\t";  
        }
        cout << endl;
    }

    // deallocation
    for(int i = 0; i < rows; ++i){
        delete[] dynamicArray[i];
    }
    delete[] dynamicArray;
}

int main() {

    int rows, cols;

    cout<<"Enter the number of rows: ";
    cin>>rows;

    cout<<"Enter the number of columns: ";
    cin>>cols;

    db_ptr(rows, cols);
}