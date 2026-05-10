"""
Main Game Application Entry Point.

This module initializes the pygame framework, orchestrates the various screens
(Menu, Init, Game, Tutorial), and runs the primary event loop.
"""
import pygame
from setup import gameSetup as gs

import core.config as config
from core.menu_screen import MenuScreen
from core.init_screen import InitScreen
from core.game_screen import GameScreen
from core.tutorial_screen import TutorialScreen
from core.utils import reset_game_state

def recreate_init_screen(old_init):
    """
    Reinstantiate the initialization screen while capturing previous settings.
    
    Clones player toggle flags, bot difficulty rankings, move constraints, 
    and map generation parameters seamlessly from the obsolete menu instance 
    so configuration profiles aren't lost upon returning from other interfaces.
    
    Args:
        old_init: The exact prior `InitScreen` object serving as the config template.
        
    Returns:
        InitScreen: A freshly constructed screen instance pre-filled with historic values.
    """
    new_init = InitScreen()
    if old_init:
        new_init.p1_is_bot = old_init.p1_is_bot
        new_init.p2_is_bot = old_init.p2_is_bot
        new_init.p1_diff = old_init.p1_diff
        new_init.p2_diff = old_init.p2_diff
        new_init.move_limit = old_init.move_limit
        new_init.map_mode = old_init.map_mode
        new_init.map_size = old_init.map_size
    return new_init

def main():
    """Main game loop managing state transitions between menu, init, and game screens."""
    menu = MenuScreen()
    init = InitScreen()
    game = GameScreen()
    tutorial = TutorialScreen()

    mode = "MENU"
    running = True
    # mode = "GAME"

    while running:
        gs.clock.tick(60)

        if mode == "GAME" and config.playerOneInteract and config.playerTwoInteract:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if mode == "MENU":
                sig = menu.handle_event(event)
                if sig == "PLAY":
                    init = recreate_init_screen(init)
                    mode = "INIT"
                elif sig == "TUTORIAL":
                    mode = "TUTORIAL"

            elif mode == "TUTORIAL":
                if tutorial.handle_event(event) == "BACK":
                    mode = "MENU"

            elif mode == "INIT":
                sig = init.handle_event(event)
                if sig == "BACK":
                    menu = MenuScreen()
                    mode = "MENU"
                elif sig == "START":
                    reset_game_state(True)
                    game = GameScreen()
                    mode = "GAME"

            else:
                signal = game.handle_event(event)
                if signal == "MENU":
                    menu = MenuScreen()
                    mode = "MENU"
                elif signal == "INIT":
                    init = recreate_init_screen(init)
                    mode = "INIT"

        if mode == "MENU":
            menu.draw()
        elif mode == "TUTORIAL":
            tutorial.draw()
        elif mode == "INIT":
            init.draw()
        else:
            game.draw()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
