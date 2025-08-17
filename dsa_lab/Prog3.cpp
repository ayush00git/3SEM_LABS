#include<bits/stdc++.h>
using namespace std;

int bin(vector<int>& a, int target){
    int low = 0;
    int high = a.size() - 1;
    
    while(low <= high){
        int mid = low + (high - low) / 2;
        if(a[mid] == target){
            a.erase(a.begin() + mid);
            return mid;
        }
        else if(a[mid] < target){
            low = mid + 1;
        }else{
            high = mid - 1;
        }
    }
    return -1;
}
int main() {

    vector<int> a = {12, 22, 32, 53, 64, 72};
    
    int target;
    cout<<"Enter the element you wanna search: ";
    cin>>target;
    
    int m = (bin(a, target));
    cout<<m<<endl;

    if(m == -1){
        for(int i = 0; i < a.size(); i++){
            if(target < a[i]){
                int t = a[i];
                a[i] = target;
                target = t;
            }
        }
        a.push_back(target);
    }

    for(auto it: a){
        cout<<it<<"\t";
    }

    cout<<endl;
}