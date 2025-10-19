#include<iostream>
#include<queue>
using namespace std;

class Node {
    public:
    int key;
    Node* left;
    Node* right;

    Node(int value) {
        key = value;
        left = right = nullptr;
    }

};

class BinaryTree {

    private:
    Node* root;

    public:
    BinaryTree() {
        root = nullptr;
    }

    void insert(int value) {
        Node* newNode = new Node(value); 
        if(root == nullptr){
            root = newNode;
            return;
        }

        queue<Node*> q;
        q.push(root);

        while(!q.empty()){
            Node* temp = q.front();
            q.pop();

            if(temp->left == nullptr){
                temp->left = newNode;
                return;
            }else{
                q.push(temp->left);
            }

            if(temp->right == nullptr){
                temp->right = newNode;
                return;
            }else{
                q.push(temp->right);
            }
        }
    }

    void levelOrder() {
        if(root == nullptr) return;

        queue<Node*> q;
        q.push(root);

        while(!q.empty()){
            Node* temp = q.front();
            q.pop();
            cout<<temp->key<<"\t";
            if(temp->left) q.push(temp->left);
            if(temp->right) q.push(temp->right);
        }
        cout<<endl;
    }

    // Root - left - right
    void preorder(Node* node) {
        if(node == nullptr) return;
        cout<<node->key<<"\t";
        preorder(node->left);
        preorder(node->right);
    }

    // Left - Root - Right
    void inorder(Node* node) {
        if(node == nullptr) return;
        inorder(node->left);
        cout<<node->key<<"\t";
        inorder(node->right);
    }

    // Left - Right - Root
    void postorder(Node* node) {
        if(node == nullptr) return;
        postorder(node->left);
        postorder(node->right);
        cout<<node->key<<"\t";
    }

    void printPreorder() {
        preorder(root);
        cout<<endl;
    }

    void printInorder() {
        inorder(root);
        cout<<endl;
    }
    void printPostorder() {
        postorder(root);
        cout<<endl;
    }
};

int main()
{

    BinaryTree bt;
    bt.insert(2);
    bt.insert(3);
    bt.insert(4);
    bt.insert(6);
    bt.insert(7);
    bt.insert(9);

    cout<<"Postorder traversal: "<<endl;
    bt.printPostorder();

    cout<<"Preorder traversal: "<<endl;
    bt.printPreorder();

    cout<<"Inorder traversal: "<<endl;
    bt.printInorder();
    // bt.levelOrder();
}