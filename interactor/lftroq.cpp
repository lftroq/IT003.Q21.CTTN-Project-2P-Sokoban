/**
 * @file lftroq.cpp
 * @brief Medium difficulty heuristic bot for Sokoban
 * 
 * This module implements a bot that uses heuristic evaluation and BFS
 * pathfinding to solve the Sokoban puzzle.
 * 
 * @details
 * - Serves as the "MED" bot opponent
 * - Evaluates box priorities based on distance to player and goal
 * - Uses BFS to find pushing paths within a time limit
 * 
 * @author lftroq
 * @version 1.0
 */
#include<bits/stdc++.h>
using namespace std;

const int dx[] = {-1, 0, 1, 0};
const int dy[] = {0, -1, 0, 1};
const char dir[] = {'U', 'L', 'D', 'R'};
const int TIME_LIMIT_MS = 950; // offset 50ms
/// Up, Left, Down, Right

mt19937_64 rng(time(0));

class SokobanSolver {
/**
 * @class SokobanSolver
 * @brief Solves single-player Sokoban puzzle by strategically moving boxes to goals.
 * 
 * This class implements a heuristic-based solver for Sokoban that:
 * - Identifies and prioritizes boxes based on proximity to player and goal
 * - Uses BFS to find paths for pushing boxes to target positions
 * - Operates within a strict time limit (450ms) for partial solutions
 * 
 * @param board Initial game board with player ('a'), goal ('A'), boxes ('X'), walls ('#')
 */
public:
    SokobanSolver(vector<vector<char>> board) {
        N = (int)board.size();
        for(int i = 0; i < N; i++) for(int j = 0; j < N; j++) grid[i][j] = board[i][j];
        for(int i = 0; i < N; i++) for(int j = 0; j < N; j++) {
            if(grid[i][j] == 'a') {
                player = {i, j};
                grid[i][j] = '.';
            }
            else if(grid[i][j] == 'A') goal = {i, j};
            else if(grid[i][j] == 'X') boxes.push_back({i, j});
            else if(grid[i][j] == 'B' || grid[i][j] == 'b') grid[i][j] = '#';
        }
    }

    string solve() {
        /**
         * @method SokobanSolver::solve()
         * @brief Finds a partial or complete solution within TIME_LIMIT_MS.
         * 
         * Algorithm:
         * 1. Selects the most promising box using heuristic evaluation
         * 2. Checks if box can be pushed toward goal from reachable positions
         * 3. Executes push sequence if path exists
         * 4. Returns after first successful move or time limit exceeded
         * 
         * @return String of moves (U/L/D/R) representing player actions, or empty if no solution found
         * @time O(N^4) per move due to BFS operations
         */
        string ans = "";
        clock_t start = clock();
        while(true) {
            /// Time management
            double elapsed = double(clock() - start) / CLOCKS_PER_SEC * 1000;
            if (elapsed > TIME_LIMIT_MS) break;
            // printMap();

            /// Choosing the most potential box
            for(int i = 0; i < (int)boxes.size(); i++) {
                pair<int, int> box = boxes[i];
                if(box.first == -1) continue;
                grid[boxes[i].first][boxes[i].second] = '#';
            }
            double bestHeur = -1e9;
            int bestBoxIndex = -1;

            for(int i = 0; i < (int)boxes.size(); i++) {
                pair<int, int> box = boxes[i];
                if(box.first == -1) continue;
                grid[box.first][box.second] = 'X';
                bool isPotential = false;
                for(int dir = 0; dir < 4; dir++) {
                    pair<int, int> behind = {box.first - dx[dir], box.second - dy[dir]};
                    if(!isInGrid(behind)) continue;
                    if(grid[behind.first][behind.second] == '#') continue;
                    string toMove = bfsReach(player, box, behind);
                    if(toMove[0] != '#') isPotential = true;
                }
                if(isPotential) {
                    double temp = heuristicEvaluation(box);
                    if(bestHeur < temp) {
                        bestBoxIndex = i;
                        bestHeur = temp;
                    }
                }
                grid[box.first][box.second] = '#';
            }
            if(bestBoxIndex == -1) break;

            /// Execute SingleBoxSolver

            pair<int, int> box = boxes[bestBoxIndex];
            boxes[bestBoxIndex] = {-1, -1};
            string temp = bfsBox(player, box, goal);
            // cerr << "Box: " << box.first << ' ' << box.second << endl;
            // cout << "Player: " << player.first << ' ' << player.second << endl;
            // for(int i=0;i<(int)boxes.size();i++) cerr << boxes[i].first << ' ' << boxes[i].second << endl;
            // cerr << temp << endl;
            if(temp == "#") continue;
            for(int i = 0; i < (int)temp.size(); i++) {
                if(temp[i] == 'U') player.first--;
                if(temp[i] == 'L') player.second--;
                if(temp[i] == 'D') player.first++;
                if(temp[i] == 'R') player.second++;
                ans.push_back(temp[i]);
            }
            grid[box.first][box.second] = '.';
            if(ans.size()) break;
        }
        return ans;
        // Choose last box
        // for(int i = 0; i < (int)boxes.size(); i++) {
        //     pair<int, int> box = boxes[i];
        //     grid[box.first][box.second] = '#';
        // }
        // while((int)boxes.size()) {
        //     pair<int, int> box = boxes.back();
        //     boxes.pop_back();
        //     string temp = bfsBox(player, box, goal);
        //     if(temp == "#") continue;
        //     for(int i = 0; i < (int)temp.size(); i++) {
        //         if(temp[i] == 'U') player.first--;
        //         if(temp[i] == 'L') player.second--;
        //         if(temp[i] == 'D') player.first++;
        //         if(temp[i] == 'R') player.second++;
        //         ans.push_back(temp[i]);
        //     }
        //     grid[box.first][box.second] = '.';
        // }
        // return ans;
    }
private:
    int N;
    char grid[32][32];
    string Reachable[32][32];
    string boxToGoal[32][32][4];
    bool vis[32][32];
    pair<int, int> player = {-1, -1}, goal = {-1, -1};
    vector<pair<int, int>> boxes; /// {-1, -1} if done

