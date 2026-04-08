import copy
import pygame

from setup import gameSetup as gs
from interactor import interactor

# Color constants for player indicators
P1_COLOR = (220, 60, 60)
P2_COLOR = (60, 140, 220)
P1_READY = (180, 90, 90)
P2_READY = (90, 140, 180)

move_limit = 200
map_mode = "SYM"


playerOneInteract, playerTwoInteract = True, False
filename = ["sample", "sample"]

BOT_MODELS = {
    "EASY": "sample.exe",
    "MED": "sample.exe",
    "HARD": "sample.exe",
}

# Keyboard mappings for each player
P1_KEYS = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
P2_KEYS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]

P1_MAP = {pygame.K_w: "U", pygame.K_s: "D", pygame.K_a: "L", pygame.K_d: "R"}
P2_MAP = {pygame.K_LEFT: "L", pygame.K_RIGHT: "R", pygame.K_UP: "U", pygame.K_DOWN: "D"}

BOT_DELAY_MS = 150

def _draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font, x: int, y: int, color=(255, 255, 255)):
    """
    Render and blit text to the given surface at the specified position.
    
    Args:
        surface: Pygame surface to draw on
        text: Text string to render
        font: Pygame font object
        x: Center x-coordinate
        y: Center y-coordinate
        color: RGB color tuple (default: white)
    """
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    surface.blit(img, rect)


class UIButton:
    """
    A clickable button UI element with hover effects.
    
    Attributes:
        rect: Pygame Rect defining button position and size
        text: Label text displayed on the button
    """
    
    def __init__(self, rect: pygame.Rect, text: str):
        """Initialize a button with position and label."""
        self.rect = rect
        self.text = text

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, *, hovered: bool = False):
        """
        Draw the button on the given surface.
        
        Args:
            surface: Pygame surface to draw on
            font: Pygame font object for rendering text
            hovered: Whether button is hovered (changes color)
        """
        bg = (235, 235, 235) if not hovered else (220, 220, 220)
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 2, border_radius=8)
        img = font.render(self.text, True, (20, 20, 20))
        r = img.get_rect(center=self.rect.center)
        surface.blit(img, r)

    def hit(self, pos) -> bool:
        """Check if the given position collides with the button."""
        return self.rect.collidepoint(pos)

