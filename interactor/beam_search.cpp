/**
 * @file beam_search.cpp
 * @brief Bot implementation for Sokoban.
 * 
 * This file contains the implementation of the beam_search bot,
 * utilizing specific search algorithms to evaluate and output the best move.
 */
#include <bits/stdc++.h>
using namespace std;

const int MAX_N = 32;
const int dx[] = {-1, 0, 1, 0, 0};
const int dy[] = {0, -1, 0, 1, 0};
const char dir[] = {'U', 'L', 'D', 'R', 'S'};
const int TIME_LIMIT_MS = 450; // offset 50ms
const int BEAM_W = 90;
const int DEPTH = 16;
/// Up, Left, Down, Right


int getAct(char c) {
    /**
    * @brief Converts a character representation of a move into an integer ID.
    * @param c The physical move character ('U', 'L', 'D', 'R', or anything else for stay).
    * @return Integer ID from 0 to 4.
    */
    if(c == 'U') return 0;
    if(c == 'L') return 1;
    if(c == 'D') return 2;
    if(c == 'R') return 3;
    return 4;
}

char getDir(int act) {
    if(act == 0) return 'U';
    if(act == 1) return 'L';
    if(act == 2) return 'D';
    if(act == 3) return 'R';
    return 'S';
}

bool isOppAct(int a, int b) {
    if(a == 4 || b == 4) return false;
    return (a == 0 && b == 2) || (a == 2 && b == 0) || (a == 1 && b == 3) || (a == 3 && b == 1);
}

mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());

struct ZobristHash {
    /**
    * @brief Zobrist hashing implementation for state tracking.
    * 
    * Generates and stores 64-bit random integers for cell states,
    * player positions, and scores to quickly compute distinct hashes
    * for explored game states, preventing redundant evaluations.
    */
    long long boxRand[MAX_N][MAX_N], playerRand[MAX_N][MAX_N], scoreRand[2 * MAX_N * MAX_N];
    ZobristHash() {
        for(int i = 0; i < MAX_N; i++) {
            for(int j = 0; j < MAX_N; j++) {
                boxRand[i][j] = rng();
                playerRand[i][j] = rng();
            }
        }
        for(int i = 0; i < MAX_N * MAX_N; i++) scoreRand[i] = rng();
    }
};

/**
 * @brief Represents a single possible state of the game during the search.
 * 
 * Tracks dynamic properties such as player position, box locations,
 * the sequence of actions, the scoring delta, and the Zobrist hash 
 * associated with this specific configuration.
 */
struct State {
    int N;
    pair<int, int> player;
    pair<int, int> goal;
    vector<pair<int, int>> boxes;
    int score = 0;
    int lastAct = 4;
    int prevAct = 4;
    bool lastPushed = false;
    int lastScoreDelta = 0;

    long long Hash = 0;
    string firstPlan = "";
    long long value = LLONG_MIN; // value of state

    bool operator<(const State& o) const {
        if (score != o.score) return score < o.score;
        if (player != o.player) return player < o.player;
        return boxes < o.boxes;
    }
};

