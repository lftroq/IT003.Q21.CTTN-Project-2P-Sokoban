"""
Headless Sokoban Bot Simulator.

This module provides a command-line interface and programmatic API to run
automated matches between two Sokoban bots without rendering the graphical
user interface. It forces the SDL dummy video driver to prevent window creation.
"""
import os
# Must set dummy video driver before importing pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import argparse
import time

from setup import gameSetup as gs
import game
import core.config as config

def key_to_d(key):
    """
    Convert a string direction key into 2D coordinate deltas.

    Args:
        key (str): The direction key ('L', 'R', 'U', 'D').

    Returns:
        tuple[int, int]: The corresponding (dx, dy) directional deltas.
    """
    if key == "L": return -1, 0
    if key == "R": return 1, 0
    if key == "U": return 0, -1
    if key == "D": return 0, 1
    return 0, 0

def run_match(bot1, bot2, move_limit=200, map_mode="SYM", map_size=16):
    """
    Simulate a single headless match between two bots.

    This function initializes the game environment, sets the configuration
    parameters, and rapidly executes turns until a terminal game state is reached.

    Args:
        bot1 (str): Executable name or path for Player 1's bot.
        bot2 (str): Executable name or path for Player 2's bot.
        move_limit (int, optional): Maximum allowed moves per game. Defaults to 200.
        map_mode (str, optional): The map generation mode ("SYM", "SEP", "NON"). Defaults to "SYM".
        map_size (int, optional): The dimension of the generated map. Defaults to 16.

    Returns:
        str: The result of the match (e.g., 'P1 Wins!', 'P2 Wins!', 'Draw!').
    """
    # Set global settings in config module
    config.move_limit = move_limit
    config.map_mode = map_mode
    config.map_size = map_size
    config.filename = [bot1, bot2]
    
    # Generate new map and reset state
    game.reset_game_state(True)
    
    gs_screen = game.GameScreen()
    
    # Simulate match until game over
    while not gs_screen.game_over:
        key1 = gs_screen._get_key(False)
        key2 = gs_screen._get_key(True)
        
        # Enforce valid keys
        if key1 not in ["U", "D", "L", "R"]: key1 = "S"
        if key2 not in ["U", "D", "L", "R"]: key2 = "S"

        dx1, dy1 = key_to_d(key1)
        dx2, dy2 = key_to_d(key2)

        # Set game screen ready states manually
        gs_screen.dxOne, gs_screen.dyOne, gs_screen.keyOne = dx1, dy1, key1
        gs_screen.dxTwo, gs_screen.dyTwo, gs_screen.keyTwo = dx2, dy2, key2
        gs_screen.ready = 3
        
        # Resolve the turn immediately
        gs_screen._resolve_turn_if_ready()

        if gs_screen.game_over:
            break

    return gs_screen.game_result_text

def run_simulations(bot1, bot2, runs, move_limit=200, map_mode="SYM", map_size=16):
    """
    Run multiple simulated matches between two bots and aggregate the results.

    Args:
        bot1 (str): Executable name or path for Player 1's bot.
        bot2 (str): Executable name or path for Player 2's bot.
        runs (int): The total number of matches to simulate.
        move_limit (int, optional): Maximum allowed moves per game. Defaults to 200.
        map_mode (str, optional): The map generation mode ("SYM", "SEP", "NON"). Defaults to "SYM".
        map_size (int, optional): The dimension of the generated map. Defaults to 16.

    Returns:
        None: Results and elapsed time are printed directly to standard output.
    """
    print(f"========== SOKOBAN BOT SIMULATOR ==========")
    print(f"P1 Bot: {bot1}")
    print(f"P2 Bot: {bot2}")
    print(f"Matches: {runs} | Move Limit: {move_limit} | Mode: {map_mode} | Size: {map_size}")
    print("-------------------------------------------")
    
    results = {"P1 Wins!": 0, "P2 Wins!": 0, "Draw!": 0}
    start_time = time.time()
    
    for i in range(1, runs + 1):
        result = run_match(bot1, bot2, move_limit, map_mode, map_size)
        # Handle unexpected result keys
        if result not in results:
            results[result] = 0
        results[result] += 1
        print(f"Match {i:03d}/{runs} -> {result}")
        
    elapsed = time.time() - start_time
    
    print("================ RESULTS =================")
    print(f"P1 ({bot1}) Wins: {results.get('P1 Wins!', 0)}")
    print(f"P2 ({bot2}) Wins: {results.get('P2 Wins!', 0)}")
    print(f"Draws                 : {results.get('Draw!', 0)}")
    print(f"Total time elapsed    : {elapsed:.2f} seconds")
    print("==========================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Headless 2P Sokoban Bot Simulator")
    parser.add_argument("--p1", type=str, default="beam_search.exe", help="Executable name for Player 1")
    parser.add_argument("--p2", type=str, default="lftroq_v2.exe", help="Executable name for Player 2")
    parser.add_argument("--runs", type=int, default=50, help="Number of simulation runs")
    parser.add_argument("--limit", type=int, default=100, help="Move limit per game")
    parser.add_argument("--mode", type=str, default="SYM", choices=["SYM", "SEP", "NON"], help="Map generation mode")
    parser.add_argument("--size", type=int, default=16, choices=[12, 16, 24], help="Map size dimension (N)")
    
    args = parser.parse_args()
    
    run_simulations(args.p1, args.p2, args.runs, args.limit, args.mode, args.size)
