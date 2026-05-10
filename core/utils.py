"""
Utility Functions.

This module offers helper functions for drawing text and resetting the global
game state.
"""
import pygame
from setup import gameSetup as gs
import core.config as config

def _draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font, x: int, y: int, color=(255, 255, 255)):
    """Render and blit text at specified position."""
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    surface.blit(img, rect)

def reset_game_state(generate: bool = False):
    """
    Reset game state including map, scores, and move history.
    
    Args:
        generate: If True, generate new map; if False, reuse current map
    """
    gs.setMapSize(config.map_size)
    gs.getMap(generate, N=config.map_size, MODE=config.map_mode)
    gs.score = [0, 0]
    gs.last_score_turn = [0, 0]
    gs.playerMove = ["", ""]
    gs.playerDidMove = ["", ""]
    gs.turn = 1
