// Write a program that show that two files named ‘Source 1’ and ‘Source 2’ contains sorted list of integers. 
// Read the content of both the files and stores the merged list in sorted form in a new file named ‘Target’.

#include<iostream>
#include<vector>
#include<fstream>
#include<algorithm>
using namespace std;

int main() {

    ifstream fileA("source_1.txt");
    ifstream fileB("source_2.txt");
    ofstream target("target.txt");

    if(!fileA.is_open() || !fileB.is_open()){
        cout<<"Error opening the file"<<endl;
    }

    vector<int> numbers;
    int num;

    while(fileA >> num) {
        numbers.push_back(num);
    }

    while(fileB >> num) {
        numbers.push_back(num);
    }

    sort(numbers.begin(), numbers.end());

    for(int n : numbers) {
        target << n << "\t";
    }

    fileA.close();
    fileB.close();
    target.close();
};;