"""Game initialization module for 2-player Sokoban.

Handles GUI setup, map generation, and game state initialization including:
- Display and rendering configuration
- Game asset loading
- Map generation and parsing
- Player, portal, and box positioning
- Game state variables
"""
# Game initialization module for 2-player Sokoban
# Handles GUI setup, map generation, and game state initialization

import pygame, sys, random, os, subprocess

# Display and grid settings
tileSize, gridSize, padding, textSize = 40, 16, 12, 50
density, boxCount = 0.1, 10
offset = 2 * padding + textSize
xSize = tileSize * gridSize + 2 * padding
ySize = tileSize * gridSize + 3 * padding + textSize

# Color palette
whiteColor = (240, 240, 240)
blackColor = (0, 0, 0)
grayColor = (200, 200, 200)

# Game assets
playerOneImg = pygame.transform.smoothscale(pygame.image.load("graphics/player-1.png"), (tileSize, tileSize))
playerTwoImg = pygame.transform.smoothscale(pygame.image.load("graphics/player-2.png"), (tileSize, tileSize))
portalOneImg = pygame.transform.smoothscale(pygame.image.load("graphics/portal-1.png"), (tileSize, tileSize))
portalTwoImg = pygame.transform.smoothscale(pygame.image.load("graphics/portal-2.png"), (tileSize, tileSize))
boxImg = pygame.transform.smoothscale(pygame.image.load("graphics/box.png"), (tileSize, tileSize))
tileImg = pygame.transform.smoothscale(pygame.image.load("graphics/tile.png"), (tileSize, tileSize))
wallImg = pygame.transform.smoothscale(pygame.image.load("graphics/wall.png"), (tileSize, tileSize))

# Generate initial game grid
grid = [[1 if random.random() < density else 0 for _ in range(gridSize)] for _ in range(gridSize)]
whiteCells = [(x, y) for y in range(gridSize) for x in range(gridSize) if grid[y][x] == 0]

# Position player one and two in random white cells
random.shuffle(whiteCells)
playerOnePos, playerTwoPos = whiteCells[0], whiteCells[1]
whiteCells = whiteCells[2:]

# Assign portal positions
portalOne, portalTwo = whiteCells[0], whiteCells[1]
whiteCells = whiteCells[2:]

# Assign box positions
boxes = whiteCells[:boxCount]
whiteCells = whiteCells[boxCount:]


def _resolve_mapgen_exe(base_dir: str) -> str:
    """Locate the map generator executable.
    
    Searches for the map generator executable in platform-specific order.
    First checks for mapGen.exe (Windows), then mapGen (Linux/Unix).
    
    Args:
        base_dir (str): Base directory to search for the executable.
    
    Returns:
        str: Absolute path to the existing executable, or path to mapGen
             if neither exists (caller responsible for error handling).
    """
    cand1 = os.path.join(base_dir, "mapGen.exe")
    cand2 = os.path.join(base_dir, "mapGen")
    return cand1 if os.path.exists(cand1) else cand2


def getMap(generate: bool = False, N: int = 16, MODE: str = "SEP"):
    """Load or generate a game map and initialize game state.
    
    Optionally runs the map generator to create a maze configuration, then
    parses the maze.txt file to populate the game grid and entity positions.
    Updates global variables for grid, player positions, portals, and boxes.
    
    Supported map symbols:
        '#': Wall
        '.': Walkable tile
        'X': Box
        'A': Portal 1
        'B': Portal 2
        'a': Player 1 starting position
        'b': Player 2 starting position
    
    Args:
        generate (bool): Whether to run the map generator. Defaults to False.
        N (int): Map size (typically 16). Defaults to 16.
        MODE (str): Generation mode - 'SEP' (separate), 'DEF' (default), or 'SYM' (symmetric).
                   Defaults to 'SEP'.
    
    Raises:
        FileNotFoundError: If maze.txt cannot be found.
        IOError: If maze.txt cannot be read.
    """
    global grid, whiteCells, boxes, playerOnePos, playerTwoPos, portalOne, portalTwo
    global gridSize

    base_dir = os.path.dirname(__file__)

    if generate:
        exe_path = _resolve_mapgen_exe(base_dir)
        input_lines = f"{N} {MODE}\n"

        process = subprocess.Popen(
            [exe_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=base_dir,
            bufsize=1,
        )
        out, err = process.communicate(input=input_lines)
        print(out, err)
        process.wait()

    txt_path = os.path.join(base_dir, "maze.txt")
    with open(txt_path, "r", encoding="utf-8") as f:
        rawMaze = f.readlines()

    grid, whiteCells, boxes = [], [], []
    for i in range(gridSize):
        curGrid = []
        for j in range(gridSize):
            ch = rawMaze[i][j]
            curGrid.append(1 if ch == "#" else 0)

            if ch == ".":
                whiteCells.append((j, i))
            elif ch == "X":
                boxes.append((j, i))
            elif ch == "A":
                portalOne = (j, i)
            elif ch == "B":
                portalTwo = (j, i)
            elif ch == "a":
                playerOnePos = (j, i)
            elif ch == "b":
                playerTwoPos = (j, i)

        grid.append(curGrid)


# Start the game
getMap(generate=True, N=16, MODE="SEP")

pygame.init()
screen = pygame.display.set_mode((xSize, ySize))
pygame.display.set_caption("2P Sokoban")
clock = pygame.time.Clock()
score = [0, 0]
playerMove = ["", ""]
playerDidMove = ["", ""]
turn = 1
