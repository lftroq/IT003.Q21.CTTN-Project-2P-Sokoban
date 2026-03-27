/**
 * @file mapGen.cpp
 * @brief Maze generation utility for game map creation
 * 
 * This module generates various types of maze layouts with obstacles,
 * portals, boxes, and player/goal positions. It supports three generation
 * modes: standard maze, separated maze (with middle wall), and symmetric maze.
 * 
 * @details
 * - Maze cells are encoded as integers:
 *   0 = walkable path, 1 = wall, 2 = box, 4 = portal A, 5 = portal B,
 *   6 = player start position, 7 = goal position
 * - Uses weighted random generation for varied obstacle placement
 * - Supports multiple maze generation strategies
 * 
 * @author lftroq
 * @version 1.0
 */
#include <bits/stdc++.h>
#define MASK(x) (1LL<<(x))
#define endl '\n'
#define int long long
#define fi first
#define se second

using namespace std;
typedef pair<int, int> pii;

mt19937_64 rng(time(0));

int N;

/**
 * @brief Generates a random integer within a given range
 * @param l Lower bound (inclusive)
 * @param r Upper bound (inclusive)
 * @return Random integer between l and r
 */
int Rand(int l, int r){
    int res = 0;
    for(int i=4; i; i--) res = res<<15|(rand()&(MASK(15) - 1));
    return l + res%(r - l + 1);
}

/**
 * @brief Generates a weighted random integer
 * @param l Lower bound (inclusive)
 * @param r Upper bound (inclusive)
 * @param t Weight parameter (negative = minimum bias, positive = maximum bias)
 * @return Weighted random integer
 */
int wRand(int l, int r, int t){
    int res = Rand(l, r);
    while(t < 0) res = min(res, Rand(l, r)), t++;
    while(t > 0) res = max(res, Rand(l, r)), t--;
    return res;
}

/**
 * @brief Generates blockages/obstacles in the maze
 * @param maze Input maze grid
 * @param num_b Number of blockages to generate
 * @param size_b Maximum size of blockages
 * @param size_w Weighting factor for blockage size distribution
 * @return Maze with generated blockages
 */
vector<vector<int>> gen_blockage_3(vector<vector<int>> maze, int num_b, int size_b, int size_w){
    for(int i=0; i<(int)maze.size(); i++){
        for(int j=0; j<(int)maze[0].size(); j++){
            maze[i][j] = 1;
        }
    }

    const int dx[] = {-1, 1, 0, 0};
    const int dy[] = {0, 0, -1, 1};
    for(int i=1; i<=num_b; i++){
        int x = Rand(0, (int)maze.size() - 1);
        int y = Rand(0, (int)maze[0].size() - 1);
        if(Rand(0, 3)){
            for(int j=0; j<4; j++){
                int d = wRand(0, size_b, size_w);
                for(int k=0; k<d; k++){
                    int u = x + dx[j] * k;
                    int v = y + dy[j] * k;
                    if(u < 0 || u >= (int)maze.size() || v < 0 || v >= (int)maze[0].size()) break;
                    maze[u][v] = 0;
                }
            }
        }
        else{
            int d = wRand(1, min(size_b, (int)min(maze.size() - x, maze[0].size() - y)), size_w) - 1;
            for(int j=0; j<=d; j++){
                maze[x][y + j] = maze[x + d][y + j] = 0;
                maze[x + j][y] = maze[x + j][y + d] = 0;
            }
        }
    }

    return maze;
}

/**
 * @brief Places portals at random walkable positions
 * @param maze Input maze grid
 * @param mask Bitmask to control which portals to place (bit 0: portal A, bit 1: portal B)
 * @return Maze with placed portals
 */
vector<vector<int>> gen_portal(vector<vector<int>> maze, int mask=3){
    vector<pii> pos;
    for(int i=0; i<(int)maze.size(); i++){
        for(int j=0; j<(int)maze[0].size(); j++){
            if(maze[i][j] == 0) pos.push_back({i, j});
        }
    }
    shuffle(pos.begin(), pos.end(), rng);
    if(mask&1) maze[pos[0].fi][pos[0].se] = 4;
    if(mask>>1&1) maze[pos[1].fi][pos[1].se] = 5;
    return maze;
}

/**
 * @brief Randomly places boxes in the maze
 * @param maze Input maze grid
 * @param num_box Number of boxes to place
 * @return Maze with placed boxes
 */
