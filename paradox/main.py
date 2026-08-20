"""Entry point: window, clock, and the state-machine loop."""

import pygame

from paradox import config
from paradox.states.base import StateManager
from paradox.states.loading import LoadingState


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()

    manager = StateManager()
    manager.push(LoadingState())  # boot chain: LOADING -> MENU -> PLAY

    while manager.running:
        # Delta time in seconds, clamped: dragging the window on Windows can
        # stall the loop for seconds, and an unclamped dt would teleport the
        # player and fast-forward every ghost through a wall of its path.
        dt = min(clock.tick(config.FPS) / 1000.0, config.MAX_FRAME_DT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                manager.running = False
            else:
                manager.handle_event(event)

        manager.update(dt)
        manager.draw(screen)
        pygame.display.flip()

    pygame.quit()
