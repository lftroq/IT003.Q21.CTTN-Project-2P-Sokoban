"""
Tutorial Screen Module.

This module provides the TutorialScreen class, which displays game rules,
mechanics, and controls using a scrollable text interface.
"""
import pygame
from setup import gameSetup as gs
from core.utils import _draw_text
from core.ui_button import UIButton

def wrap_text(text: str, font: pygame.font.Font, max_width: int):
    """Wrap text to fit within a given width."""
    if not text:
        return []
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines

class TutorialScreen:
    """Screen displaying game rules, controls, and specific mechanics."""

    def __init__(self):
        """Initialize tutorial screen with text content and scrolling logic."""
        self.title_font = pygame.font.Font(gs.FONT, 34)
        self.header_font = pygame.font.Font(gs.FONT, 20)
        self.text_font = pygame.font.Font(gs.FONT, 16)
        
        btn_w, btn_h = 140, 50
        self.btn_back = UIButton(pygame.Rect(gs.xSize // 2 - btn_w // 2, gs.ySize - 80, btn_w, btn_h), "BACK")
        
        # Content remains the exact same, but we will dynamically wrap it
        self.raw_instructions = [
            ("OBJECTIVE", self.header_font, (255, 255, 100)),
            ("Push boxes into your designated portal to score points.", self.text_font, (200, 200, 200)),
            ("The game ends when the move limit is reached. The player with the highest score wins. In a tie, the first player to score wins.", self.text_font, (200, 200, 200)),
            ("", self.text_font, (0,0,0)),  # Spacer
            ("CONTROLS AND IDENTIFICATION", self.header_font, (255, 255, 100)),
            ("Player 1 (Red Character): W, A, S, D", self.text_font, (255, 90, 90)),
            ("Player 2 (Blue Character): Arrow Keys (Up, Down, Left, Right)", self.text_font, (90, 160, 255)),
            ("", self.text_font, (0,0,0)),
            ("CHAIN PUSH MECHANIC", self.header_font, (255, 255, 100)),
            ("Unlike regular Sokoban, you can push MULTIPLE boxes at once in a straight line, as long as there is an empty space at the end of the line.", self.text_font, (200, 200, 200)),
            ("Use this mechanic to block opponents or score efficiently.", self.text_font, (200, 200, 200)),
            ("", self.text_font, (0,0,0)),
            ("SIMULTANEOUS TURNS AND SPECIAL INTERACTIONS", self.header_font, (255, 255, 100)),
            ("Both players input their moves, and they resolve simultaneously.", self.text_font, (200, 200, 200)),
            ("If both players try to enter the same cell or push the same box, the moves will conflict and be cancelled out.", self.text_font, (200, 200, 200)),
            ("A player can still push a box into opponent's goal. However, the opponent's score will increase instead. ", self.text_font, (200, 200, 200)),
            ("If a player push a box into the cell that the opponent is also moving into, the opponent's move will succeed and the player's move will be cancelled out", self.text_font, (200, 200, 200)),
            ("If a player push a box into the cell that the opponent is also standing, but in that turn the opponent move, both moves still succeed.", self.text_font, (200, 200, 200)),
            ("If two players standing beside and move to each other's direction, their position swap.", self.text_font, (200, 200, 200)),
            ("", self.text_font, (0,0,0)),
        ]

        self.scroll_y = 0
        self.max_scroll = 0
        self.line_spacing = 30
        
        # Dynamic layout: column smaller than full screen
        self.max_col_width = min(600, gs.xSize - 120) 

        # Pre-process word wrapping
        self.rendered_lines = []
        for text, font, color in self.raw_instructions:
            if text == "":
                self.rendered_lines.append(("", font, color))
            else:
                wrapped = wrap_text(text, font, self.max_col_width)
                for line in wrapped:
                    self.rendered_lines.append((line, font, color))

        # Calculate max scrolling
        total_height = len(self.rendered_lines) * self.line_spacing
        visible_height = gs.ySize - 200 # Leave room for header and back button
        if total_height > visible_height:
            self.max_scroll = visible_height - total_height
        else:
            self.max_scroll = 0

    def draw(self):
        """Render the tutorial screen."""
        gs.screen.fill((25, 25, 25))
        _draw_text(gs.screen, "HOW TO PLAY", self.title_font, gs.xSize // 2, 40)
        
        # Apply Clipping Rect so text doesn't overlap header or footer
        clip_rect = pygame.Rect(0, 80, gs.xSize, gs.ySize - 180)
        gs.screen.set_clip(clip_rect)

        start_y = 100 + self.scroll_y
        for text, font, color in self.rendered_lines:
            if text:
                # Basic culling
                if 60 < start_y < gs.ySize - 80:
                    _draw_text(gs.screen, text, font, gs.xSize // 2, start_y, color)
            start_y += self.line_spacing

        # Clear clip mask
        gs.screen.set_clip(None)
        
        # Draw scroll indicator if scrollable
        if self.max_scroll < 0:
            scroll_progress = self.scroll_y / self.max_scroll
            bar_height = 100
            bar_y = 100 + (gs.ySize - 280) * scroll_progress
            pygame.draw.rect(gs.screen, (100, 100, 100), (gs.xSize - 40, 100, 6, gs.ySize - 200), border_radius=3)
            pygame.draw.rect(gs.screen, (200, 200, 200), (gs.xSize - 40, bar_y, 6, bar_height), border_radius=3)

        mx, my = pygame.mouse.get_pos()
        self.btn_back.draw(gs.screen, self.header_font, hovered=self.btn_back.hit((mx, my)))
        
    def handle_event(self, event: pygame.event.Event):
        """Handle interactions for navigating back and scrolling."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "BACK"
            elif event.key == pygame.K_UP:
                self.scroll_y += 40
            elif event.key == pygame.K_DOWN:
                self.scroll_y -= 40

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.btn_back.hit(event.pos):
                    return "BACK"
            elif event.button == 4: # Scroll Up
                self.scroll_y += 30
            elif event.button == 5: # Scroll Down
                self.scroll_y -= 30
                
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * 30

        # Clamp scrolling
        if self.scroll_y > 0:
            self.scroll_y = 0
        elif self.scroll_y < self.max_scroll:
            self.scroll_y = self.max_scroll

        return None