    void printMap() {
        for(int i = 0; i < N; i++) {
            for(int j = 0; j < N; j++) cout << grid[i][j];
            cout << endl;
        }
    }

    double heuristicEvaluation(pair<int, int> boxes) {
        /**
         * @method SokobanSolver::heuristicEvaluation(pair<int,int> boxes)
         * @brief Evaluates priority of a box for pushing.
         * 
         * Uses weighted combination: 2 * (negative player distance) + (negative goal distance)
         * Prioritizes boxes close to goal while maintaining player accessibility.
         * 
         * @param boxes Target box coordinates
         * @return Double value representing box priority (higher = better)
         */
        int playerDist = -abs(boxes.first - player.first) - abs(boxes.second - player.second);
        int goalDist = -abs(boxes.first - goal.first) - abs(boxes.second - goal.second);
        /// Choose the nearest box to player
        /// Caution: May cause infinite loop
        // return playerDist;
        /// Choose the nearest box to goal
        // return goalDist;
        return 2 * playerDist + goalDist;
    }

    bool isInGrid(pair<int, int> pos) {
        return (0 <= min(pos.first, pos.second) && max(pos.first, pos.second) < N);
    }

    /// Check if player can go to goal if don't push the box
    string bfsReach(pair<int, int> player, pair<int, int> box, pair<int, int> goal) {
        /**
         * @method SokobanSolver::bfsReach(pair<int,int> player, pair<int,int> box, pair<int,int> goal)
         * @brief BFS pathfinding that treats box as obstacle.
         * 
         * Finds shortest path from player to goal without pushing the specified box.
         * Used to position player behind boxes for pushing.
         * 
         * @param player Starting position
         * @param box Obstacle position
         * @param goal Target position
         * @return Path string or "#" if unreachable
         */
        for(int i = 0; i < N; i++) for(int j = 0; j < N; j++) Reachable[i][j] = "#";
        grid[box.first][box.second] = '#';
        queue<pair<int, int>> q;
        Reachable[player.first][player.second] = "";
        q.push(player);
        while((int)q.size()) {
            pair<int, int> pos = q.front();
            if(pos == goal) {
                grid[box.first][box.second] = '.';
                return Reachable[pos.first][pos.second];
            }
            q.pop();
            for(int i = 0; i < 4; i++) {
                pair<int, int> newPos = {pos.first + dx[i], pos.second + dy[i]};
                if(!isInGrid(newPos)) continue;
                if(grid[newPos.first][newPos.second] == '#' || grid[newPos.first][newPos.second] == 'A') continue;
                if(Reachable[newPos.first][newPos.second] == "#") {
                    Reachable[newPos.first][newPos.second] = Reachable[pos.first][pos.second];
                    Reachable[newPos.first][newPos.second].push_back(dir[i]);
                    q.push(newPos);
                }
            }
        }
        grid[box.first][box.second] = '.';
        return Reachable[goal.first][goal.second];
    }

