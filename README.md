# IT003.Q21.CTTN-Project-2P-Sokoban

A two-player strategy game, where players push boxes to theỉr portal to score.

This project consists of AI agents, a map generator, and many modes and features.

---

## Gameplay

Two players will control their characters to move on the map simultaneously.

Push the boxes into:
- Portal 1 (marked in Red by default) to score for Player 1.
- Portal 2 (marked in Blue by default) to score for Player 2
- Game ends when it reaches the move limit.
- 
---

## Controls

### Player 1 (marked in Red by default):
- `W A S D`

### Player 2 (marked in Blue by default):
- `← ↑ → ↓`

---

## AI agents

This game supports bots with multiple difficulties via `.exe` files:

Default bots:
| Level | File      | Algorithm |
|-------|-----------|-----------|
| EASY  | TBD | TBD |
| MED   | TBD | TBD |
| HARD  | TBD | TBD |

Bots are saved in the `interactor` directory and interact via the module `interactor/interactor.py`.

---

## Map System

The map is generated with `setup/mapGen.exe` (C++), using weighted random.

### Map mode

| Mode | Code | Details |
|------|------|------|
| Separate | `SEP` | Two players and goals are separated. It is also ensured that the map is symmetrical. |
| Symmetrical | `SYM` | The map is symmetrical. |
| Default | `DEF` | The map is generated fully randomly |

Currently, the game only supports `N = 16`, where `N` is the map size.

### Map structure (map.txt)

The map is decoded with the following rules:
- `.` = Empty cell.
- `#` = Wall/obstacle cell.
- `X` = Box.
- `A` = Portal P1.
- `B` = Portal P2.
- `a` = Player 1.
- `b` = Player 2.

---

## Game Mechanics

The game occurs in `T` turns, where the turns are simultaneously resolved. Players push a box into the goal to score.

Detailed interaction:
- The player can push a box by moving into the box cell. The box is pushed toward the player's opposite direction by a cell.
- Multiple boxes can be pushed at once (Chain push).
- The player cannot push or move into obstacle cells.
- The player cannot move into the portal, but can push a box into the portal.
- When a box is moved into the goal, the player who owns that portal will receive a point.

Special interaction:
- Both players cannot stand in a single cell. If they move into the same cell simultaneously, both players' actions fail.
- Both players cannot simultaneously push a box.
- A player can still push a box into the opponent's portal. But the other player receives a point.
- If a player pushes boxes into a cell where the other player intended to move into, the opponent is prioritized, and the push action fails.
- If a player pushes boxes into a cell where the other player stands, but at the same time the opponent moves away, the push action still succeeds.
- Two players can swap their positions with each other if they are standing next to each other and both move toward the other’s direction.

---

## User Interface

The UI is implemented using Pygame.

The game's asset is stored in `graphics` and loaded in `setup/gameSetup.py`.

The game has three screens.
### Menu
- Start game.
### Game init
Initialize the game, choose game settings:
- Human or bot for each player.
- Difficulty of the bots if a bot is chosen.
- Set move limit.
- Set map mode (SEP / SYM / DEF).
### Game screen
Display:
- Current game board.
- Two players' scores.
- Utility buttons.

---

## Run
```bash
cd interactor
g++ mapGen.cpp -o mapGen
cd ..
python game.py
```

---

## Directory tree

```
│
├── game.py
├── setup/
│   ├── gameSetup.py
│   ├── mapGen (.cpp and .exe)
│   └── maze.txt
├── interactor/
│   ├── bots (.cpp and .exe)
│   └── interactor.py
├── graphics/
│   ├── silkscreen.ttf
│   ├── player-1.png
│   ├── player-2.png
│   ├── box.png
│   ├── tile.png
│   ├── wall.png
│   ├── portal-1.png
│   └── portal-2.png
```

## AI Development Support

This project allows users to implement their own bots to compete in the game.

---

### Bot Input

At each turn, your bot control player `a` and receives the current game state in standard input with the following format:

#### Input
- The first line contains three integers `N`, `T_cur`, and `T_max`, which are the size of the map, current turn, and move limit.
- In the `N` following lines, each line contains `N` characters describing the map.
- In the `T_cur - 1` following lines, each line contains two characters `playerHist`, `oppHist` describing the game history, and two integers `playerDidMove`, `oppDidMove`, which are either 0/1 describing if the action succeeded.
- The last line contains two integers `playerScore` and `oppScore`, which are the player's score and the opponent's score.

#### Output
- A single character `U/D/L/R` describing the bot's choice for the next move.

### Integrating the bot

The bot should be implemented and compiled into an `.exe` file and placed into the `interactor` directory.

Register in `game.py`:
```python
BOT_MODELS = {
    "EASY": "your_bot_1.exe",
    "MED": "your_bot_2.exe",
    "HARD": "your_bot_3.exe",
}
```

### Algorithm Ideas

You can experiment with:
- BFS / DFS (basic pathfinding).
- Dijkstra / A*.
- Beam search with heuristic evaluation.
- Greedy strategies.
- Minimax (adversarial planning).
- Alpha-Beta pruning.
- Monte Carlo Tree Search (MCTS).
- Reinforcement Learning (advanced).

### Important Notes
- The game uses simultaneous turns, so consider predicting opponent actions.
- Invalid moves (e.g., walking into walls) will be ignored.
- Box pushing must follow valid rules.
- Keep response time fast to avoid timeouts.

## Known issues
- The default map mode may cause unfairness.
- The portal may be separated from the players.
- UI is not responsive to all sizes.

## Future improvement
- Preview map in GameInit screen.
- Choose custom size (8 / 16 / 24).
- Utility buttons, replay system.
- Online multiplayer.
- Better bots' algorithm.
