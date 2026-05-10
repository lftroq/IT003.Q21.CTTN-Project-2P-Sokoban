"""
Game Screen Module.

This module provides the GameScreen class responsible for rendering the main
Sokoban game state, handling player/bot inputs, and resolving game logic
such as pushing boxes and scoring.
"""
import copy
import pygame
from setup import gameSetup as gs
from interactor import interactor
import core.config as config
from core.utils import _draw_text, reset_game_state
from core.ui_button import UIButton

class GameScreen:
    """Main game screen handling gameplay, rendering, and turn resolution."""

    def __init__(self):
        """Initialize game screen with rendering fonts, buttons, and game state."""
        self.game_over = False
        self.game_result_text = ""
    
        self.customFontScore = pygame.font.Font(gs.FONT, 25)
        self.customFontReady = pygame.font.Font(gs.FONT, 18)
        self.customFontUi = pygame.font.Font(gs.FONT, 14)

        self.dxOne = 0
        self.dyOne = 0
        self.dxTwo = 0
        self.dyTwo = 0

        self.keyOne = "S"
        self.keyTwo = "S"
        self.ready = 0
        
        self._undo_stack = []
        self.last_bot_move_time = 0

        btn_w, btn_h, gap = 72, 26, 8
        total_w = 5 * btn_w + 4 * gap

        y = gs.offset - btn_h - 6
        start_x = (gs.xSize - total_w) // 2

        self.btn_undo = UIButton(pygame.Rect(start_x + 0 * (btn_w + gap), y, btn_w, btn_h), "Undo")
        self.btn_reset = UIButton(pygame.Rect(start_x + 1 * (btn_w + gap), y, btn_w, btn_h), "Reset")
        self.btn_new = UIButton(pygame.Rect(start_x + 2 * (btn_w + gap), y, btn_w, btn_h), "New")
        self.btn_end = UIButton(pygame.Rect(start_x + 3 * (btn_w + gap), y, btn_w, btn_h), "End")
        self.btn_quit = UIButton(pygame.Rect(start_x + 4 * (btn_w + gap), y, btn_w, btn_h), "Quit")

    def draw_grid(self):
        """Draw game grid with walls and floor tiles."""
        for row in range(gs.gridSize):
            for col in range(gs.gridSize):
                x = col * gs.tileSize + gs.map_padding_x
                y = row * gs.tileSize + gs.map_padding_y

                if gs.grid[row][col] == 1:
                    gs.screen.blit(gs.wallImg, (x, y))
                else:
                    gs.screen.blit(gs.tileImg, (x, y))
                pygame.draw.rect(gs.screen, gs.grayColor, (x, y, gs.tileSize, gs.tileSize), 1)

    def draw_players(self):
        """Draw player sprites at their current positions."""
        x, y = gs.playerOnePos
        gs.screen.blit(gs.playerOneImg, (x * gs.tileSize + gs.map_padding_x, y * gs.tileSize + gs.map_padding_y))
        x, y = gs.playerTwoPos
        gs.screen.blit(gs.playerTwoImg, (x * gs.tileSize + gs.map_padding_x, y * gs.tileSize + gs.map_padding_y))

    def draw_boxes_portals(self):
        """Draw boxes and portal targets at their positions."""
        for x, y in gs.boxes:
            gs.screen.blit(gs.boxImg, (x * gs.tileSize + gs.map_padding_x, y * gs.tileSize + gs.map_padding_y))

        x, y = gs.portalOne
        gs.screen.blit(gs.portalOneImg, (x * gs.tileSize + gs.map_padding_x, y * gs.tileSize + gs.map_padding_y))
        x, y = gs.portalTwo
        gs.screen.blit(gs.portalTwoImg, (x * gs.tileSize + gs.map_padding_x, y * gs.tileSize + gs.map_padding_y))

    def draw_score(self):
        """Draw player scores in top corners."""
        textbox = self.customFontScore.render(f"P1: {gs.score[0]}", True, gs.P1_COLOR)
        rect = textbox.get_rect()
        rect.center = (gs.padding + rect.width / 2, gs.padding + gs.textSize / 2 - 9)
        gs.screen.blit(textbox, rect)

        textbox = self.customFontScore.render(f"P2: {gs.score[1]}", True, gs.P2_COLOR)
        rect = textbox.get_rect()
        rect.center = (gs.xSize - gs.padding - rect.width / 2, gs.padding + gs.textSize / 2 - 9)
        gs.screen.blit(textbox, rect)

    def draw_ready_state(self):
        """Draw ready indicators when players have submitted their moves."""
        if (self.ready & (1 << 0)) > 0:
            textbox = self.customFontReady.render("P1 ready", True, gs.P1_READY)
            rect = textbox.get_rect()
            rect.center = (gs.padding + rect.width / 2, gs.padding + gs.textSize / 2 + 11)
            gs.screen.blit(textbox, rect)

        if (self.ready & (1 << 1)) > 0:
            textbox = self.customFontReady.render("P2 ready", True, gs.P2_READY)
            rect = textbox.get_rect()
            rect.center = (gs.xSize - gs.padding - rect.width / 2, gs.padding + gs.textSize / 2 + 11)
            gs.screen.blit(textbox, rect)

    def _capture_state(self):
        """
        Capture current game state for undo functionality.
        
        Returns:
            Dictionary containing positions, boxes, scores, and move history
        """
        return {
            "playerOnePos": gs.playerOnePos,
            "playerTwoPos": gs.playerTwoPos,
            "boxes": copy.deepcopy(gs.boxes),
            "score": copy.deepcopy(gs.score),
            "last_score_turn": copy.deepcopy(gs.last_score_turn),
            "playerMove": copy.deepcopy(gs.playerMove),
            "playerDidMove": copy.deepcopy(gs.playerDidMove),
            "turn": gs.turn,
        }

    def _restore_state(self, state):
        """
        Restore game state from captured snapshot.
        
        Args:
            state: Previously captured game state dictionary
        """
        gs.playerOnePos = state["playerOnePos"]
        gs.playerTwoPos = state["playerTwoPos"]
        gs.boxes = copy.deepcopy(state["boxes"])
        gs.score = copy.deepcopy(state["score"])
        gs.last_score_turn = copy.deepcopy(state["last_score_turn"])
        gs.playerMove = copy.deepcopy(state["playerMove"])
        gs.playerDidMove = copy.deepcopy(state["playerDidMove"])
        gs.turn = state["turn"]

        self.ready, self.dxOne, self.dyOne, self.dxTwo, self.dyTwo = 0, 0, 0, 0, 0

    def undo_turn(self):
        """Undo the last turn by restoring previous game state."""
        if not self._undo_stack:
            return
        state = self._undo_stack.pop()
        self._restore_state(state)
        self.game_over = False

    def reset_game(self):
        """Reset game while keeping current map."""
        reset_game_state(False)
        self._undo_stack.clear()
        self.ready, self.dxOne, self.dyOne, self.dxTwo, self.dyTwo = 0, 0, 0, 0, 0
        self.game_over = False

    def new_game(self):
        """Start completely new game with fresh map."""
        reset_game_state(True)
        self._undo_stack.clear()
        self.ready, self.dxOne, self.dyOne, self.dxTwo, self.dyTwo = 0, 0, 0, 0, 0
        self.game_over = False
        
    def _in_grid(self, x: int, y: int) -> bool:
        """Check if coordinates are within grid bounds."""
        return 0 <= x < gs.gridSize and 0 <= y < gs.gridSize

    def _check_shift(self, x: int, y: int, dx: int, dy: int):
        """
        Check if boxes can be shifted in a direction and return indices.
        
        Args:
            x, y: Starting position
            dx, dy: Direction deltas
            
        Returns:
            List of box indices that can be shifted, empty if blocked
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
        Legacy method: attempt to change player position with box interaction.
        
        Args:
            curPos: Current position tuple
            dx, dy: Direction deltas
            
        Returns:
            True if movement resulted in action
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
                gs.last_score_turn[0] = gs.turn
            if gs.portalTwo in gs.boxes:
                gs.score[1] += 1
                gs.boxes.remove(gs.portalTwo)
                gs.last_score_turn[1] = gs.turn
            return len(shift_list) > 0 or not ((newX, newY) in gs.boxes)
        return False

    def _move(self, curPos, dx: int, dy: int):
        """Legacy method: calculate new position from delta."""
        x, y = curPos
        return (x + dx, y + dy)

    def _attempt_plan(self, curPos, dx: int, dy: int, blocked_cells: set):
        """
        Plan a single player move on current state.
        
        Args:
            curPos: Current player position
            dx, dy: Desired movement direction
            blocked_cells: Set of forbidden cells
            
        Returns:
            Dict with valid flag, new position, and list of box moves
        """
        if dx == 0 and dy == 0:
            return {"valid": False, "newPos": curPos, "box_moves": []}

        x, y = curPos
        nx, ny = x + dx, y + dy

        # Check bounds and walls
        if not self._in_grid(nx, ny) or gs.grid[ny][nx] == 1:
            return {"valid": False, "newPos": curPos, "box_moves": []}
        
        if (nx, ny) == gs.portalOne or (nx, ny) == gs.portalTwo:
            return {"valid": False, "newPos": curPos, "box_moves": []}

        # Check blocked cells
        if (nx, ny) in blocked_cells:
            return {"valid": False, "newPos": curPos, "box_moves": []}

        # Empty cell - free move
        if (nx, ny) not in gs.boxes:
            return {"valid": True, "newPos": (nx, ny), "box_moves": []}

        # Box pushing chain
        chain = []
        cx, cy = nx, ny
        while self._in_grid(cx, cy) and (cx, cy) in gs.boxes:
            chain.append((cx, cy))
            cx += dx
            cy += dy

        # Check destination for last box
        if not self._in_grid(cx, cy) or gs.grid[cy][cx] == 1:
            return {"valid": False, "newPos": curPos, "box_moves": []}
        if (cx, cy) in blocked_cells:
            return {"valid": False, "newPos": curPos, "box_moves": []}
        if (cx, cy) in gs.boxes:
            return {"valid": False, "newPos": curPos, "box_moves": []}

        # Build box moves in reverse order
        box_moves = []
        for bx, by in reversed(chain):
            box_moves.append(((bx, by), (bx + dx, by + dy)))

        return {"valid": True, "newPos": (nx, ny), "box_moves": box_moves}

    def _apply_all_box_moves_and_score(self, p1_box_moves, p2_box_moves):
        """
        Apply all box moves simultaneously and resolve scoring.
        
        Args:
            p1_box_moves: List of box moves by P1
            p2_box_moves: List of box moves by P2
        """
        new_boxes = list(gs.boxes)

        def apply_moves(moves):
            """
            Helper to apply a specific set of box moves.

            Args:
                moves (list): List of tuples specifying from and to positions.
            """
            nonlocal new_boxes
            for from_pos, to_pos in moves:
                if from_pos in new_boxes:
                    i = new_boxes.index(from_pos)
                    new_boxes[i] = to_pos

        apply_moves(p1_box_moves)
        apply_moves(p2_box_moves)

        gs.boxes = new_boxes

        # Score portals once after both players have moved
        if gs.portalOne in gs.boxes:
            gs.score[0] += 1
            gs.boxes.remove(gs.portalOne)
            gs.last_score_turn[0] = gs.turn
        if gs.portalTwo in gs.boxes:
            gs.score[1] += 1
            gs.boxes.remove(gs.portalTwo)
            gs.last_score_turn[1] = gs.turn

    def _move_players(self):
        """
        Execute simultaneous player movement with conflict resolution.
        
        Returns:
            Tuple of (p1_moved, p2_moved) booleans
        """
        p1_start = gs.playerOnePos
        p2_start = gs.playerTwoPos

        p1_intend = not (self.dxOne == 0 and self.dyOne == 0)
        p2_intend = not (self.dxTwo == 0 and self.dyTwo == 0)

        p1_target = (p1_start[0] + self.dxOne, p1_start[1] + self.dyOne)
        p2_target = (p2_start[0] + self.dxTwo, p2_start[1] + self.dyTwo)

        # Both players targeting same cell - cancel both
        if p1_intend and p2_intend and p1_target == p2_target:
            return False, False

        # Plan moves with empty blocked set to allow chase moves
        p1_plan = self._attempt_plan(p1_start, self.dxOne, self.dyOne, blocked_cells=set())
        p2_plan = self._attempt_plan(p2_start, self.dxTwo, self.dyTwo, blocked_cells=set())

        p1_end = p1_plan["newPos"] if p1_plan["valid"] else p1_start
        p2_end = p2_plan["newPos"] if p2_plan["valid"] else p2_start

        # Cancel if final positions overlap
        if p1_end == p2_end:
            return False, False

        p1_valid = p1_plan["valid"]
        p2_valid = p2_plan["valid"]

        # Cancel player if stepping into opponent's starting cell when opponent doesn't leave
        if p1_valid and p1_end == p2_start and (not p2_valid):
            p1_valid = False
            p1_end = p1_start
            p1_plan["box_moves"] = []

        if p2_valid and p2_end == p1_start and (not p1_valid):
            p2_valid = False
            p2_end = p2_start
            p2_plan["box_moves"] = []

        # Recheck overlap
        if p1_end == p2_end:
            return False, False

        # Resolve box conflicts
        p1_box_moves = p1_plan["box_moves"] if p1_valid else []
        p2_box_moves = p2_plan["box_moves"] if p2_valid else []

        p1_idx = {i for i, _ in p1_box_moves}
        p2_idx = {i for i, _ in p2_box_moves}

        # Same box target - cancel both
        if p1_idx & p2_idx:
            p1_valid = p2_valid = False
            p1_box_moves = p2_box_moves = []
            p1_end, p2_end = p1_start, p2_start

        # Different pushes to same cell - cancel both
        if p1_valid and p2_valid:
            p1_targets = {pos for _, pos in p1_box_moves}
            p2_targets = {pos for _, pos in p2_box_moves}
            if p1_targets & p2_targets:
                p1_valid = p2_valid = False
                p1_box_moves = p2_box_moves = []
                p1_end, p2_end = p1_start, p2_start

        # Box pushed into player - cancel pusher
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

        # Final overlap check
        if p1_end == p2_end:
            p1_valid = p2_valid = False
            p1_end, p2_end = p1_start, p2_start
            p1_box_moves = p2_box_moves = []

        # Commit position changes
        gs.playerOnePos = p1_end if p1_valid else p1_start
        gs.playerTwoPos = p2_end if p2_valid else p2_start

        # Apply box moves and scoring
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
            "T": config.move_limit,
            "maze": maze,
            "playerHist": gs.playerMove[player],
            "oppHist": gs.playerMove[not player],
            "playerScore": gs.score[player],
            "oppScore": gs.score[not player],
            "playerDidMove": gs.playerDidMove[player],
            "oppDidMove": gs.playerDidMove[not player],
        }
        return interactor.interact(config.filename[player], payload)

    def _resolve_turn_if_ready(self):
        """Execute turn resolution when both players have submitted moves."""
        if self.ready == 3:
            # Capture state before applying moves
            self._undo_stack.append(self._capture_state())

            # Run movement resolution
            m1, m2 = self._move_players()

            # Reset input state
            self.ready, self.dxOne, self.dyOne, self.dxTwo, self.dyTwo = 0, 0, 0, 0, 0

            # Record move history
            gs.playerMove[0] += self.keyOne
            gs.playerMove[1] += self.keyTwo

            # Record movement success
            gs.playerDidMove[0] += "1" if m1 else "0"
            gs.playerDidMove[1] += "1" if m2 else "0"

            gs.turn += 1
            if (gs.turn - 1) >= config.move_limit:
                self._end_game()

    def _end_game(self):
        """Determine winner and end game."""
        self.game_over = True
        if gs.score[0] > gs.score[1]:
            self.game_result_text = "P1 Wins!"
        elif gs.score[1] > gs.score[0]:
            self.game_result_text = "P2 Wins!"
        else:
            p1_last = gs.last_score_turn[0]
            p2_last = gs.last_score_turn[1]
            if gs.score[0] > 0 and p1_last < p2_last:
                self.game_result_text = "P1 Wins!"
            elif gs.score[1] > 0 and p2_last < p1_last:
                self.game_result_text = "P2 Wins!"
            else:
                self.game_result_text = "Draw!"
        self.ready, self.dxOne, self.dyOne, self.dxTwo, self.dyTwo = 0, 0, 0, 0, 0

    def handle_event(self, event: pygame.event.Event):
        """
        Handle game screen events including input and UI interaction.
        
        Returns:
            Navigation signal ("MENU", "INIT") or None
        """
        # UI button interactions
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_undo.hit(event.pos):
                self.undo_turn()
                return None
            if self.btn_reset.hit(event.pos):
                self.reset_game()
                return None
            if self.btn_new.hit(event.pos):
                return "INIT"
            if self.btn_end.hit(event.pos):
                self._end_game()
                return None
            if self.btn_quit.hit(event.pos):
                return "MENU"
                        
        # Game over handling
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                elif event.key == pygame.K_r:
                    self.reset_game()
                    return None
            return None

        both_bots = config.playerOneInteract and config.playerTwoInteract
        space_pressed = pygame.key.get_pressed()[pygame.K_SPACE]

        allow_bot_move = True
        if both_bots:
            current_time = pygame.time.get_ticks()
            if space_pressed and (current_time - self.last_bot_move_time >= config.BOT_DELAY_MS):
                self.last_bot_move_time = current_time
                allow_bot_move = True
            else:
                allow_bot_move = False

        # Player 1 input
        if (
            (not config.playerOneInteract)
            and event.type == pygame.KEYDOWN
            and event.key in config.P1_KEYS
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
            self.keyOne = config.P1_MAP[event.key]
        elif config.playerOneInteract and (self.ready & (1 << 0)) == 0:
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
            (not config.playerTwoInteract)
            and event.type == pygame.KEYDOWN
            and event.key in config.P2_KEYS
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
            self.keyTwo = config.P2_MAP[event.key]
        elif config.playerTwoInteract and (self.ready & (1 << 1)) == 0:
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
        """Render complete game screen with UI elements."""
        gs.screen.fill((0, 0, 0))
        self.draw_grid()
        self.draw_players()
        self.draw_boxes_portals()
        self.draw_score()
        self.draw_ready_state()

        # UI buttons
        mx, my = pygame.mouse.get_pos()
        self.btn_undo.draw(gs.screen, self.customFontUi, hovered=self.btn_undo.hit((mx, my)))
        self.btn_reset.draw(gs.screen, self.customFontUi, hovered=self.btn_reset.hit((mx, my)))
        self.btn_new.draw(gs.screen, self.customFontUi, hovered=self.btn_new.hit((mx, my)))
        self.btn_end.draw(gs.screen, self.customFontUi, hovered=self.btn_end.hit((mx, my)))
        self.btn_quit.draw(gs.screen, self.customFontUi, hovered=self.btn_quit.hit((mx, my)))

        # Remaining moves display
        remain = max(0, config.move_limit - (gs.turn - 1))
        _draw_text(
            gs.screen,
            f"Moves left: {remain}",
            self.customFontUi,
            gs.xSize // 2,
            gs.padding + 12,
            color=(180, 180, 180),
        )

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((gs.xSize, gs.ySize), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            gs.screen.blit(overlay, (0, 0))
            _draw_text(gs.screen, "GAME OVER", self.customFontScore, gs.xSize // 2, gs.ySize // 2 - 30)
            _draw_text(gs.screen, self.game_result_text, self.customFontScore, gs.xSize // 2, gs.ySize // 2 + 10)
            _draw_text(gs.screen, "Press R to Replay, ESC to Quit", self.customFontUi, gs.xSize // 2, gs.ySize // 2 + 50, color=(200, 200, 200))


