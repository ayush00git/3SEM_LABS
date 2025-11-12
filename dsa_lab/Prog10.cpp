#include <iostream>
#include <vector>
using namespace std;

class GraphList
{
    int V;
    vector<vector<int>> adj;

public:
    GraphList(int vertices)
    {
        V = vertices;
        adj.resize(V);
    }

    void addEdge(int u, int v)
    {
        adj[u].push_back(v); // directed edge
    }

    void display()
    {
        cout << "\nAdjacency List Representation:\n";
        for (int i = 0; i < V; i++)
        {
            cout << i << " -> ";
            for (int node : adj[i])
                cout << node << " ";
            cout << endl;
        }
    }

    GraphList getTranspose()
    {
        GraphList gT(V);
        for (int u = 0; u < V; u++)
        {
            for (int v : adj[u])
                gT.addEdge(v, u); // reverse edge
        }
        return gT;
    }
};

class GraphMatrix
{
    int V;
    vector<vector<int>> adjMat;

public:
    GraphMatrix(int vertices)
    {
        V = vertices;
        adjMat.resize(V, vector<int>(V, 0));
    }

    void addEdge(int u, int v)
    {
        adjMat[u][v] = 1;
    }

    void display()
    {
        cout << "\nAdjacency Matrix Representation:\n";
        for (int i = 0; i < V; i++)
        {
            for (int j = 0; j < V; j++)
                cout << adjMat[i][j] << " ";
            cout << endl;
        }
    }

    GraphMatrix getTranspose()
    {
        GraphMatrix gT(V);
        for (int i = 0; i < V; i++)
        {
            for (int j = 0; j < V; j++)
            {
                if (adjMat[i][j] == 1)
                    gT.addEdge(j, i); // reverse edge
            }
        }
        return gT;
    }
};

int main()
{
    int choice;
    cout << "  GRAPH TRANSPOSE\n";
    cout << "1. Using Adjacency List\n";
    cout << "2. Using Adjacency Matrix\n";
    cout << "Enter your choice (1 or 2): ";
    cin >> choice;

    int V, E;
    cout << "\nEnter number of vertices: ";
    cin >> V;
    cout << "Enter number of edges: ";
    cin >> E;

    cout << "Enter edges in format (u v) for directed edge u -> v:\n";

    switch (choice)
    {
    case 1:
    {
        GraphList g(V);
        for (int i = 0; i < E; i++)
        {
            int u, v;
            cin >> u >> v;
            g.addEdge(u, v);
        }

        cout << "\nOriginal Graph:";
        g.display();

        GraphList gT = g.getTranspose();
        cout << "\nTranspose Graph:";
        gT.display();
        break;
    }

    case 2:
    {
        GraphMatrix g(V);
        for (int i = 0; i < E; i++)
        {
            int u, v;
            cin >> u >> v;
            g.addEdge(u, v);
        }

        cout << "\nOriginal Graph:";
        g.display();

        GraphMatrix gT = g.getTranspose();
        cout << "\nTranspose Graph:";
        gT.display();
        break;
    }

    default:
        cout << "\nInvalid choice! Please restart the program and choose 1 or 2.\n";
        break;
    }

    cout << "\nProgram ended successfully.\n";
    return 0;
}