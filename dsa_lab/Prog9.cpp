#include <iostream>
#include <vector>
using namespace std;

class MaxHeap {
private:
    vector<int> heap;

    int parent(int i) { return (i - 1) / 2; }
    int left(int i) { return 2 * i + 1; }
    int right(int i) { return 2 * i + 2; }

    void heapifyUp(int i) {
        // Move up until heap property is restored
        while (i > 0 && heap[parent(i)] < heap[i]) {
            swap(heap[i], heap[parent(i)]);
            i = parent(i);
        }
    }

    void heapifyDown(int i) {
        int largest = i;
        int l = left(i);
        int r = right(i);

        // Find the largest among node and its children
        if (l < heap.size() && heap[l] > heap[largest])
            largest = l;
        if (r < heap.size() && heap[r] > heap[largest])
            largest = r;

        // If root is not largest, swap and continue
        if (largest != i) {
            swap(heap[i], heap[largest]);
            heapifyDown(largest);
        }
    }

public:
    // Insert a new element into the heap
    void insert(int value) {
        heap.push_back(value);
        heapifyUp(heap.size() - 1);
    }

    // Return the maximum element (root)
    int getMax() {
        if (heap.empty()) {
            cout << "Heap is empty!\n";
            return -1;
        }
        return heap[0];
    }

    // Remove and return the maximum element
    int extractMax() {
        if (heap.empty()) {
            cout << "Heap is empty!\n";
            return -1;
        }

        int maxValue = heap[0];
        heap[0] = heap.back();
        heap.pop_back();
        if (!heap.empty())
            heapifyDown(0);
        return maxValue;
    }

    // Print heap as array
    void printHeap() {
        for (int val : heap)
            cout << val << " ";
        cout << endl;
    }
};

int main() {
    MaxHeap pq;

    pq.insert(10);
    pq.insert(30);
    pq.insert(20);
    pq.insert(5);

    cout << "Heap elements: ";
    pq.printHeap();

    cout << "Maximum: " << pq.getMax() << endl;

    cout << "Extracting max: " << pq.extractMax() << endl;

    cout << "Heap after extraction: ";
    pq.printHeap();

    return 0;
}