    /// Check if player can push box to the goal
    string bfsBox(pair<int,int> player, pair<int,int> box, pair<int,int> goal) {
        /**
         * @method SokobanSolver::bfsBox(pair<int,int> player, pair<int,int> box, pair<int,int> goal)
         * @brief Dijkstra's algorithm to push box to goal position.
         * 
         * Explores states combining box position and push direction.
         * Two transition cases:
         * 1. Change push direction: reposition player and continue
         * 2. Continue pushing: advance box in same direction
         * 
         * @param player Current player position
         * @param box Current box position
         * @param goal Target box position
         * @return Complete move sequence to push box to goal, or "#" if impossible
         */
        grid[box.first][box.second] = '.';
        for(int i = 0; i < N; i++) for(int j = 0; j < N; j++) for(int k = 0; k < 4; k++) boxToGoal[i][j][k] = "#";
        priority_queue<pair<pair<int, int>, pair<int, int>>, vector<pair<pair<int, int>, pair<int, int>>>, greater<pair<pair<int, int>, pair<int, int>>>> pq;
        for(int i = 0; i < 4; i++) {
            pair<int, int> behind = {box.first - dx[i], box.second - dy[i]};
            if(!isInGrid(behind)) continue;
            if(grid[behind.first][behind.second] == '#' || grid[behind.first][behind.second] == 'A') continue;
            string toMove = bfsReach(player, box, behind);
            if(toMove[0] != '#') {
                // cout << behind.first << ' ' << behind.second << ' ' << grid[behind.first][behind.second] << endl; // DEBUG
                boxToGoal[box.first][box.second][i] = toMove;
                pq.push({{boxToGoal[box.first][box.second][i].size(), i}, box});
            }
           // printMap(); // DEBUG
        }
        while((int)pq.size()) {
            int curDist = pq.top().first.first;
            pair<int, int> pos = pq.top().second;
            int d = pq.top().first.second;
            pq.pop();
            if((int)boxToGoal[pos.first][pos.second][d].size() != curDist) continue;
            // cout << boxToGoal[pos.first][pos.second][d] << ' ' << pos.first << ' ' << pos.second << ' ' << d << endl; // DEBUG
            if(pos == goal) {
                return boxToGoal[pos.first][pos.second][d];
            }
            /// Case 1: Box change its direction
            for(int i = 0; i < 4; i++) {
                if(i == d) continue;
                pair<int, int> behind1 = {pos.first - dx[d], pos.second - dy[d]};
                pair<int, int> behind2 = {pos.first - dx[i], pos.second - dy[i]};
                if(!isInGrid(behind1) || !isInGrid(behind2)) continue;
                if(grid[behind1.first][behind1.second] == '#' || grid[behind2.first][behind2.second] == '#') continue;
                if(grid[behind1.first][behind1.second] == 'A' || grid[behind2.first][behind2.second] == 'A') continue;
                string toMove = bfsReach(behind1, pos, behind2);
                if(toMove[0] == '#') continue; // can't move to behind the box
                if((int)boxToGoal[pos.first][pos.second][i][0] == '#') {
                    boxToGoal[pos.first][pos.second][i] = boxToGoal[pos.first][pos.second][d];
                    boxToGoal[pos.first][pos.second][i] += toMove;
                    pq.push({{curDist + (int)toMove.size(), i}, pos});
                }
                if((int)boxToGoal[pos.first][pos.second][i].size() > curDist + (int)toMove.size()) {
                    boxToGoal[pos.first][pos.second][i] = boxToGoal[pos.first][pos.second][d];
                    boxToGoal[pos.first][pos.second][i] += toMove;
                    pq.push({{curDist + (int)toMove.size(), i}, pos});
                }
            }
            /// Case 2: Box move to next grid
            pair<int, int> newPos = {pos.first + dx[d], pos.second + dy[d]};
            if(isInGrid(newPos)) {
                char cell = grid[newPos.first][newPos.second];
                if(cell == '#') continue;
                if(boxToGoal[newPos.first][newPos.second][d][0] == '#') {
                    boxToGoal[newPos.first][newPos.second][d] = boxToGoal[pos.first][pos.second][d];
                    boxToGoal[newPos.first][newPos.second][d].push_back(dir[d]);
                    pq.push({{curDist + 1, d}, newPos});
                }
                if((int)boxToGoal[newPos.first][newPos.second][d].size() > curDist + 1) {
                    boxToGoal[newPos.first][newPos.second][d] = boxToGoal[pos.first][pos.second][d];
                    boxToGoal[newPos.first][newPos.second][d].push_back(dir[d]);
                    pq.push({{curDist + 1, d}, newPos});
                }
            }
        }
        grid[box.first][box.second] = '#';
        return "#";
    }
};

int main(){
    ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
    int N,T_cur,T_total;
    cin >> N >> T_cur >> T_total;
    vector<vector<char>> board(N, vector<char>(N));
    for(int i = 0; i < N; i++) for(int j = 0; j < N; j++)
        cin >> board[i][j];
    if(rng() % 5 == 0) { // nerf, move randomly with 20% probability
        cout << dir[rng() % 5];
        return 0;
    }
    SokobanSolver solver(board);
    string ans=solver.solve();
    cout << ans[0];
    return 0;
}
