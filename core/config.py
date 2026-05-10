"""
Global Configuration and Settings.

This module defines default game configuration variables, keyboard mappings,
and bot execution details used across the game application.
"""
import pygame

import os

# Default game configuration values
move_limit = 200
map_mode = "SYM"
map_size = 16

playerOneInteract = True
playerTwoInteract = False
filename = ["lftroq_v2", "lftroq_v2"]

EXT = ".exe" if os.name == "nt" else ""
BOT_MODELS = {
    "EASY": f"lftroq{EXT}",
    "MED": f"lftroq_v2{EXT}",
    "HARD": f"beam_search{EXT}",
}

# Keyboard mappings for each player
P1_KEYS = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
P2_KEYS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]

P1_MAP = {pygame.K_w: "U", pygame.K_s: "D", pygame.K_a: "L", pygame.K_d: "R"}
P2_MAP = {pygame.K_LEFT: "L", pygame.K_RIGHT: "R", pygame.K_UP: "U", pygame.K_DOWN: "D"}

BOT_DELAY_MS = 250
