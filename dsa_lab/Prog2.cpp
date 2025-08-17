#include<bits/stdc++.h>
using namespace std;

void bubble_sort(int* arr, int n) {
    bool FLAG = 0;
    for(int i = 0; i < n - 1; i++) {
        for(int j = 0; j < n - i - 1; j++) {
            if(arr[j] > arr[j+1]) {
                swap(arr[j], arr[j+1]);
                FLAG = 1;
            }
        }
        if(FLAG == 0){
            return;
        }
    }
}
int main() {
    int n;
    cout << "Enter size of array: ";
    cin >> n;

    int* arr = (int*)malloc(n * sizeof(int));
    if(arr == NULL) {
        cout << "Memory allocation failed\n";
        return 1;
    }
    cout << "Enter " << n << " elements:\n";
    for(int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    bubble_sort(arr, n);
    cout << "Sorted array:\n";
    for(int i = 0; i < n; i++) {
        cout << arr[i] << "\t";
    }
    cout << endl;
    free(arr);
}