class MenuScreen:
    """Main menu with Play button and title."""

    def __init__(self):
        """Initialize menu screen with fonts and button layout."""
        self.title_font = pygame.font.Font("graphics/silkscreen.ttf", 42)
        self.btn_font = pygame.font.Font("graphics/silkscreen.ttf", 28)

        btn_w, btn_h = 220, 70
        self.play_rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.play_rect.center = (gs.xSize // 2, gs.ySize // 2 + 60)

        self.hint_font = pygame.font.Font("graphics/silkscreen.ttf", 16)

    def draw(self):
        """Render menu screen with title and play button."""
        gs.screen.fill((0, 0, 0))

        _draw_text(gs.screen, "2P SOKOBAN", self.title_font, gs.xSize // 2, gs.ySize // 2 - 40)

        pygame.draw.rect(gs.screen, (30, 30, 30), self.play_rect)
        pygame.draw.rect(gs.screen, (200, 200, 200), self.play_rect, 2)
        _draw_text(gs.screen, "PLAY", self.btn_font, self.play_rect.centerx, self.play_rect.centery)

        _draw_text(
            gs.screen,
            "Click Play or press ENTER",
            self.hint_font,
            gs.xSize // 2,
            self.play_rect.bottom + 28,
            color=(160, 160, 160),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle menu events.
        
        Returns:
            True if player wants to start game
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_rect.collidepoint(event.pos):
                return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return True
        return False


class InitScreen:
    """Game initialization screen for player/bot selection and settings."""

    def __init__(self):
        """Initialize init screen with buttons for player modes, difficulty, and move limits."""
        self.title_font = pygame.font.Font("graphics/silkscreen.ttf", 34)
        self.font = pygame.font.Font("graphics/silkscreen.ttf", 16)
        self.btn_font = pygame.font.Font("graphics/silkscreen.ttf", 16)
        self.big_num_font = pygame.font.Font("graphics/silkscreen.ttf", 32)

        panel_w, panel_h = 620, 400
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

        my = self.panel.bottom - 160
        self.btn_minus = UIButton(pygame.Rect(self.panel.left + 120, my, 54, 38), "-")
        self.btn_plus  = UIButton(pygame.Rect(self.panel.left + 250, my, 54, 38), "+")
        self.btn_50  = UIButton(pygame.Rect(right_x, my, diff_w, diff_h), "50")
        self.btn_100   = UIButton(pygame.Rect(right_x + diff_w + diff_gap, my, diff_w, diff_h), "100")
        self.btn_200   = UIButton(pygame.Rect(right_x + 2 * (diff_w + diff_gap), my, diff_w, diff_h), "200")

        mode_y = my + 50
        self.btn_mode_sep = UIButton(pygame.Rect(self.panel.left + 120, mode_y, 90, 36), "SEP")
        self.btn_mode_sym = UIButton(pygame.Rect(self.panel.left + 220, mode_y, 90, 36), "SYM")
        self.btn_mode_def = UIButton(pygame.Rect(self.panel.left + 320, mode_y, 90, 36), "DEF")

        sy = self.panel.bottom - 45
        self.btn_start = UIButton(pygame.Rect(self.panel.centerx - 120, sy, 110, 40), "START")
        self.btn_back  = UIButton(pygame.Rect(self.panel.centerx + 10, sy, 110, 40), "BACK")

        self.p1_is_bot = True
        self.p2_is_bot = False
        self.p1_diff = "HARD"
        self.p2_diff = "HARD"
        self.move_limit = 50
        self.map_mode = "SYM"

    def _apply_settings(self):
        """Apply selected settings to global game variables."""
        global playerOneInteract, playerTwoInteract, filename, move_limit, map_mode

        playerOneInteract = self.p1_is_bot
        playerTwoInteract = self.p2_is_bot

        if self.p1_is_bot:
            filename[0] = BOT_MODELS[self.p1_diff]
        if self.p2_is_bot:
            filename[1] = BOT_MODELS[self.p2_diff]

        move_limit = max(1, int(self.move_limit))
        map_mode = self.map_mode

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
        self.btn_mode_def.draw(gs.screen, self.btn_font,
                               hovered=self.btn_mode_def.hit((mx, my)))

        sel_mode_btn = {
            "SEP": self.btn_mode_sep,
            "SYM": self.btn_mode_sym,
            "DEF": self.btn_mode_def
        }[self.map_mode]

        pygame.draw.rect(gs.screen, (255,255,255),
                         sel_mode_btn.rect, 2, border_radius=8)

        _draw_text(gs.screen, "MOVE:", self.font, self.panel.left + 85, self.btn_minus.rect.centery, color=(200, 200, 200))
        self.btn_minus.draw(gs.screen, self.btn_font, hovered=self.btn_minus.hit((mx, my)))
        self.btn_plus.draw(gs.screen, self.btn_font, hovered=self.btn_plus.hit((mx, my)))
        self.btn_50.draw(gs.screen, self.btn_font, hovered=self.btn_50.hit((mx, my)))
        self.btn_100.draw(gs.screen, self.btn_font, hovered=self.btn_100.hit((mx, my)))
        self.btn_200.draw(gs.screen, self.btn_font, hovered=self.btn_200.hit((mx, my)))
        _draw_text(gs.screen, str(self.move_limit), self.big_num_font, self.panel.left + 210, self.btn_minus.rect.centery)

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
            elif self.btn_mode_def.hit(pos):
                self.map_mode = "DEF"

            elif self.btn_minus.hit(pos):
                self.move_limit = max(5, self.move_limit - 5)
            elif self.btn_plus.hit(pos):
                self.move_limit = min(200, self.move_limit + 5)
            elif self.btn_50.hit(pos):
                self.move_limit = 50
            elif self.btn_100.hit(pos):
                self.move_limit = 100
            elif self.btn_200.hit(pos):
                self.move_limit = 200

            elif self.btn_start.hit(pos):
                self._apply_settings()
                return "START"
            elif self.btn_back.hit(pos):
                return "BACK"

        return None

class GameScreen:
    """Main game screen handling gameplay, rendering, and turn resolution."""
    
    def __init__(self):
        """Initialize game screen with UI buttons and game state."""
        self.game_over = False
        self.game_result_text = ""
    
        # Fonts for different UI elements
        self.customFontScore = pygame.font.Font("graphics/silkscreen.ttf", 25)
        self.customFontReady = pygame.font.Font("graphics/silkscreen.ttf", 18)
        self.customFontUi = pygame.font.Font("graphics/silkscreen.ttf", 14)

        # Player movement deltas (change in x, y)
        self.dxOne = 0
        self.dyOne = 0
        self.dxTwo = 0
        self.dyTwo = 0

        # Last move direction for each player
        self.keyOne = "S"
        self.keyTwo = "S"
        
        # Bitfield: bit 0 = P1 ready, bit 1 = P2 ready
        self.ready = 0
        
        self.last_bot_move_time = 0
        # UI button layout

    def draw_grid(self):
        """Render the game grid with walls and floor tiles."""
        for row in range(gs.gridSize):
            for col in range(gs.gridSize):
                x = col * gs.tileSize + gs.padding
                y = row * gs.tileSize + gs.offset

                if gs.grid[row][col] == 1:
                    gs.screen.blit(gs.wallImg, (x, y))
                else:
                    gs.screen.blit(gs.tileImg, (x, y))
                pygame.draw.rect(gs.screen, gs.grayColor, (x, y, gs.tileSize, gs.tileSize), 1)

    def draw_players(self):
        """Render player sprites at current positions."""
        x, y = gs.playerOnePos
        gs.screen.blit(gs.playerOneImg, (x * gs.tileSize + gs.padding, y * gs.tileSize + gs.offset))
        x, y = gs.playerTwoPos
        gs.screen.blit(gs.playerTwoImg, (x * gs.tileSize + gs.padding, y * gs.tileSize + gs.offset))

    def draw_boxes_portals(self):
        """Render boxes and portal sprites."""
        for x, y in gs.boxes:
            gs.screen.blit(gs.boxImg, (x * gs.tileSize + gs.padding, y * gs.tileSize + gs.offset))

        x, y = gs.portalOne
        gs.screen.blit(gs.portalOneImg, (x * gs.tileSize + gs.padding, y * gs.tileSize + gs.offset))
        x, y = gs.portalTwo
        gs.screen.blit(gs.portalTwoImg, (x * gs.tileSize + gs.padding, y * gs.tileSize + gs.offset))

    def draw_score(self):
        """Render the current score for both players."""
        textbox = self.customFontScore.render(f"P1: {gs.score[0]}", True, P1_COLOR)
        rect = textbox.get_rect()
        rect.center = (gs.padding + rect.width / 2, gs.padding + gs.textSize / 2 - 9)
        gs.screen.blit(textbox, rect)

        textbox = self.customFontScore.render(f"P2: {gs.score[1]}", True, P2_COLOR)
        rect = textbox.get_rect()
        rect.center = (gs.xSize - gs.padding - rect.width / 2, gs.padding + gs.textSize / 2 - 9)
        gs.screen.blit(textbox, rect)

    def draw_ready_state(self):
        """Render "ready" notifications for players who have made their move."""
        if (self.ready & (1 << 0)) > 0:
            textbox = self.customFontReady.render("P1 ready", True, P1_READY)
            rect = textbox.get_rect()
            rect.center = (gs.padding + rect.width / 2, gs.padding + gs.textSize / 2 + 11)
            gs.screen.blit(textbox, rect)

        if (self.ready & (1 << 1)) > 0:
            textbox = self.customFontReady.render("P2 ready", True, P2_READY)
            rect = textbox.get_rect()
            rect.center = (gs.xSize - gs.padding - rect.width / 2, gs.padding + gs.textSize / 2 + 11)
            gs.screen.blit(textbox, rect)

    def _capture_state(self) -> dict:
        """
        Capture current game state for undo functionality.
        
        Returns:
            Dictionary containing all relevant game state
        """
        return {
            "playerOnePos": gs.playerOnePos,
            "playerTwoPos": gs.playerTwoPos,
            "boxes": copy.deepcopy(gs.boxes),
            "score": copy.deepcopy(gs.score),
            "playerMove": copy.deepcopy(gs.playerMove),
            "playerDidMove": copy.deepcopy(gs.playerDidMove),
            "turn": gs.turn,
        }

    def _restore_state(self, state: dict):
        """
        Restore game state from a captured state dictionary.
        
        Args:
            state: State dictionary from _capture_state()
        """
        gs.playerOnePos = state["playerOnePos"]
        gs.playerTwoPos = state["playerTwoPos"]
        gs.boxes = copy.deepcopy(state["boxes"])
        gs.score = copy.deepcopy(state["score"])
        gs.playerMove = copy.deepcopy(state["playerMove"])
        gs.playerDidMove = copy.deepcopy(state["playerDidMove"])
        gs.turn = state["turn"]

        # Reset input state
        self.ready, self.dxOne, self.dyOne, self.dxTwo, self.dyTwo = 0, 0, 0, 0, 0
        
    def _in_grid(self, x: int, y: int) -> bool:
        """Check if coordinates are within grid bounds."""
        return 0 <= x < gs.gridSize and 0 <= y < gs.gridSize

    def _check_shift(self, x: int, y: int, dx: int, dy: int) -> list:
        """
        Check if boxes can be shifted in a direction.
        
        Args:
            x, y: Starting position
            dx, dy: Direction of shift
            
        Returns:
            List of box indices that would be shifted, or empty list if invalid
        """
        shift_list = []
        while self._in_grid(x, y) and (x, y) in gs.boxes:
            shift_list.append(gs.boxes.index((x, y)))
            x += dx
            y += dy
        if self._in_grid(x, y) and gs.grid[y][x] == 0 and (x, y) != gs.playerOnePos and (x, y) != gs.playerTwoPos:
            return shift_list
        return []

    def _change_position(self, curPos, dx: int, dy: int) -> bool:
        """
        Legacy movement function. Move player and shift boxes if needed.
        
        Args:
            curPos: Current player position
            dx, dy: Intended movement direction
            
        Returns:
            True if movement was valid and executed
        """
        newX, newY = curPos
        if dx == 0 and dy == 0:
            return False

        if self._in_grid(newX, newY) and gs.grid[newY][newX] == 0 and curPos != gs.portalOne and curPos != gs.portalTwo:
            shift_list = self._check_shift(newX, newY, dx, dy)
            for idx in shift_list:
                tx, ty = gs.boxes[idx]
                gs.boxes[idx] = (tx + dx, ty + dy)
            if gs.portalOne in gs.boxes:
                gs.score[0] += 1
                gs.boxes.remove(gs.portalOne)
            if gs.portalTwo in gs.boxes:
                gs.score[1] += 1
                gs.boxes.remove(gs.portalTwo)
            return len(shift_list) > 0 or not ((newX, newY) in gs.boxes)
        return False

    def _move(self, curPos, dx: int, dy: int):
        """Calculate new position after movement."""
        x, y = curPos
        return (x + dx, y + dy)

    def _attempt_plan(self, curPos, dx: int, dy: int, blocked_cells: set) -> dict:
        """
        Attempt to plan a player move, checking for collisions and box shifts.
        
        Args:
            curPos: Current position
            dx, dy: Intended movement direction
            blocked_cells: Set of positions that cannot be entered
            
        Returns:
            Dict with keys: valid (bool), newPos (tuple), box_moves (list)
        """
        if dx == 0 and dy == 0:
            return {"valid": False, "newPos": curPos, "box_moves": []}

        x, y = curPos
        nx, ny = x + dx, y + dy

        # Check grid boundaries
        if not self._in_grid(nx, ny) or gs.grid[ny][nx] == 1:
            return {"valid": False, "newPos": curPos, "box_moves": []}
        
        # Check portals (can't move into them)
        if (nx, ny) == gs.portalOne or (nx, ny) == gs.portalTwo:
            return {"valid": False, "newPos": curPos, "box_moves": []}

        # Check blocked cells
        if (nx, ny) in blocked_cells:
            return {"valid": False, "newPos": curPos, "box_moves": []}

        # No obstacles, can move directly
        if (nx, ny) not in gs.boxes:
            return {"valid": True, "newPos": (nx, ny), "box_moves": []}

        # Attempt to push/shift boxes
        chain = []
        cx, cy = nx, ny
        while self._in_grid(cx, cy) and (cx, cy) in gs.boxes:
            chain.append((cx, cy))
            cx += dx
            cy += dy

        # Check if chain can be pushed
        if not self._in_grid(cx, cy) or gs.grid[cy][cx] == 1:
            return {"valid": False, "newPos": curPos, "box_moves": []}
        if (cx, cy) in blocked_cells:
            return {"valid": False, "newPos": curPos, "box_moves": []}
        if (cx, cy) in gs.boxes:
            return {"valid": False, "newPos": curPos, "box_moves": []}

        # Create box movement list
        box_moves = []
        for bx, by in reversed(chain):
            box_moves.append(((bx, by), (bx + dx, by + dy)))

        return {"valid": True, "newPos": (nx, ny), "box_moves": box_moves}

    def _apply_all_box_moves_and_score(self, p1_box_moves, p2_box_moves):
        """
        Apply all box movements and update score for boxes reaching portals.
        
        Args:
            p1_box_moves: List of box moves for player 1
            p2_box_moves: List of box moves for player 2
        """
        new_boxes = list(gs.boxes)

        def apply_moves(moves):
            nonlocal new_boxes
            for from_pos, to_pos in moves:
                if from_pos in new_boxes:
                    i = new_boxes.index(from_pos)
                    new_boxes[i] = to_pos

        apply_moves(p1_box_moves)
        apply_moves(p2_box_moves)

        gs.boxes = new_boxes

        # Score boxes that reached portals
        if gs.portalOne in gs.boxes:
            gs.score[0] += 1
            gs.boxes.remove(gs.portalOne)
        if gs.portalTwo in gs.boxes:
            gs.score[1] += 1
            gs.boxes.remove(gs.portalTwo)

    def _move_players(self) -> tuple:
        """
        Resolve player moves for the current turn.
        
        Returns:
            Tuple of (p1_moved, p2_moved) indicating if each player successfully moved
        """
        p1_start = gs.playerOnePos
        p2_start = gs.playerTwoPos

        # Check if players intended to move
        p1_intend = not (self.dxOne == 0 and self.dyOne == 0)
        p2_intend = not (self.dxTwo == 0 and self.dyTwo == 0)

        p1_target = (p1_start[0] + self.dxOne, p1_start[1] + self.dyOne)
        p2_target = (p2_start[0] + self.dxTwo, p2_start[1] + self.dyTwo)

        # If both players target the same cell, both fail
        if p1_intend and p2_intend and p1_target == p2_target:
            return False, False

        # Plan moves for both players
        p1_plan = self._attempt_plan(p1_start, self.dxOne, self.dyOne, blocked_cells=set())
        p2_plan = self._attempt_plan(p2_start, self.dxTwo, self.dyTwo, blocked_cells=set())

        p1_end = p1_plan["newPos"] if p1_plan["valid"] else p1_start
        p2_end = p2_plan["newPos"] if p2_plan["valid"] else p2_start

        # Both players can't end in same cell
        if p1_end == p2_end:
            return False, False

        p1_valid = p1_plan["valid"]
        p2_valid = p2_plan["valid"]

        # Handle collision: one player moves into other's starting position while other can't move
        if p1_valid and p1_end == p2_start and (not p2_valid):
            p1_valid = False
            p1_end = p1_start
            p1_plan["box_moves"] = []

        if p2_valid and p2_end == p1_start and (not p1_valid):
            p2_valid = False
            p2_end = p2_start
            p2_plan["box_moves"] = []

        # Recheck final positions
        if p1_end == p2_end:
            return False, False

        p1_box_moves = p1_plan["box_moves"] if p1_valid else []
        p2_box_moves = p2_plan["box_moves"] if p2_valid else []

        # Check for box conflicts: same box moved by both players
        p1_idx = {i for i, _ in p1_box_moves}
        p2_idx = {i for i, _ in p2_box_moves}

        if p1_idx & p2_idx:
            p1_valid = p2_valid = False
            p1_box_moves = p2_box_moves = []
            p1_end, p2_end = p1_start, p2_start

        # Check for box destination conflicts
        if p1_valid and p2_valid:
            p1_targets = {pos for _, pos in p1_box_moves}
            p2_targets = {pos for _, pos in p2_box_moves}
            if p1_targets & p2_targets:
                p1_valid = p2_valid = False
                p1_box_moves = p2_box_moves = []
                p1_end, p2_end = p1_start, p2_start

        # Check if moved boxes block the other player
        if p1_valid:
            for _, pos in p1_box_moves:
                if pos == p2_end:
                    p1_valid = False
                    p1_box_moves = []
                    p1_end = p1_start
                    break
        if p2_valid:
            for _, pos in p2_box_moves:
                if pos == p1_end:
                    p2_valid = False
                    p2_box_moves = []
                    p2_end = p2_start
                    break

        # Final collision check
        if p1_end == p2_end:
            p1_valid = p2_valid = False
            p1_end, p2_end = p1_start, p2_start
            p1_box_moves = p2_box_moves = []

        # Apply final positions and box moves
        gs.playerOnePos = p1_end if p1_valid else p1_start
        gs.playerTwoPos = p2_end if p2_valid else p2_start

        p1_box_moves = p1_plan["box_moves"] if p1_valid else []
        p2_box_moves = p2_plan["box_moves"] if p2_valid else []
        self._apply_all_box_moves_and_score(p1_box_moves, p2_box_moves)

        return p1_valid, p2_valid

    def _get_key(self, player: bool):
        """
        Get input from bot AI for specified player.
        
        Args:
            player: True for P2, False for P1
            
        Returns:
            Direction string (U/D/L/R/S)
        """
        maze = copy.deepcopy(gs.grid)
        for i in range(gs.gridSize):
            for j in range(gs.gridSize):
                maze[i][j] = "#" if gs.grid[i][j] == 1 else "."
        for x, y in gs.boxes:
            maze[y][x] = "X"

        if not player:
            x, y = gs.playerOnePos
            maze[y][x] = "a"
            x, y = gs.playerTwoPos
            maze[y][x] = "b"
            x, y = gs.portalOne
            maze[y][x] = "A"
            x, y = gs.portalTwo
            maze[y][x] = "B"
        else:
            x, y = gs.playerTwoPos
            maze[y][x] = "a"
            x, y = gs.playerOnePos
            maze[y][x] = "b"
            x, y = gs.portalTwo
            maze[y][x] = "A"
            x, y = gs.portalOne
            maze[y][x] = "B"

        payload = {
            "size": gs.gridSize,
            "cur": gs.turn,
            "T": move_limit,
            "maze": maze,
            "playerHist": gs.playerMove[player],
            "oppHist": gs.playerMove[not player],
            "playerScore": gs.score[player],
            "oppScore": gs.score[not player],
            "playerDidMove": gs.playerDidMove[player],
            "oppDidMove": gs.playerDidMove[not player],
        }
        return interactor.interact(filename[player], payload)

    def _resolve_turn_if_ready(self):
        """Resolve the turn if both players have submitted moves."""
        if self.ready == 3:  # Both players ready (bits 0 and 1 set)
            # Capture state before applying moves

            # Move players and resolve box conflicts
            m1, m2 = self._move_players()

            # Reset input state for next turn
            self.ready, self.dxOne, self.dyOne, self.dxTwo, self.dyTwo = 0, 0, 0, 0, 0

            # Record moves in game history
            gs.playerMove[0] += self.keyOne
            gs.playerMove[1] += self.keyTwo

            gs.playerDidMove[0] += "1" if m1 else "0"
            gs.playerDidMove[1] += "1" if m2 else "0"

            # Advance turn
            gs.turn += 1
            if (gs.turn - 1) >= move_limit:
                self._end_game()

    def _end_game(self):
        """End the game and determine the winner."""
        self.game_over = True
        if gs.score[0] > gs.score[1]:
            self.game_result_text = "P1 Wins!"
        elif gs.score[1] > gs.score[0]:
            self.game_result_text = "P2 Wins!"
        else:
            self.game_result_text = "Draw!"
        self.ready, self.dxOne, self.dyOne, self.dxTwo, self.dyTwo = 0, 0, 0, 0, 0

    def handle_event(self, event: pygame.event.Event):
        """
        Handle game screen input events.
        
        Returns: Navigation signal ("MENU", "INIT") or None
        """
            
        # Game over handling
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                elif event.key == pygame.K_r:
                    self.reset_game()
                    return None
            return None

        both_bots = playerOneInteract and playerTwoInteract
        space_pressed = pygame.key.get_pressed()[pygame.K_SPACE]

        allow_bot_move = True
        if both_bots:
            current_time = pygame.time.get_ticks()
            if space_pressed and (current_time - self.last_bot_move_time >= BOT_DELAY_MS):
                self.last_bot_move_time = current_time
                allow_bot_move = True
            else:
                allow_bot_move = False

        # Player 1 input
        if (
            (not playerOneInteract)
            and event.type == pygame.KEYDOWN
            and event.key in P1_KEYS
            and (self.ready & (1 << 0)) == 0
        ):
            if event.key == pygame.K_w:
                self.dyOne = -1
            if event.key == pygame.K_s:
                self.dyOne = 1
            if event.key == pygame.K_a:
                self.dxOne = -1
            if event.key == pygame.K_d:
                self.dxOne = 1
            self.ready |= (1 << 0)
            self.keyOne = P1_MAP[event.key]
        elif playerOneInteract and (self.ready & (1 << 0)) == 0:
            if (not both_bots) or allow_bot_move:
                key = self._get_key(False)
                if key == "U":
                    self.dyOne = -1
                if key == "D":
                    self.dyOne = 1
                if key == "L":
                    self.dxOne = -1
                if key == "R":
                    self.dxOne = 1
                self.ready |= (1 << 0)
                if(key not in ["U","D","L","R"]):
                    key="S"
                self.keyOne = key

        # Player 2 input
        if (
            (not playerTwoInteract)
            and event.type == pygame.KEYDOWN
            and event.key in P2_KEYS
            and (self.ready & (1 << 1)) == 0
        ):
            if event.key == pygame.K_LEFT:
                self.dxTwo = -1
            if event.key == pygame.K_RIGHT:
                self.dxTwo = 1
            if event.key == pygame.K_UP:
                self.dyTwo = -1
            if event.key == pygame.K_DOWN:
                self.dyTwo = 1
            self.ready |= (1 << 1)
            self.keyTwo = P2_MAP[event.key]
        elif playerTwoInteract and (self.ready & (1 << 1)) == 0:
            if (not both_bots) or allow_bot_move:
                key = self._get_key(True)
                if key == "L":
                    self.dxTwo = -1
                if key == "R":
                    self.dxTwo = 1
                if key == "U":
                    self.dyTwo = -1
                if key == "D":
                    self.dyTwo = 1
                self.ready |= (1 << 1)
                if(key not in ["U","D","L","R"]):
                    key="S"
                self.keyTwo = key

        self._resolve_turn_if_ready()

    def draw(self):
        """Render the complete game screen."""
        gs.screen.fill((0, 0, 0))
        self.draw_grid()
        self.draw_players()
        self.draw_boxes_portals()
        self.draw_score()
        self.draw_ready_state()

        # Display remaining moves
        remain = max(0, move_limit - (gs.turn - 1))
        _draw_text(
            gs.screen,
            f"Moves left: {remain}",
            self.customFontUi,
            gs.xSize // 2,
            gs.padding + 12,
            color=(180, 180, 180),
        )

        # Draw game over overlay if applicable
        if self.game_over:
            overlay = pygame.Surface((gs.xSize, gs.ySize), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            gs.screen.blit(overlay, (0, 0))
            _draw_text(gs.screen, "GAME OVER", self.customFontScore, gs.xSize // 2, gs.ySize // 2 - 30)
            _draw_text(gs.screen, self.game_result_text, self.customFontScore, gs.xSize // 2, gs.ySize // 2 + 10)
            _draw_text(gs.screen, "Press ESC or Quit", self.customFontUi, gs.xSize // 2, gs.ySize // 2 + 50, color=(200, 200, 200))


def reset_game_state(generate: bool = False):
    """
    Reset game state to initial values.
    
    Args:
        generate: If True, generate a new level; if False, use current level
    """
    gs.getMap(generate, N=16, MODE=map_mode)
    gs.score = [0, 0]
    gs.playerMove = ["", ""]
    gs.playerDidMove = ["", ""]
    gs.turn = 1


def main():
    """Main game loop managing state transitions between menu, init, and game screens."""
    menu = MenuScreen()
    init = InitScreen()
    game = GameScreen()

    mode = "MENU"
    running = True

    while running:
        gs.clock.tick(60)

        if mode == "GAME" and playerOneInteract and playerTwoInteract:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if mode == "MENU":
                if menu.handle_event(event):
                    init = InitScreen()
                    mode = "INIT"

            elif mode == "INIT":
                sig = init.handle_event(event)
                if sig == "BACK":
                    mode = "MENU"
                elif sig == "START":
                    reset_game_state(True)
                    game = GameScreen()
                    mode = "GAME"

            else:
                signal = game.handle_event(event)
                if signal == "MENU":
                    mode = "MENU"
                elif signal == "INIT":
                    mode = "INIT"

        if mode == "MENU":
            menu.draw()
        elif mode == "INIT":
            init.draw()
        else:
            game.draw()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
