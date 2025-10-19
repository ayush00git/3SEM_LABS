#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int* avgsq(int*, int*, int);
int* avgli(int*, int*, int);

int main() {
    srand(time(NULL));
    clock_t start, end;
    FILE *file_sq = fopen("Lab1/SquaredTimeComplexity.csv", "w");
    FILE *file_li = fopen("Lab1/LinearTimeComplexity.csv", "w");

    if (!file_sq || !file_li) {
        return 1;
    }

    fprintf(file_sq, "n,time\n");
    fprintf(file_li, "n,time\n");

    for (int k = 1000; k <= 100000; k += 10000) {
        int n = k;
        int *X = (int*)calloc(n, sizeof(*X));
        int *A = (int*)calloc(n, sizeof(*X));
        int *B = (int*)calloc(n, sizeof(*X));

        if (!X || !A || !B) {
            free(X); free(A); free(B);
            return 1;
        }

        for (int i = 0; i < n; ++i) {
            X[i] = rand() % 100;
        }

        start = clock();
        avgsq(X, A, n);
        end = clock();
        double time_sq = ((double)(end - start)) / CLOCKS_PER_SEC;
        fprintf(file_sq, "%d,%.7f\n", n, time_sq);
        printf("[Squared] n = %d -> %.7f sec\n", n, time_sq);

        start = clock();
        for (int i = 0; i < 1000; ++i) {
            avgli(X, B, n);
        }
        end = clock();
        double time_li = ((double)(end - start)) / CLOCKS_PER_SEC / 1000;
        fprintf(file_li, "%d,%.9f\n", n, time_li);
        printf("[Linear ] n = %d -> %.9f sec\n", n, time_li);

        free(X); free(A); free(B);
    }

    fclose(file_sq);
    fclose(file_li);
    return 0;
}

int* avgsq(int* X, int* A, int n) {
    for (int i = 0; i < n; ++i) {
        int sum = 0;
        for (int j = 0; j <= i; ++j)
            sum += X[j];
        A[i] = sum / (i + 1);
    }
    return A;
}

int* avgli(int* X, int* A, int n) {
    volatile int sum = 0;
    for (int i = 0; i < n; ++i) {
        sum += X[i];
        A[i] = sum / (i + 1);
    }
    return A;
}