class BeamSearch {
/**
 * @class BeamSearch
 * @brief Solves multiplayer Sokoban by strategically chosing the most value move.
 * 
 * This class implements a heuristic-based solver for Sokoban that:
 * - Uses Beam Search to find optimal move.
 * - Operates within a strict time limit (450ms) for partial solutions
 * 
 * @param board Initial game board with player ('a'), goal ('A'), boxes ('X'), walls ('#')
 */
public:
    BeamSearch(vector<vector<char>> board, vector<char> aHist, int scoreDelta) {
        N = (int)board.size();
        for(int i = 0; i < N; i++) for(int j = 0; j < N; j++) grid[i][j] = board[i][j];
        for(int i = 0; i < N; i++) for(int j = 0; j < N; j++) {
            if(grid[i][j] == 'a') {
                player = {i, j};
                grid[i][j] = '.';
            }
            else if(grid[i][j] == 'A') goal = {i, j};
            else if(grid[i][j] == 'B') oppGoal = {i, j};
            else if(grid[i][j] == 'b') {
                opp = {i, j};
                grid[i][j] = '.';
            }
            else if(grid[i][j] == 'X') {
                boxes.push_back({i, j});
                grid[i][j] = '.';
            }
        }
        precomputeDists();
        root.N = N;
        root.player = player;
        root.goal = goal;
        root.boxes = boxes;
        root.score = scoreDelta;
        root.Hash = 0;
        for(int i = 0; i < N; i++) {
            for(int j = 0; j < N; j++) {
                if(grid[i][j] == 'X') {
                    root.Hash ^= Z.boxRand[i][j];
                }
            }
        }
        root.Hash ^= Z.playerRand[player.first][player.second];
        root.Hash ^= Z.scoreRand[scoreDelta + 1000];

        if(aHist.size() > 0) root.lastAct = getAct(aHist.back());
        if(aHist.size() > 1) root.prevAct = getAct(aHist[aHist.size() - 2]);
        root.value = heuristic(root, DEPTH);
    }
    char solve() {
        vector<State> beam;
        beam.push_back(root);

        State best = root;

        clock_t start = clock();
        for(int depth = 0; depth < DEPTH; depth++) {
            double elapsed = double(clock() - start) / CLOCKS_PER_SEC * 1000;
            if (elapsed > TIME_LIMIT_MS) break;
            // cerr << "depth: " << depth << endl;
            
            vector<State> nextBeam;
            unordered_set<long long> visited;

            for(auto& state : beam) {
                // cerr << "cur: " << state.firstPlan << " " << state.value << endl;
                double elapsed = double(clock() - start) / CLOCKS_PER_SEC * 1000;
                if (elapsed > TIME_LIMIT_MS) break;
                for(int d = 0; d <= 4; d++) {
                    double elapsed = double(clock() - start) / CLOCKS_PER_SEC * 1000;
                    if (elapsed > TIME_LIMIT_MS) break;
                    State ns = state;
                    if(ns.firstPlan.empty()) ns.firstPlan = string(1, dir[d]);
                    
                    bool ok = applyMove(ns, d);
                    if(!ok) continue;

                    int remaining = DEPTH - depth;
                    ns.value = heuristic(ns, remaining);

                    if(ns.value > best.value) best = ns;
                    // cout << "ROOT: " << endl << ns.firstPlan << " " << ns.value << endl;
                    // cerr << ns.firstPlan << " " << ns.value << endl;

                    if(visited.find(ns.Hash) == visited.end()) {
                        visited.insert(ns.Hash);
                        nextBeam.push_back(ns);
                    }
                }
                // cerr << "===" << endl;
            }
            sort(nextBeam.begin(), nextBeam.end(), [](const State& a, const State& b) {
                return a.value > b.value;
            });
            nextBeam.resize(min((int)nextBeam.size(), BEAM_W));
            swap(beam, nextBeam);
        }
        // cerr << "best: " << endl;
        // cerr << "player: " << best.player.first << " " << best.player.second << endl;
        // cerr << "goal: " << best.goal.first << " " << best.goal.second << endl;
        // cerr << "score: " << best.score << endl;
        // cerr << "lastAct: " << best.lastAct << endl;
        // cerr << "prevAct: " << best.prevAct << endl;
        // cerr << "lastPushed: " << best.lastPushed << endl;
        // cerr << "lastScoreDelta: " << best.lastScoreDelta << endl;
        // cerr << "firstPlan: " << best.firstPlan << endl;
        // cerr << "value: " << best.value << endl;
        
        if(best.firstPlan.empty()) return 'S';
        return best.firstPlan[0];
    }
private:
    ZobristHash Z;
    int N;
    pair<int, int> player, goal;
    pair<int, int> opp, oppGoal;
    vector<pair<int, int>> boxes;
    char grid[MAX_N][MAX_N];
    int distA[MAX_N][MAX_N], distB[MAX_N][MAX_N], dist[MAX_N][MAX_N];
    State root;

