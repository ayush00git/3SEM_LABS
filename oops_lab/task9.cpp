#include<bits/stdc++.h>
using namespace std;

int main() {
    fstream file1("source1.txt", ios::in);
    fstream file2("source2.txt", ios::in);
    fstream target("target.txt", ios::out);
    
    vector<int> numbers;
    int nums;

    while(file1 >> nums) {
        numbers.push_back(nums);
    }

    while(file2 >> nums) {
        numbers.push_back(nums);
    }

    sort(numbers.begin(), numbers.end());

    for(int n : numbers) {
        target << n << "\t";
    }

    file1.close();
    file2.close();
    target.close();

    return 0;
}