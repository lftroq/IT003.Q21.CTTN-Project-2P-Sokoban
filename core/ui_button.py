"""
UI Button Component.

This module provides a generic UIButton class used for interactive and
clickable elements across various game screens.
"""
import pygame

class UIButton:
    """Simple clickable button UI element with hover effects."""

    def __init__(self, rect: pygame.Rect, text: str):
        """
        Initialize button.
        
        Args:
            rect: Button rectangle
            text: Button label text
        """
        self.rect = rect
        self.text = text

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, *, hovered: bool = False):
        """
        Draw button on surface with optional hover effect.
        
        Args:
            surface: Pygame surface to draw on
            font: Font for button text
            hovered: Whether button is currently hovered
        """
        bg = (235, 235, 235) if not hovered else (220, 220, 220)
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 2, border_radius=8)
        img = font.render(self.text, True, (20, 20, 20))
        r = img.get_rect(center=self.rect.center)
        surface.blit(img, r)

    def hit(self, pos) -> bool:
        """Check if position collides with button."""
        return self.rect.collidepoint(pos)
