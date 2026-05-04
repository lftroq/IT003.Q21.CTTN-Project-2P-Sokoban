/**
 * @file lftroq_v2.cpp
 * @brief Hard difficulty aggressive bot for Sokoban
 * 
 * This module implements an advanced bot that not only solves the puzzle
 * but also plays aggressively against the opponent when leading in score.
 * 
 * @details
 * - Serves as the "HARD" bot opponent
 * - Includes a defensive mode to block the opponent when ahead
 * - Employs Dijkstra's algorithm for optimal box pushing paths
 * 
 * @author lftroq
 * @version 2.0
 */
#include<bits/stdc++.h>
using namespace std;

const int MAX_N = 32;
const int dx[] = {-1, 0, 1, 0};
const int dy[] = {0, -1, 0, 1};
const char dir[] = {'U', 'L', 'D', 'R'};
const int TIME_LIMIT_MS = 320; // offset 50ms
/// Up, Left, Down, Right

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

    string solve(bool InvisibleBoxes = false) {
        /**
         * @method SokobanSolver::solve(bool InvisibleBoxes = false)
         * @brief Finds a partial or complete solution within TIME_LIMIT_MS.
         * 
         * @param InvisibleBoxes Consider boxes as empty cells or not
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
                if(InvisibleBoxes) grid[boxes[i].first][boxes[i].second] = '.';
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
                if(InvisibleBoxes) grid[box.first][box.second] = '.';
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
    char grid[MAX_N][MAX_N];
    string Reachable[MAX_N][MAX_N];
    string boxToGoal[MAX_N][MAX_N][4];
    bool vis[MAX_N][MAX_N];
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
        return 3 * playerDist + goalDist;
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

class AggressivePlayer {
/**
 * @class AggressivePlayer
 * @brief Defensive strategy when player is ahead in score.
 * 
 * Blocks opponent by:
 * - Moving toward opponent's goal location
 * - Positioning near boxes to deny box access
 * - Minimizing opponent's movement options
 * 
 * @param board Current game board state
 */
public:
    AggressivePlayer(vector<vector<char>> board) {
        N = (int)board.size();
        for(int i = 0; i < N; i++) for(int j = 0; j < N; j++) grid[i][j] = board[i][j];
        for(int i = 0; i < N; i++) for(int j = 0; j < N; j++) {
            if(grid[i][j] == 'a') {
                player = {i, j};
                grid[i][j] = '.';
            }
            else if(grid[i][j] == 'A') {
                playerGoal = {i, j};
                grid[i][j] = '#';
            }
            else if(grid[i][j] == 'b') opp = {i, j};
            else if(grid[i][j] == 'B') oppGoal = {i, j};
            else if(grid[i][j] == 'X') boxes.push_back({i, j});
        }
    }

    /// partial ans, find answer in TIME_LIMIS_MS
    int chosenDir = -1;
    double bestHeur = -1e9;
    string solve() {
        /**
         * @method AggressivePlayer::solve()
         * @brief Computes blocking move when player has score advantage.
         * 
         * Tries all 4 directions around opponent goal, selects move that:
         * 1. Minimizes distance to opponent
         * 2. Maximizes distance from opponent to nearest box
         * 3. Is reachable from current player position
         * 
         * @return Single move character (U/L/D/R) or 'S' (stay) if no valid move
         */
        string ans = "#";
        for(int i = 0; i < 4; i++) {
            // printMap();
            pair<int, int> newPos = {oppGoal.first + dx[i], oppGoal.second + dy[i]};
            if(!isInGrid(newPos)) continue;
            if(grid[newPos.first][newPos.second] == '#') continue;
            double temp = -abs(newPos.first - opp.first) - abs(newPos.second - opp.second);
            int minBoxDist = 1e9, minBoxIndex = -1;

            for(int j = 0; j < (int)boxes.size(); j++) {
                pair<int, int> box = boxes[j];
                grid[box.first][box.second] = '.';
                int boxDist = abs(box.first - newPos.first) + abs(box.second - newPos.second);
                if(minBoxDist > boxDist) {
                    minBoxDist = boxDist;
                    minBoxIndex = j;
                }
            }
            temp -= minBoxDist;
            // cerr << i << ' ' << newPos.first << ' ' << newPos.second << ": " << temp << endl;
            // cerr << newPos.first << ' ' << newPos.second << '\n';
            // printMap();
            // cerr << "===" << endl;
            string curPath = bfsReach(player, oppGoal, newPos);
            if(curPath.empty()) curPath = "S";
            if(curPath[0] == '#') continue;
            if(bestHeur < temp) {
                bestHeur = temp;
                chosenDir = i;
                ans = curPath;
            }
            for(int j = 0; j < (int)boxes.size(); j++) {
                pair<int, int> box = boxes[j];
                grid[box.first][box.second] = 'X';
            }
        }
        // cerr << bestHeur << ' ' << chosenDir << ": " << oppGoal.first << ' ' << oppGoal.second << "   " << player.first << ' ' << player.second << '\n';
        return ans;
    }
private:
    int N;
    char grid[MAX_N][MAX_N];
    string Reachable[MAX_N][MAX_N];
    string boxToGoal[MAX_N][MAX_N][4];
    bool vis[MAX_N][MAX_N];
    pair<int, int> player = {-1, -1}, playerGoal = {-1, -1};
    pair<int, int> opp = {-1, -1}, oppGoal = {-1, -1};
    vector<pair<int, int>> boxes; /// {-1, -1} if done

    void printMap() {
        for(int i = 0; i < N; i++) {
            for(int j = 0; j < N; j++) cout << grid[i][j];
            cout << endl;
        }
    }

    bool isInGrid(pair<int, int> pos) {
        return (0 <= min(pos.first, pos.second) && max(pos.first, pos.second) < N);
    }

    /// Check if player can go to goal if don't push the box
    string bfsReach(pair<int, int> player, pair<int, int> box, pair<int, int> goal) {
        for(int i = 0; i < N; i++) for(int j = 0; j < N; j++) Reachable[i][j] = "#";
        grid[box.first][box.second] = '#';
        queue<pair<int, int>> q;
        Reachable[player.first][player.second] = "";
        q.push(player);
        while((int)q.size()) {
            pair<int, int> pos = q.front();
            if(pos == goal) {
                grid[box.first][box.second] = 'B';
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
        grid[box.first][box.second] = 'B';
        return Reachable[goal.first][goal.second];
    }
};

int main(){
    ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
    int N, T_cur, T_total, playerScore, oppScore;
    cin >> N >> T_cur >> T_total;
    vector<vector<char>> board(N, vector<char>(N));
    for(int i = 0; i < N; i++) for(int j = 0; j < N; j++)
        cin >> board[i][j];
    vector<char> playerHist(T_cur), oppHist(T_cur), playerMoved(T_cur), oppMoved(T_cur);
    for(int i = 0; i < T_cur - 1; i++)
        cin >> playerHist[i] >> oppHist[i] >> playerMoved[i] >> oppMoved[i];
    cin >> playerScore >> oppScore;

    if(playerScore > oppScore) {
        AggressivePlayer solver_aggressively(board);
        string ans = solver_aggressively.solve();
        // cerr << ":::" << ans << '\n';
        if(ans.size() && ans[0] != '#') {
            cout << ans[0];
            return 0;
        }
    }

    SokobanSolver solver(board);
    string ans = solver.solve(false);
    if(ans.size()) {
        cout << ans[0];
        return 0;
    }
    ans = solver.solve(true);
    // cerr << ":::" << ans << endl;
    if(ans.size()) {
        cout << ans[0];
        return 0;
    }

    cout << 'S';
    return 0;
}
