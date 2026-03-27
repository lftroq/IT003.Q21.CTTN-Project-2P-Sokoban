import copy
import pygame

from setup import gameSetup as gs

# Color constants for player indicators
P1_COLOR = (220, 60, 60)
P2_COLOR = (60, 140, 220)
P1_READY = (180, 90, 90)
P2_READY = (90, 140, 180)

move_limit = 50
map_mode = "SEP"

# Keyboard mappings for each player
P1_KEYS = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
P2_KEYS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]

P1_MAP = {pygame.K_w: "U", pygame.K_s: "D", pygame.K_a: "L", pygame.K_d: "R"}
P2_MAP = {pygame.K_LEFT: "L", pygame.K_RIGHT: "R", pygame.K_UP: "U", pygame.K_DOWN: "D"}


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
        
        # Stack for undo functionality
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

    def _get_key(self, player: bool) -> str:
        """
        Get the next move for a bot player.
        
        Args:
            player: False for P1, True for P2
            
        Returns:
            Move direction as string: "U", "D", "L", "R", or "S" (stay)
        """
        return 'S'

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
        
        Returns: None
        """
            
        # Game over handling
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "MENU"
            return None

        # Player 1 input handling
        if (
            event.type == pygame.KEYDOWN
            and event.key in P1_KEYS
            and (self.ready & (1 << 0)) == 0
        ):
            # Human player controlling P1
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

        # Player 2 input handling
        if (
            event.type == pygame.KEYDOWN
            and event.key in P2_KEYS
            and (self.ready & (1 << 1)) == 0
        ):
            # Human player controlling P2
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
    game = GameScreen()

    mode = "GAME"
    running = True

    while running:
        gs.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or mode == "MENU":
                running = False
                break

            else:
                mode = game.handle_event(event)

        # Render current screen
        game.draw()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
