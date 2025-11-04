// average of numbers stored in an array
// largest element in an array
// addition matrix using array

#include<iostream>
using namespace std;

// average of array elements
float avg(int a[], int n){
    int sum = 0;
    for(int i = 0; i < n; i++) {
        sum += a[i];
    }
    float av = float(sum) / n;
    return av;
}
// largest element in the array
int largest(int a[], int n, int* max) {
    if(n == 1) {
        *max = a[0];
        return *max;
    }
    largest(a, n - 1, max);

    if(*max < a[n - 1]){
        *max = a[n - 1];
    }
    return *max;
}

// creating a dynamic 2D array
void twoD_arr(int rows, int columns) {
    // initializing a row pointer arrar
    int** dynArr = new int* [rows];

    // creating column arrays
    for(int i = 0; i < rows; i++) {
        dynArr[i] = new int[columns];
    }

    // taking input into the dynamic array
    for(int i = 0; i < rows; i++) {
        for(int j = 0; j < columns; j++) {
            cout<<"Enter the "<<(i + 1)<<", "<<(j + 1)<<" element: ";
            cin>>dynArr[i][j];
        }
    }

    // printing it back
    for(int i = 0; i < rows; i++) {
        for(int j = 0; j < columns; j++) {
            cout<<dynArr[i][j]<<"\t";
        }
        cout<<endl;
    }
    // deallocation
    for(int i = 0; i < rows; i++){
        delete[] dynArr[i];
    }
    delete[] dynArr;
} 

// Display the maximum marks in 3 different classes with 3, 5, 7 students in each class, 
// make a 2D array (with dynamic memory allocation).

void maximum(int classes){
    int** dynArr = new int* [classes];

    dynArr[0] = new int[3];
    dynArr[1] = new int[5];
    dynArr[2] = new int[7];

    int size[] = {3, 5, 7};

    for(int i = 0; i < classes; i++) {
        for(int j = 0; j < size[i]; j++) {
            cout<<"Enter the "<<(i + 1)<<", "<<(j + 1)<<" element: ";
            cin>>dynArr[i][j];
        }
    }
    int max = dynArr[0][0];
    for(int i = 0; i < classes; i++) {
        for(int j = 0; j < size[i]; j++) {
            if(max < dynArr[i][j]){
                max = dynArr[i][j];
            }
        }
    }

    // printing the array
    for(int i = 0; i < classes; i++ ) {
        for(int k = 0; k < size[i]; k++) {
            cout<< *(*(dynArr + i) + k)<<"\t";
        }
        cout<<endl;
    }
    cout<<max<<endl;
}

void swap(int* a, int* b) {
    int t = *a;
    *a = *b;
    *b = t;
}
// array of pointers
void arrPtr(int n) {
    int** dynArr = new int*[n];

    for(int i = 0; i < n; i++){
        cout<< *(dynArr + i) << endl;
    }

    delete[] dynArr;
}

// Write a function in C++ that accepts a pointer as an argument and prints the elements of an array
void print(int* n) {
    int* dynArr = new int[*n];
    for(int i = 0; i < *n; i++) {
        cout<<"Enter the element: ";
        cin>>dynArr[i];
    }

    for(int i = 0; i < *n; i++) {
        cout<<*(dynArr + i)<<"\t";
    }
    cout<<endl;
    // cout<<dynArr[0]<<endl;
}



int main() {

    int x;
    cout<<"Enter x: ";
    cin>>x;
    print(&x);

    // arrPtr(3);
    // int rows;
    // int columns;

    // cout<<"Enter the number of rows: ";
    // cin>>rows;
    // cout<<"Enter the number of columns: ";
    // cin>>columns;

    // twoD_arr(rows, columns);
    // int x, y;
    // cout<<"Enter x: ";
    // cin>>x;
    // cout<<"Enter y: ";
    // cin>>y;
    // swap(&x, &y);
    // cout<<"x: "<<x<<" and"<<" y: "<<y<<endl;
    // maximum(3);

    // addition matrix

    // int x, y;
    // cout<<"Enter the number of rows: ";
    // cin>>x;
    // cout<<"Enter the number of columns: ";
    // cin>>y;

    // int b[x][y], c[x][y], result[x][y];
    
    // cout<<endl<<"Enter the elements in array B: "<<endl;
    // // inputing the elements in b
    // for(int i = 0; i < x; i++) {
    //     for(int j = 0; j < y; j++) {
    //         cout<<"Enter the "<<(i + 1)<<", "<<(j + 1)<<" elemnt: ";
    //         cin>>b[i][j]; 
    //     }
    // }

    // cout<<endl<<"Enter the elements in array C: "<<endl;
    // // inputing the elements in c
    // for(int i = 0; i < x; i++) {
    //     for(int j = 0; j < y; j++) {
    //         cout<<"Enter the "<<(i + 1)<<", "<<(j + 1)<<" elemnt: ";
    //         cin>>c[i][j]; 
    //     }
    // }

    // // calculation of sum
    // for(int i = 0; i < x; i++) {
    //     for(int j = 0; j < y; j++) {
    //         result[i][j] = c[i][j] + b[i][j];
    //     }
    // }

    // // printing the sum
    // for(int i = 0; i < x; i++) {
    //     for(int j = 0; j < y; j++) {
    //         cout<<result[i][j]<<"\t";
    //     }
    //     cout<<endl;
    // }

}