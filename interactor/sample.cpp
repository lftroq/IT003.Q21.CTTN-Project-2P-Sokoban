/**
 * @file sample.cpp
 * @brief Simple random-move bot for Sokoban.
 * 
 * This executable reads the game state from standard input and outputs a random
 * valid move ('U', 'L', 'D', 'R', or 'S'). It serves as a baseline or testing bot.
 */
#include <bits/stdc++.h>
using namespace std;

const char dir[] = {'U', 'L', 'D', 'R', 'S'};

mt19937_64 rng(chrono::steady_clock::now().time_since_epoch().count());

/**
 * @brief Entry point for the sample bot.
 * 
 * Reads grid size, turn limits, the maze state, and player histories from stdin.
 * Then randomly selects and prints a single move character to stdout.
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

    char ans = dir[rng() % 5];
    cout << ans;
    return 0;
}