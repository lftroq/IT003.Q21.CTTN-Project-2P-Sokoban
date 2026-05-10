"""
Main Menu Screen Module.

This module provides the MenuScreen class that displays the game's title
and main navigation buttons ('PLAY', 'HOW TO PLAY').
"""
import pygame
from setup import gameSetup as gs
from core.utils import _draw_text

class MenuScreen:
    """Main menu with Play and Tutorial buttons."""

    def __init__(self):
        """Initialize menu screen with fonts and button layout."""
        self.title_font = pygame.font.Font(gs.FONT, 42)
        self.btn_font = pygame.font.Font(gs.FONT, 28)

        btn_w, btn_h = 220, 70
        self.play_rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.play_rect.center = (gs.xSize // 2, gs.ySize // 2 + 10)

        self.tutorial_rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.tutorial_rect.center = (gs.xSize // 2, gs.ySize // 2 + 100)

        self.hint_font = pygame.font.Font(gs.FONT, 16)

    def draw(self):
        """Render menu screen with title and buttons."""
        gs.screen.fill((0, 0, 0))

        _draw_text(gs.screen, "2P SOKOBAN", self.title_font, gs.xSize // 2, gs.ySize // 2 - 80)

        mx, my = pygame.mouse.get_pos()
        
        # Hover handling
        hover_play = self.play_rect.collidepoint((mx, my))
        hover_tut = self.tutorial_rect.collidepoint((mx, my))

        # Play Button
        bg_play = (220, 220, 220) if hover_play else (30, 30, 30)
        fg_play = (20, 20, 20) if hover_play else (255, 255, 255)
        pygame.draw.rect(gs.screen, bg_play, self.play_rect, border_radius=8)
        pygame.draw.rect(gs.screen, (200, 200, 200), self.play_rect, 2, border_radius=8)
        _draw_text(gs.screen, "PLAY", self.btn_font, self.play_rect.centerx, self.play_rect.centery, color=fg_play)

        # Tutorial Button
        bg_tut = (220, 220, 220) if hover_tut else (30, 30, 30)
        fg_tut = (20, 20, 20) if hover_tut else (255, 255, 255)
        pygame.draw.rect(gs.screen, bg_tut, self.tutorial_rect, border_radius=8)
        pygame.draw.rect(gs.screen, (200, 200, 200), self.tutorial_rect, 2, border_radius=8)
        _draw_text(gs.screen, "HOW TO PLAY", self.btn_font, self.tutorial_rect.centerx, self.tutorial_rect.centery, color=fg_tut)

        _draw_text(
            gs.screen,
            "Click Play or press ENTER",
            self.hint_font,
            gs.xSize // 2,
            self.tutorial_rect.bottom + 28,
            color=(160, 160, 160),
        )

    def handle_event(self, event: pygame.event.Event) -> str:
        """
        Handle menu events.
        
        Returns:
            "PLAY", "TUTORIAL", or None
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_rect.collidepoint(event.pos):
                return "PLAY"
            if self.tutorial_rect.collidepoint(event.pos):
                return "TUTORIAL"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return "PLAY"
        return None