    bool applyMove(State &s, int d) {
        /**
        * @brief Modifies a state in-place by applying a move action.
        * 
        * Handles movement, static board boundaries, collision with walls or opponents,
        * and box pushing (including chain-pushes and scoring goals).
        * 
        * @param s The current state to modify.
        * @param d The action direction ID to apply.
        * @return True if the move is valid and successfully applied, False otherwise.
        */
        s.lastPushed = false;
        s.lastScoreDelta = 0;

        s.prevAct = s.lastAct;

        if(d == 4){
            s.lastAct = d;
            return true;
        }

        int px = s.player.first, py = s.player.second;
        int nx = px + dx[d], ny = py + dy[d];
        pair<int, int> ntemp = {nx, ny};
        if(!isInGrid(ntemp)) return false;

        if(grid[nx][ny] == '#' || grid[nx][ny] == 'A' || grid[nx][ny] == 'B' || (nx == opp.first && ny == opp.second)) return false;
        
        if(find(s.boxes.begin(), s.boxes.end(), ntemp) == s.boxes.end()) {
            s.Hash ^= Z.playerRand[px][py];
            s.player = {nx, ny};
            s.Hash ^= Z.playerRand[nx][ny];

            s.lastAct = d;
            return true;
        }
        // chain push
        int cx = nx, cy = ny;
        pair<int, int> firstBox = {nx, ny};
        pair<int, int> tail = {-1, -1};

        while(true){
            int tx = cx + dx[d], ty = cy + dy[d];
            pair<int, int> ttemp = {tx, ty};
            if(!isInGrid(ttemp)) return false;
            if(find(s.boxes.begin(), s.boxes.end(), ttemp) == s.boxes.end()) {
                tail = ttemp; 
                break; 
            }
            cx = tx; cy = ty;
        }

        if(tail == opp) return false;
        if(grid[tail.first][tail.second] == '#') return false;

        // push into goal => allowed, box disappears, score changes
        if(grid[tail.first][tail.second] == 'A' || grid[tail.first][tail.second] == 'B'){
            s.lastPushed = true;

            s.boxes.erase(find(s.boxes.begin(), s.boxes.end(), firstBox));

            int oldScore = s.score;
            if(grid[tail.first][tail.second] == 'A') {
                s.score += 1;
                s.lastScoreDelta = +1;
            }
            else {
                s.score -= 1;
                s.lastScoreDelta = -1;
            }
            s.Hash ^= Z.scoreRand[oldScore + 1000];
            s.Hash ^= Z.scoreRand[s.score + 1000];

            // player steps into firstBox
            s.Hash ^= Z.playerRand[px][py];
            s.player = firstBox;
            s.Hash ^= Z.playerRand[firstBox.first][firstBox.second];

            s.lastAct = d;
            return true;
        }


        // tail is empty '.' => shift: clear first, set tail
        s.lastPushed = true;

        s.Hash ^= Z.boxRand[firstBox.first][firstBox.second];
        s.boxes.erase(find(s.boxes.begin(), s.boxes.end(), firstBox));
        s.boxes.push_back(tail);
        sort(s.boxes.begin(), s.boxes.end()); // maintain set comparison ordering
        s.Hash ^= Z.boxRand[tail.first][tail.second];

        s.Hash ^= Z.playerRand[px][py];
        s.player = firstBox;
        s.Hash ^= Z.playerRand[firstBox.first][firstBox.second];

        s.lastAct = d;
        return true;
    }

    void bfs(pair<int, int> start, int dist[MAX_N][MAX_N]){
        for(int i=0;i<N;i++) for(int j=0;j<N;j++) dist[i][j] = -1;
        queue<pair<int, int>> q;
        q.push(start);
        dist[start.first][start.second] = 0;
        while(!q.empty()){
            pair<int, int> u = q.front();
            q.pop();
            for(int k=0;k<4;k++){
                int vx = u.first + dx[k], vy = u.second + dy[k];
                if(!isInGrid({vx,vy})) continue;
                if(grid[vx][vy] == '#' || grid[vx][vy] == 'A' || grid[vx][vy] == 'B' || grid[vx][vy] == 'b') continue;
                if(dist[vx][vy] == -1){
                    dist[vx][vy] = dist[u.first][u.second] + 1;
                    q.push({vx, vy});
                }
            }
        }
    }

    void precomputeDists(){
        if(goal.first != -1) bfs(goal, distA);
        if(oppGoal.first != -1) bfs(oppGoal, distB);
        if(player.first != -1) bfs(player, dist);
    }

    pair<int, int> bestBlockCellNearBGoal() {
        int gx = oppGoal.first, gy = oppGoal.second;
        pair<int, int> best = {-1, -1};
        int bestDist = 1e9;
        for(int k=0;k<4;k++){
            int nx = gx + dx[k], ny = gy + dy[k];
            if(!isInGrid({nx,ny})) continue;
            if(grid[nx][ny] == '#' || grid[nx][ny] == 'A' || grid[nx][ny] == 'B' || grid[nx][ny] == 'b') continue;

            int d = dist[nx][ny];
            if(d == -1) continue;

            if(d < bestDist){
                bestDist = d;
                best = {nx, ny};
            }
        }
        return best;
    }

