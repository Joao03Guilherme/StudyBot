#include<iostream>

using namespace std;

int main(void){
    int n, m, v1, v2;
    cin >> n >> m;
    
    int adj[n][n]; 
    memset(adj, 0, sizeof(adj));
    
    for (int i = 0; i < m; i++)
    {
        cin >> v1 >> v2;
        adj[v1][v2] = 1;
        adj[v2][v1] = 1;
    }
    
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            cout << adj[i][j] << " ";
        }
        cout << "\n";
    }
    return 0; 
}