#include <stdio.h>
#include <time.h>
#include <stdlib.h>

void sumN(int arr[], int n) {
    int runningSum = 0;
    for(int i = 0; i < n; i++) {
        runningSum += arr[i];
        float average = (float)runningSum / (i + 1);
        // printf("%.2f\t", average);
    }
    printf("\n");
}

void formation(int arr[], int n) {
    srand(time(NULL));
    int min = 1, max = 20;

    for(int i = 0; i < n; i++) {
        arr[i] = (rand() % (max - min + 1)) + min;
    }
}

int main() {
    int n;
    printf("Enter the size of the array: ");
    scanf("%d", &n);

    int arr[n];
    formation(arr, n);

    // Time measurement starts here
    clock_t start_time = clock();

    sumN(arr, n); 

    // Time measurement ends here
    clock_t end_time = clock();
    double cpu_time_used = ((double)(end_time - start_time)) / CLOCKS_PER_SEC * 1000;
    
    printf("Execution time: %f milli seconds\n", cpu_time_used);

    return 0;
}
