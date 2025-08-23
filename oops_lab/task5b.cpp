// Display the maximum marks in 3 different classes with 3, 5, 7 students in each class, 
// make a 2D array (with dynamic memory allocation).

#include<iostream>
using namespace std;

int main() {

    int** classes = new int*[3];

    classes[0] = new int[3];
    classes[1] = new int[5];
    classes[2] = new int[7];

    int sizes[3] = {3, 5, 7};
    
    // input
    for(int i = 0; i < 3; ++i){
        cout << "Enter marks for class " << i+1 << " (" << sizes[i] << " students):\n";
        for(int j = 0; j < sizes[i]; ++j){
            cout << "Student " << j+1 << ": ";
            cin >> classes[i][j];
        }
    }
    // max marks in the 2D array
    int maxMarks = classes[0][0];
    for(int i = 0; i < 3; ++i){
        for(int j = 0; j < sizes[i]; ++j){
            if(classes[i][j] > maxMarks){
                maxMarks = classes[i][j];
            }
        }
    }

    cout << "Max marks in the whole 2D array = " << maxMarks << endl;

    // deallocation
    for(int i = 0; i < 3; ++i){
        delete[] classes[i];
    }
    delete[] classes;  

}