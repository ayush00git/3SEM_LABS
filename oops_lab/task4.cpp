// average of numbers stored in an array
// largest element in an array
// addition matrix using array

#include<iostream>
using namespace std;

float average(int a[], int n){
    int sum = 0;
    for(int i = 0; i < n; i++){
        sum += a[i];
    }
    float avg = (float)sum / n;
    return avg;
}

int maxi(int a[], int n){
    int max = a[0];
    for(int i = 1; i < n; i++){
        if(a[i] > max){
            max = a[i];
        }
    }
    return max;
}

void addition(int a[][3], int b[][3], int n, int m) {
    int sum[3][3];
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {
            sum[i][j] = a[i][j] + b[i][j];
            cout << sum[i][j] << " ";
        }
        cout << endl;
    }
}
int main() {

    int n;
    cout<<"Enter the size of the array: ";
    cin>>n;

    int a[n];
    for(int i = 0; i < n; i++){
        cout<<(i+1)<<" index: ";
        cin>>a[i];
    }
    
    float av = average(a, n);
    int largest = maxi(a, n);

    cout<<"The avergae of numbers in the array is: "<<(av)<<endl;
    cout<<"The maximum number in the array is: "<<largest<<endl;

    cout<<"The sum of the arrays is: "<<endl;
    int a2[3][3] = {{1, 2, 4}, {2, 3, 4}, {5, 6, 7}};
    int b2[3][3] = {{1, 2, 4}, {2, 3, 4}, {5, 6, 7}};
    addition(a2, b2, 3, 3);
}