vector<vector<int>> gen_box(vector<vector<int>> maze, int num_box){
    vector<pii> pos;
    for(int i=0; i<(int)maze.size(); i++){
        for(int j=0; j<(int)maze[0].size(); j++){
            if(maze[i][j] == 0) pos.push_back({i, j});
        }
    }
    shuffle(pos.begin(), pos.end(), rng);
    num_box = min(num_box, (int)pos.size() - 2);
    for(int i=0; i<num_box; i++) maze[pos[i].fi][pos[i].se] = 2;
    return maze;
}

/**
 * @brief Places player and goal positions in the maze
 * @param maze Input maze grid
 * @param mask Bitmask to control positions (bit 0: player 1 start, bit 1: player 2 start)
 * @return Maze with placed positions
 */
vector<vector<int>> gen_position(vector<vector<int>> maze, int mask=3){
    vector<pii> pos;
    for(int i=0; i<(int)maze.size(); i++){
        for(int j=0; j<(int)maze[0].size(); j++){
            if(maze[i][j] == 0) pos.push_back({i, j});
        }
    }
    shuffle(pos.begin(), pos.end(), rng);
    if(mask&1) maze[pos[0].fi][pos[0].se] = 6;
    if(mask>>1&1) maze[pos[1].fi][pos[1].se] = 7;
    return maze;
}

/**
 * @brief Generates a standard unseparated maze
 * @return Complete maze grid of size N×N
 */
vector<vector<int>> gen_maze(){
    vector<vector<int>> maze(N, vector<int>(N, 0));
    maze = gen_blockage_3(maze, 30, 10, Rand(-1, 1));
    maze = gen_portal(maze);
    maze = gen_box(maze, 15);
    maze = gen_position(maze);
    return maze;
}

/**
 * @brief Generates a separated maze with a wall dividing two sections
 * @details Creates two symmetric sections separated by a wall row
 * @return Maze grid with separation
 */
vector<vector<int>> gen_sep_maze(){
    vector<vector<int>> maze(N/2-1, vector<int>(N, 0));
    maze = gen_blockage_3(maze, 15, 10, Rand(-1, 1));
    maze = gen_portal(maze, 1);
    maze = gen_box(maze, 10);
    maze = gen_position(maze, 1);
    vector<int> temp(N, 1);
    maze.push_back(temp);
    for(int i=N/2-1; i>=0; i--) {
        maze.push_back(maze[i]);
        for(int j=0; j<N; j++) {
            if(maze.back()[j] == 4) maze.back()[j] = 5;
            if(maze.back()[j] == 6) maze.back()[j] = 7;
        }
    }
    return maze;
}

/**
 * @brief Generates a vertically symmetric maze
 * @details Upper and lower halves are mirror images with swapped portal/position pairs
 * @return Vertically symmetric maze grid
 */
vector<vector<int>> gen_sym_maze(){
    vector<vector<int>> maze(N/2, vector<int>(N, 0));
    maze = gen_blockage_3(maze, 15, 10, Rand(-1, 1));
    maze = gen_portal(maze, 1);
    maze = gen_box(maze, 10);
    maze = gen_position(maze, 1);
    for(int i=N/2-1; i>=0; i--) {
        maze.push_back(maze[i]);
        for(int j=0; j<N; j++) {
            if(maze.back()[j] == 4) maze.back()[j] = 5;
            if(maze.back()[j] == 6) maze.back()[j] = 7;
        }
    }
    return maze;
}

/**
 * @brief Converts integer cell encoding to character representation
 * @param x Cell value (0-7)
 * @return Character representation of cell type
 */
char decode(int x){
    switch (x){
        case 0: return '.';
        case 1: return '#';
        case 2: return 'X';
        case 4: return 'A';
        case 5: return 'B';
        case 6: return 'a';
        case 7: return 'b';
    }
    return '?';
}

/**
 * @brief Outputs maze to file in text format
 * @param maze Maze grid to write
 * @details Writes maze.txt with character-encoded cells
 */
void print_maze(vector<vector<int>> maze){
    ofstream fout("maze.txt");

    for(int i=0; i<(int)maze.size(); i++){
        //cerr << "::: ";
        for(int j=0; j<(int)maze[0].size(); j++){
            fout << decode(maze[i][j]);
            //cerr << decode(maze[i][j]);
        }
        fout << '\n';
        //cerr << '\n';
    }

    fout.close();
}

int32_t main(){
    ios_base::sync_with_stdio(false);
    cin.tie(0);

    srand(time(NULL));
    string MODE;
    cin >> N >> MODE;

    vector<vector<int>> maze;
    if(MODE == "SEP") maze = gen_sep_maze();
    else if(MODE == "SYM") maze = gen_sym_maze();
    else maze = gen_maze();
    print_maze(maze);

    cerr << "NO BUG";

    return 0;
}
