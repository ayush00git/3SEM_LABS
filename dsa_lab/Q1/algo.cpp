#include <stdio.h>
#include <time.h>
#include <stdlib.h>

long long operations_n = 0;
long long operations_n2 = 0;

// O(n) algorithm 
void sumN_On(int arr[], int n) {
    operations_n = 0;
    int runningSum = 0;
    
    for(int i = 0; i < n; i++) {
        runningSum += arr[i];
        operations_n++; 
        
        float average = (float)runningSum / (i + 1);
        operations_n++; 
    }
}

// O(n^2) algorithm 
void sumN_On2(int arr[], int n) {
    operations_n2 = 0;
    
    for(int i = 0; i < n; i++) {
        int sum = 0;
        
        for(int j = 0; j <= i; j++) {
            sum += arr[j];
            operations_n2++;
        }
        
        float average = (float)sum / (i + 1);
        operations_n2++; // Division operation
    }
}

void formation(int arr[], int n) {
    srand(time(NULL));
    int min = 1, max = 20;

    for(int i = 0; i < n; i++) {
        arr[i] = (rand() % (max - min + 1)) + min;
    }
}

void writeCSVHeader(const char* filename) {
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        printf("Error creating file!\n");
        return;
    }
    
    fprintf(file, "inputs,time(n),time(n^2)\n");
    fclose(file);
}

void appendToCSV(const char* filename, int n, double time_n, double time_n2) {
    FILE *file = fopen(filename, "a");
    if (file == NULL) {
        printf("Error opening file!\n");
        return;
    }
    
    fprintf(file, "%d,%.6f,%.6f\n", n, time_n, time_n2);
    fclose(file);
}

double measureTime_On(int arr[], int n) {
    clock_t start_time = clock();
    sumN_On(arr, n);
    clock_t end_time = clock();
    return ((double)(end_time - start_time)) / CLOCKS_PER_SEC * 1000;
}

double measureTime_On2(int arr[], int n) {
    clock_t start_time = clock();
    sumN_On2(arr, n);
    clock_t end_time = clock();
    return ((double)(end_time - start_time)) / CLOCKS_PER_SEC * 1000;
}

int main() {
    // Define test sizes
    int test_sizes[] = {10000, 20000, 30000, 40000, 50000};
    int num_tests = sizeof(test_sizes) / sizeof(test_sizes[0]);
    
    const char* filename = "output.csv";
    
    printf("Starting performance comparison for O(n) vs O(n^2) algorithms...\n");
    printf("Testing with array sizes: ");
    for(int i = 0; i < num_tests; i++) {
        printf("%d ", test_sizes[i]);
    }
    printf("\n\n");
    
    
    writeCSVHeader(filename);
    
    // Test each array size
    for(int i = 0; i < num_tests; i++) {
        int n = test_sizes[i];
        printf("Testing with array size: %d\n", n);
        
        // Create array and populate with random numbers
        int *arr = (int*)malloc(n * sizeof(int));
        formation(arr, n);
        
        // Measure O(n) algorithm
        printf("  Running O(n) algorithm...");
        fflush(stdout);
        double time_n = measureTime_On(arr, n);
        printf(" %.6f ms\n", time_n);
        
        // Measure O(n^2) algorithm
        printf("  Running O(n^2) algorithm...");
        fflush(stdout);
        double time_n2 = measureTime_On2(arr, n);
        printf(" %.6f ms\n", time_n2);
        
        // Write results to CSV
        appendToCSV(filename, n, time_n, time_n2);
        
        printf("  Ratio (n^2/n): %.2fx\n\n", (time_n > 0) ? time_n2/time_n : 0);
        
        free(arr);
    }
    
    printf("Performance comparison completed!\n");
    printf("Results saved to: %s\n\n", filename);
    
    // Display summary
    printf("CSV Format:\n");
    printf("inputs,time(n),time(n^2)\n");
    printf("1000,x.xxxxxx,y.yyyyyy\n");
    printf("2000,x.xxxxxx,y.yyyyyy\n");
    printf("...\n");
    
    return 0;
}