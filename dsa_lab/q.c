#include<stdio.h>
#include<time.h>
#include<stdlib.h>

int sumN(int arr[], int index){
    int sum = 0;
    for(int i = 0; i < index; i++){
        sum += arr[i];
        
    }
    return sum;
}

void avg(int arr[], int n){
    // for(float i = 0; i < n; i++){
    //     printf("%f\t", (sumN(arr, i + 1)) / (i + 1));
    // }
}

void formation(int arr[], int n){

    srand(time(NULL));
    int min = 1;
    int max = 20;

    for(int i = 0; i < n; i++){
        int randomNumber = (rand() % (max - min + 1)) + min;
        arr[i] = randomNumber;
        // printf("%d\t", arr[i]);
    }
    
    printf("\n");
}

int main(){

    int n;
    printf("Enter the size of the array: ");
    scanf("%d", &n);
    
    int arr[n];
    formation(arr, n);
    

    // taking input of the array manually
    // for(int i = 0; i < n; i++){
    //     printf("Enter the %dthe index: ", i);
    //     scanf("%d", &arr[i]);
    // }
    // printf("Formated array: \n");

    // for recording time
    clock_t start_time, end_time;
    double cpu_time_used;

    start_time = clock();

    avg(arr, n);
    printf("\n");

    end_time = clock(); // Record the end time

    cpu_time_used = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;
    printf("Execution time: %f seconds\n", cpu_time_used);

}