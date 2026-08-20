"""State machine: a stack of screens.

A stack (not a single current state) so PAUSE can sit on top of PLAY and show
the frozen game underneath it (Phase 2). Only the top state receives events
and updates; every state in the stack draws, bottom-up.
"""

from abc import ABC, abstractmethod

import pygame


class State(ABC):
    manager: "StateManager | None" = None  # set by StateManager on push

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...


class StateManager:
    def __init__(self) -> None:
        self.stack: list[State] = []
        self.running = True

    def push(self, state: State) -> None:
        state.manager = self
        self.stack.append(state)

    def pop(self) -> None:
        self.stack.pop()
        if not self.stack:
            self.running = False

    def replace(self, state: State) -> None:
        """Swap the top state in place. This is how R-restart stays a one-frame
        action: the dead run is dropped and a fresh PlayState takes its slot,
        with no transition in between."""
        if self.stack:
            self.stack.pop()
        self.push(state)

    def reset_to(self, state: State) -> None:
        """Collapse the whole stack to a single state (e.g. back to the menu
        from a paused game, dropping both PAUSE and the PLAY underneath it)."""
        self.stack.clear()
        self.push(state)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.stack:
            self.stack[-1].handle_event(event)

    def update(self, dt: float) -> None:
        if self.stack:
            self.stack[-1].update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        for state in self.stack:
            state.draw(surface)
