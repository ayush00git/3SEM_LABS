#include<bits/stdc++.h>
using namespace std;

pair<int, int> conOrVow(const char a[]){
    int n = strlen(a);
    int vow = 0, cons = 0; 
    for(int i = 0; i < n; i++){
        char ch = tolower(a[i]);
        if(ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u'){
            vow++;
        }else if(isalpha(ch)){
            cons++;
        }
    }
    return {vow, cons};
}

bool nullCounts(char ch[]){
    int n = strlen(ch);
    int cnt = 0;
    int i = 0;
    
    while(ch[i] != '\0'){
        cnt++;
        i++;
    }

    if(n == cnt) return true;
    return false;
}

void startsWithA(const char sent[]) {
    int n = strlen(sent);
    string word = "";

    for (int i = 0; i <= n; i++) {
        if (sent[i] == ' ' || sent[i] == '\0') {
            if (!word.empty() && (word[0] == 'a' || word[0] == 'A')) {
                cout<<word<<endl;
            }
            word = "";
        } else {
            word += sent[i];
        }
    }
}


int main() {

    char st[100];
    cout<<"Enter the string: ";
    cin.getline(st, 100);
    
    pair<int, int> res = conOrVow(st);
    cout<<"Number of vowels in the string are: "<<res.first<<" and consonants: "<<res.second<<endl;

    bool counts = nullCounts(st);
    cout<<"strlen does not count null char? : "<<counts<<endl; 

    startsWithA(st);
}