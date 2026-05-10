"""
Initialization Screen Module.

This module defines the InitScreen class, which presents the pre-game lobby
for configuring player controls, bot difficulty, map size, and move limits.
"""
import pygame
from setup import gameSetup as gs
import core.config as config
from core.utils import _draw_text
from core.ui_button import UIButton

class InitScreen:
    """Game initialization screen for player/bot selection and settings."""

    def __init__(self):
        """Initialize init screen with buttons for player modes, difficulty, and move limits."""
        self.title_font = pygame.font.Font(gs.FONT, 34)
        self.font = pygame.font.Font(gs.FONT, 16)
        self.btn_font = pygame.font.Font(gs.FONT, 16)
        self.big_num_font = pygame.font.Font(gs.FONT, 32)

        panel_w, panel_h = 620, 460
        self.panel = pygame.Rect(0, 0, panel_w, panel_h)
        self.panel.center = (gs.xSize // 2, gs.ySize // 2)

        col_w = 240
        left_x = self.panel.left + 70
        right_x = self.panel.right - 70 - col_w
        top_y = self.panel.top + 85

        box_w, box_h, gap_y = col_w, 44, 12
        diff_w, diff_h, diff_gap = 72, 36, 12

        self.p1_human = UIButton(pygame.Rect(left_x, top_y, box_w, box_h), "HUMAN")
        self.p1_bot   = UIButton(pygame.Rect(left_x, top_y + box_h + gap_y, box_w, box_h), "BOT")
        dy = top_y + 2 * (box_h + gap_y) + 6
        self.p1_easy  = UIButton(pygame.Rect(left_x, dy, diff_w, diff_h), "EASY")
        self.p1_med   = UIButton(pygame.Rect(left_x + diff_w + diff_gap, dy, diff_w, diff_h), "MED")
        self.p1_hard  = UIButton(pygame.Rect(left_x + 2 * (diff_w + diff_gap), dy, diff_w, diff_h), "HARD")

        self.p2_human = UIButton(pygame.Rect(right_x, top_y, box_w, box_h), "HUMAN")
        self.p2_bot   = UIButton(pygame.Rect(right_x, top_y + box_h + gap_y, box_w, box_h), "BOT")
        self.p2_easy  = UIButton(pygame.Rect(right_x, dy, diff_w, diff_h), "EASY")
        self.p2_med   = UIButton(pygame.Rect(right_x + diff_w + diff_gap, dy, diff_w, diff_h), "MED")
        self.p2_hard  = UIButton(pygame.Rect(right_x + 2 * (diff_w + diff_gap), dy, diff_w, diff_h), "HARD")

        my = self.panel.bottom - 210
        bw, bh = 50, 38
        cx = self.panel.centerx + 30
        
        self.btn_m100 = UIButton(pygame.Rect(0, 0, bw, bh), "-100")
        self.btn_m100.rect.centerx = cx - 190
        self.btn_m100.rect.top = my
        
        self.btn_m25 = UIButton(pygame.Rect(0, 0, bw, bh), "-25")
        self.btn_m25.rect.centerx = cx - 128
        self.btn_m25.rect.top = my
        
        self.btn_minus = UIButton(pygame.Rect(0, 0, bw, bh), "-5")
        self.btn_minus.rect.centerx = cx - 66
        self.btn_minus.rect.top = my
        
        self.btn_plus = UIButton(pygame.Rect(0, 0, bw, bh), "+5")
        self.btn_plus.rect.centerx = cx + 66
        self.btn_plus.rect.top = my
        
        self.btn_p25 = UIButton(pygame.Rect(0, 0, bw, bh), "+25")
        self.btn_p25.rect.centerx = cx + 128
        self.btn_p25.rect.top = my
        
        self.btn_p100 = UIButton(pygame.Rect(0, 0, bw, bh), "+100")
        self.btn_p100.rect.centerx = cx + 190
        self.btn_p100.rect.top = my

        mode_y = my + 45
        self.btn_mode_sep = UIButton(pygame.Rect(self.panel.left + 120, mode_y, 90, 36), "SEP")
        self.btn_mode_sym = UIButton(pygame.Rect(self.panel.left + 220, mode_y, 90, 36), "SYM")
        self.btn_mode_non = UIButton(pygame.Rect(self.panel.left + 320, mode_y, 90, 36), "NON")

        size_y = mode_y + 45
        self.btn_size_sm = UIButton(pygame.Rect(self.panel.left + 120, size_y, 90, 36), "SML")
        self.btn_size_md = UIButton(pygame.Rect(self.panel.left + 220, size_y, 90, 36), "MED")
        self.btn_size_lg = UIButton(pygame.Rect(self.panel.left + 320, size_y, 90, 36), "LRG")

        sy = self.panel.bottom - 45
        self.btn_start = UIButton(pygame.Rect(self.panel.centerx - 120, sy, 110, 40), "START")
        self.btn_back  = UIButton(pygame.Rect(self.panel.centerx + 10, sy, 110, 40), "BACK")

        self.p1_is_bot = True
        self.p2_is_bot = False
        self.p1_diff = "HARD"
        self.p2_diff = "HARD"
        self.move_limit = 50
        self.map_mode = "SYM"
        self.map_size = 16

    def _apply_settings(self):
        """Apply selected settings to global game variables."""
        config.playerOneInteract = self.p1_is_bot
        config.playerTwoInteract = self.p2_is_bot

        if self.p1_is_bot:
            config.filename[0] = config.BOT_MODELS[self.p1_diff]
        if self.p2_is_bot:
            config.filename[1] = config.BOT_MODELS[self.p2_diff]

        config.move_limit = max(1, int(self.move_limit))
        config.map_mode = self.map_mode
        config.map_size = self.map_size

    def draw(self):
        """Render initialization screen with all configuration options."""
        gs.screen.fill((0, 0, 0))
        pygame.draw.rect(gs.screen, (18, 18, 18), self.panel, border_radius=14)
        pygame.draw.rect(gs.screen, (200, 200, 200), self.panel, 2, border_radius=14)

        _draw_text(gs.screen, "GAME INIT", self.title_font, self.panel.centerx, self.panel.top + 38)

        _draw_text(gs.screen, "P1", self.font, self.p1_human.rect.centerx, self.p1_human.rect.top - 12, color=(200, 200, 200))
        _draw_text(gs.screen, "P2", self.font, self.p2_human.rect.centerx, self.p2_human.rect.top - 12, color=(200, 200, 200))

        mx, my = pygame.mouse.get_pos()

        self.p1_human.draw(gs.screen, self.btn_font, hovered=self.p1_human.hit((mx, my)))
        self.p1_bot.draw(gs.screen, self.btn_font, hovered=self.p1_bot.hit((mx, my)))

        sel = self.p1_bot if self.p1_is_bot else self.p1_human
        pygame.draw.rect(gs.screen, (255, 255, 255), sel.rect, 3, border_radius=8)

        self.p1_easy.draw(gs.screen, self.btn_font, hovered=self.p1_easy.hit((mx, my)))
        self.p1_med.draw(gs.screen, self.btn_font, hovered=self.p1_med.hit((mx, my)))
        self.p1_hard.draw(gs.screen, self.btn_font, hovered=self.p1_hard.hit((mx, my)))

        p1sel = {"EASY": self.p1_easy, "MED": self.p1_med, "HARD": self.p1_hard}[self.p1_diff]
        pygame.draw.rect(gs.screen, (255, 255, 255), p1sel.rect, 2, border_radius=8)
        if not self.p1_is_bot:
            dim = pygame.Surface((p1sel.rect.width * 3 + 24, p1sel.rect.height), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 120))
            gs.screen.blit(dim, (self.p1_easy.rect.left, self.p1_easy.rect.top))

        self.p2_human.draw(gs.screen, self.btn_font, hovered=self.p2_human.hit((mx, my)))
        self.p2_bot.draw(gs.screen, self.btn_font, hovered=self.p2_bot.hit((mx, my)))

        sel2 = self.p2_bot if self.p2_is_bot else self.p2_human
        pygame.draw.rect(gs.screen, (255, 255, 255), sel2.rect, 3, border_radius=8)

        self.p2_easy.draw(gs.screen, self.btn_font, hovered=self.p2_easy.hit((mx, my)))
        self.p2_med.draw(gs.screen, self.btn_font, hovered=self.p2_med.hit((mx, my)))
        self.p2_hard.draw(gs.screen, self.btn_font, hovered=self.p2_hard.hit((mx, my)))

        p2sel = {"EASY": self.p2_easy, "MED": self.p2_med, "HARD": self.p2_hard}[self.p2_diff]
        pygame.draw.rect(gs.screen, (255, 255, 255), p2sel.rect, 2, border_radius=8)
        if not self.p2_is_bot:
            dim = pygame.Surface((p2sel.rect.width * 3 + 24, p2sel.rect.height), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 120))
            gs.screen.blit(dim, (self.p2_easy.rect.left, self.p2_easy.rect.top))

        _draw_text(gs.screen, "MAP:", self.font,
                   self.panel.left + 80,
                   self.btn_mode_sep.rect.centery,
                   color=(200, 200, 200))

        self.btn_mode_sep.draw(gs.screen, self.btn_font,
                               hovered=self.btn_mode_sep.hit((mx, my)))
        self.btn_mode_sym.draw(gs.screen, self.btn_font,
                               hovered=self.btn_mode_sym.hit((mx, my)))
        self.btn_mode_non.draw(gs.screen, self.btn_font,
                               hovered=self.btn_mode_non.hit((mx, my)))

        sel_mode_btn = {
            "SEP": self.btn_mode_sep,
            "SYM": self.btn_mode_sym,
            "NON": self.btn_mode_non
        }[self.map_mode]

        pygame.draw.rect(gs.screen, (255,255,255),
                         sel_mode_btn.rect, 2, border_radius=8)

        _draw_text(gs.screen, "SIZE:", self.font,
                   self.panel.left + 80,
                   self.btn_size_sm.rect.centery,
                   color=(200, 200, 200))

        self.btn_size_sm.draw(gs.screen, self.btn_font, hovered=self.btn_size_sm.hit((mx, my)))
        self.btn_size_md.draw(gs.screen, self.btn_font, hovered=self.btn_size_md.hit((mx, my)))
        self.btn_size_lg.draw(gs.screen, self.btn_font, hovered=self.btn_size_lg.hit((mx, my)))

        sel_size_btn = {
            12: self.btn_size_sm,
            16: self.btn_size_md,
            24: self.btn_size_lg
        }[self.map_size]

        pygame.draw.rect(gs.screen, (255, 255, 255),
                         sel_size_btn.rect, 2, border_radius=8)

        _draw_text(gs.screen, "MOVE:", self.font, self.panel.left + 85, self.btn_m25.rect.centery, color=(200, 200, 200))
        self.btn_m100.draw(gs.screen, self.btn_font, hovered=self.btn_m100.hit((mx, my)))
        self.btn_m25.draw(gs.screen, self.btn_font, hovered=self.btn_m25.hit((mx, my)))
        self.btn_minus.draw(gs.screen, self.btn_font, hovered=self.btn_minus.hit((mx, my)))
        self.btn_plus.draw(gs.screen, self.btn_font, hovered=self.btn_plus.hit((mx, my)))
        self.btn_p25.draw(gs.screen, self.btn_font, hovered=self.btn_p25.hit((mx, my)))
        self.btn_p100.draw(gs.screen, self.btn_font, hovered=self.btn_p100.hit((mx, my)))
        _draw_text(gs.screen, str(self.move_limit), self.big_num_font, self.panel.centerx + 30, self.btn_m25.rect.centery)

        self.btn_start.draw(gs.screen, self.btn_font, hovered=self.btn_start.hit((mx, my)))
        self.btn_back.draw(gs.screen, self.btn_font, hovered=self.btn_back.hit((mx, my)))

    def handle_event(self, event: pygame.event.Event):
        """
        Handle keyboard and mouse events on init screen.
        
        Returns:
            "START" to begin game, "BACK" to return to menu, None otherwise
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "BACK"
            if event.key == pygame.K_RETURN:
                self._apply_settings()
                return "START"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.p1_human.hit(pos):
                self.p1_is_bot = False
            elif self.p1_bot.hit(pos):
                self.p1_is_bot = True
            elif self.p1_easy.hit(pos):
                self.p1_diff = "EASY"
            elif self.p1_med.hit(pos):
                self.p1_diff = "MED"
            elif self.p1_hard.hit(pos):
                self.p1_diff = "HARD"

            elif self.p2_human.hit(pos):
                self.p2_is_bot = False
            elif self.p2_bot.hit(pos):
                self.p2_is_bot = True
            elif self.p2_easy.hit(pos):
                self.p2_diff = "EASY"
            elif self.p2_med.hit(pos):
                self.p2_diff = "MED"
            elif self.p2_hard.hit(pos):
                self.p2_diff = "HARD"

            elif self.btn_mode_sep.hit(pos):
                self.map_mode = "SEP"
            elif self.btn_mode_sym.hit(pos):
                self.map_mode = "SYM"
            elif self.btn_mode_non.hit(pos):
                self.map_mode = "NON"

            elif self.btn_size_sm.hit(pos):
                self.map_size = 12
            elif self.btn_size_md.hit(pos):
                self.map_size = 16
            elif self.btn_size_lg.hit(pos):
                self.map_size = 24

            elif self.btn_m100.hit(pos):
                self.move_limit = max(5, self.move_limit - 100)
            elif self.btn_m25.hit(pos):
                self.move_limit = max(5, self.move_limit - 25)
            elif self.btn_minus.hit(pos):
                self.move_limit = max(5, self.move_limit - 5)
            elif self.btn_plus.hit(pos):
                self.move_limit = min(1000, self.move_limit + 5)
            elif self.btn_p25.hit(pos):
                self.move_limit = min(1000, self.move_limit + 25)
            elif self.btn_p100.hit(pos):
                self.move_limit = min(1000, self.move_limit + 100)

            elif self.btn_start.hit(pos):
                self._apply_settings()
                return "START"
            elif self.btn_back.hit(pos):
                return "BACK"

        return None