    long long heuristic(State &s, int remainingTurns) {
        long long val = 0;

        // score dominates
        val += (long long)s.score * 20000000LL;

        // sum distances of boxes to A / B (static estimate)
        long long sA = 0, sB = 0;
        int mobility = 0;
        for(int i = 0; i < (int)s.boxes.size(); i++) {
            int x = s.boxes[i].first, y = s.boxes[i].second;
            int dA = distA[x][y];
            int dB = distB[x][y];

            if(dA == -1) dA = 2000; 
            if(dB == -1) dB = 2000; 
            sA += dA;
            sB += dB;
            for(int k = 0; k < 4; k++) {
                int px = x - dx[k], py = y - dy[k];
                if(!isInGrid({px, py})) continue;
                if(grid[px][py] != '.' && grid[px][py] != 'a') continue;

                int cx = x, cy = y;
                pair<int, int> tail = {-1, -1};
                while(true){
                    int tx = cx + dx[k], ty = cy + dy[k];
                    if(!isInGrid({tx, ty})) {
                        tail = {-1, -1};
                        break; 
                    }
                    bool isBox=false;
                    for(int j=0;j<(int)s.boxes.size();j++) if(s.boxes[j].first==tx && s.boxes[j].second==ty) isBox=true;
                    if(!isBox) {
                        tail = {tx, ty};
                        break;
                    }
                    cx=tx; cy=ty;
                }
                if(tail.first == -1) continue;
                if(tail == opp) continue;
                if(tail == oppGoal) continue;
                if(grid[tail.first][tail.second] == '#') continue;
                mobility++;
            }
        }
        
        val -= sA * 1500LL;
        val -= sB * 40LL;
        val += mobility * 200LL;

        // prefer being closer to some box (reduce pure wandering)
        int px = s.player.first, py = s.player.second;
        int bestNear = 2000;
        for(int i = 0; i < (int)s.boxes.size(); i++) {
            int x = s.boxes[i].first, y = s.boxes[i].second;
            bestNear = min(bestNear, abs(x-px)+abs(y-py));
        }
        val -= (long long)bestNear * 200LL;

        // urgency
        val += (long long)(DEPTH - remainingTurns) * 50LL;

        // When leading, strongly like sitting on block cell near B-goal
        pair<int, int> blockCell = {-1, -1};
        bool holdingBlock = false;
        if(s.score > 0 && oppGoal.first != -1){
            blockCell = bestBlockCellNearBGoal();
            if(blockCell.first != -1 && s.player == blockCell) holdingBlock = true;

            // also prefer being adjacent to B-goal generally (soft)
            int gx = oppGoal.first, gy = oppGoal.second;
            int distMan = abs(s.player.first - gx) + abs(s.player.second - gy);
            val += (long long)max(0, 6 - distMan) * 2500LL;

            if(holdingBlock){
                val += 20000; // big reward for locking
            }
        }

        // anti-stall: only punish standing still if NOT holding the block
        if(s.lastAct==4 && !holdingBlock) val -= 300;
        if(s.lastAct==4 && holdingBlock)  val += 1000;

        // Anti-oscillation: punish immediate back-and-forth if no progress
        if(!s.lastPushed && s.lastScoreDelta==0 && isOppAct(s.lastAct, s.prevAct)){
            val -= 12000;
        }

        return val;
    }

    bool isInGrid(pair<int, int> pos) {
        return (0 <= min(pos.first, pos.second) && max(pos.first, pos.second) < N);
    }
};

/**
 * @brief Entry point for the bot executable.
 * 
 * Reads the current game state from standard input, initializes the solver,
 * and outputs the calculated best move to standard output.
 * 
 * @return 0 on successful execution.
 */
int main() {
    ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
    int N, T_cur, T_total, playerScore, oppScore;
    cin >> N >> T_cur >> T_total;
    vector<vector<char>> board(N, vector<char>(N));
    for(int i = 0; i < N; i++) for(int j = 0; j < N; j++)
        cin >> board[i][j];
    vector<char> playerHist(max(0, T_cur - 1)), oppHist(max(0, T_cur - 1)), playerMoved(max(0, T_cur - 1)), oppMoved(max(0, T_cur - 1));
    for(int i = 0; i < T_cur - 1; i++)
        cin >> playerHist[i] >> oppHist[i] >> playerMoved[i] >> oppMoved[i];
    cin >> playerScore >> oppScore;

    BeamSearch solver(board, playerHist, playerScore - oppScore);

    char ans = solver.solve();
    cout << ans;
    return 0;
}
/*
16 1 200
#.....X.##.#####
#..#.#.....a..##
#..#.##X##.##.##
......X.##..#.##
#.....X..#....##
#.#X.##.##.#####
#X............X.
###.A##.#XX..X..
###.B##.#XX..X..
#X............X.
#.#X.##.##.#####
#.....X..#....##
......X.##..#.##
#..#.##X##.##.##
#..#.#.....b..##
#.....X.##.#####
0 0

cur: L -31560
L -31210
L -31210
:::2 2 7
::: died
:::liem
L -33170
L -31410
L -31510
===
depth: 8
cur: L -27490
:::0 7 10
::: died
*/