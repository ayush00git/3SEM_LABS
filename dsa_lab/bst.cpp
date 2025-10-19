// Implement a Binary Search Tree and insert and delete a node in the BST.

#include<bits/stdc++.h>
using namespace std;

class Node {
    public:
    int val;
    Node* left;
    Node* right;

    Node(int v) : val(v), left(NULL), right(NULL) {}
};

Node* insert(Node* root, int val) {
    if(!root) return new Node(val);
    if(root->val < val){
        root->right = insert(root->right, val);
    }
    else if(root->val > val){
        root->left = insert(root->left, val);
    }
    return root;
}

Node* minVal(Node* root) {
    while(root && root->left) root = root->left;
    return root;
}

Node* erase(Node* root, int val) {
    if(!root) return root;
    if(root->val < val) {
        root->right = erase(root->right, val);
    }else if(root->val > val) {
        root->left = erase(root->left, val);
    }
    else{
        // no child
        if(!root->left){
            Node* r = root->right;
            delete root;
            return r; // null
        }
        // single child
        else if(!root->right) {
            Node* l = root->left;
            delete root;
            return l;
        }
        // two children
        else {
            Node* suc = minVal(root->right);
            root->val = suc->val;
            root->right = erase(root->right, suc->val);
        }
    }
    return root;
}


void inorder(Node* root) {
    if(!root) return;
    inorder(root->left);
    cout<<root->val<<"\t";
    inorder(root->right);
}

int main() {

    Node* root = NULL;

    // root = insert(root, 12);
    // root = insert(root, 3);
    // root = insert(root, 7);
    // root = insert(root, 2);
    // root = insert(root, 15);
    // root = insert(root, 13);
    // root = insert(root, 16);

    // root = erase(root, 12);

    // inorder(root);
    // cout<<endl;

    
    int v;
    while(true) {
        char z;
        cout<<"Enter i (for insertion) or d (for deletion) or t (inorder traversal): ";
        cin>>z;
        switch (z)
        {
        case 'i':
            cout<<"Enter the value you wanna insert to the BST: ";
            cin>>v;
            root = insert(root, v);
            break;
        
        case 'd':
            cout<<"Enter the value you want to delete from the BST: ";
            cin>>v;
            root = erase(root, v);
            break;
        
        case 't':
            inorder(root);
            break;

        default:
            break;
        }
    }

}