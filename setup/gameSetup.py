"""
Game Configuration and Initialization Module

This module initializes Pygame, configures game constants (grid size, tiles, colors),
loads graphical assets, and provides the map generation function to load or generate
the 2P Sokoban puzzle maps.
"""

import pygame, sys, random, os, subprocess

# Grid and rendering constants
tileSize, gridSize, padding, textSize = 40, 16, 12, 50
density, boxCount = 0.1, 10
offset = 2 * padding + textSize
xSize = tileSize * gridSize + 2 * padding
ySize = tileSize * gridSize + 3 * padding + textSize
map_padding_x = padding
map_padding_y = offset

# Color definitions
P1_COLOR = (220, 60, 60)
P2_COLOR = (60, 140, 220)
P1_READY = (180, 90, 90)
P2_READY = (90, 140, 180)

whiteColor = (240, 240, 240)
blackColor = (0, 0, 0)
grayColor = (200, 200, 200)

# Asset loading and scaling
FONT = "graphics/Silkscreen.ttf"

def load_assets():
    """
    Load and rescale all graphical assets based on the current tileSize.
    
    This updates the global image objects dynamically whenever the grid size 
    forces a scale readjustment for visual responsiveness.
    """
    global playerOneImg, playerTwoImg, portalOneImg, portalTwoImg, boxImg, tileImg, wallImg
    playerOneImg = pygame.transform.smoothscale(pygame.image.load("graphics/player-1.png"), (tileSize, tileSize))
    playerTwoImg = pygame.transform.smoothscale(pygame.image.load("graphics/player-2.png"), (tileSize, tileSize))
    portalOneImg = pygame.transform.smoothscale(pygame.image.load("graphics/portal-1.png"), (tileSize, tileSize))
    portalTwoImg = pygame.transform.smoothscale(pygame.image.load("graphics/portal-2.png"), (tileSize, tileSize))
    boxImg = pygame.transform.smoothscale(pygame.image.load("graphics/box.png"), (tileSize, tileSize))
    tileImg = pygame.transform.smoothscale(pygame.image.load("graphics/tile.png"), (tileSize, tileSize))
    wallImg = pygame.transform.smoothscale(pygame.image.load("graphics/wall.png"), (tileSize, tileSize))

load_assets()

# Initial random grid generation (placeholder before actual map generation)
grid = [[1 if random.random() < density else 0 for _ in range(gridSize)] for _ in range(gridSize)]
whiteCells = [(x, y) for y in range(gridSize) for x in range(gridSize) if grid[y][x] == 0]

# Shuffle available cells for random entity placements
random.shuffle(whiteCells)

# Assign player starting positions
playerOnePos, playerTwoPos = whiteCells[0], whiteCells[1]
whiteCells = whiteCells[2:]

# Assign portal positions
portalOne, portalTwo = whiteCells[0], whiteCells[1]
whiteCells = whiteCells[2:]

# Assign box positions
boxes = whiteCells[:boxCount]
whiteCells = whiteCells[boxCount:]

# Map caching
last_rawMaze = []


def setMapSize(N = 16):
    """
    Dynamically reconfigure the game grid and UI parameters.
    
    Automatically scales the `tileSize` according to the grid dimension `N` 
    to ensure the entire map elegantly fits within readable boundaries, recalibrates 
    the overall display coordinates, applies the necessary margin paddings, and 
    prompts the main application window to resize securely.
    
    Args:
        N (int): The dimensional size of the map (default 16).
    """
    global tileSize, gridSize, padding, textSize, offset, xSize, ySize, screen
    global map_padding_x, map_padding_y
    gridSize = N
    if N == 12:
        tileSize = 50
    elif N == 24:
        tileSize = 30
    else:
        tileSize = 40
        
    offset = 2 * padding + textSize
    grid_pixel_size = tileSize * gridSize
    
    # We want a minimum window size so InitScreen fits
    min_w = 664
    min_h = 550
    xSize = max(min_w, grid_pixel_size + 2 * padding)
    ySize = max(min_h, grid_pixel_size + 3 * padding + textSize)
    
    map_padding_x = (xSize - grid_pixel_size) // 2
    map_padding_y = offset
    
    load_assets()
    if 'screen' in globals():
        screen = pygame.display.set_mode((xSize, ySize))

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
    parses the generated output to populate the game grid and entity positions.
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
        FileNotFoundError: If the map generator executable cannot be found.
        IOError: If map generation output cannot be read.
    """
    global grid, whiteCells, boxes, playerOnePos, playerTwoPos, portalOne, portalTwo
    global gridSize, last_rawMaze

    base_dir = os.path.dirname(__file__)

    if generate:
        exe_path = _resolve_mapgen_exe(base_dir)

        # Map generation input parameters
        input_lines = f"{N} {MODE}\n"

        # Execute map generation binary
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
        process.wait()
        
        # Read the resulting raw map structure from stdout
        rawMaze = [line for line in out.splitlines() if line.strip()]
        last_rawMaze = rawMaze
    else:
        if 'last_rawMaze' in globals() and last_rawMaze:
            rawMaze = last_rawMaze
        else:
            # Fallback empty map if reset is called before any generation
            rawMaze = ["." * gridSize for _ in range(gridSize)]

    # Parse map characters to grid state arrays
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


# Perform initial map generation setup
getMap(generate=True, N=16, MODE="SEP")

# Global Pygame and session initialization
pygame.init()
screen = pygame.display.set_mode((xSize, ySize))
pygame.display.set_caption("2P Sokoban")
clock = pygame.time.Clock()

# Session tracking variables
score = [0, 0]
last_score_turn = [0, 0]
playerMove = ["", ""]
playerDidMove = ["", ""]
turn = 1
