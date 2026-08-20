"""Boot screen: a lab terminal warming up a machine that probably isn't safe.

The REAL loading work happens here — CRT overlay, sprite pre-warm, fonts,
save file — one step per frame, so the progress bar animates instead of the
window freezing. The boot log types itself out meanwhile; each line's status
appears when its work step actually completes. Minimum time on screen so a
fast machine reads it as intentional, not as a flicker.
"""

import pygame

from paradox import config
from paradox.states.base import State
from paradox.states.menu import MenuState
from paradox.systems import save, sprites
from paradox.ui import crt
from paradox.ui.fonts import get_font


class LoadingState(State):
    def __init__(self):
        self.t = 0.0
        self.done_steps = 0
        self.ready = False
        self._skip_typing = False  # any key fast-forwards the typewriter
        self.lines = [
            "> INITIALIZING CONTAINMENT FIELD .........",
            "> CALIBRATING TEMPORAL RECORDER ..........",
            "> SPAWNING DIVERGENT INSTANCE BUFFER .....",
            "> ETHICS SUBROUTINE ......................",
            "> CHECKING FOR PREVIOUS OCCUPANTS ........",
            "> READY.",
        ]
        self._total_chars = sum(len(line) for line in self.lines)
        # One work step per boot line (READY has none). Order matters: the
        # sprite pre-warm is the heavy one, so it sits early in the bar.
        self._steps = [self._work_crt, self._work_sprites, self._work_fonts, self._work_ethics, self._work_save]
        self.statuses: list[str | None] = [None] * len(self._steps)

    # ---- the actual loading work ------------------------------------------

    def _work_crt(self) -> str:
        crt.get_overlay((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        return "OK"

    def _work_sprites(self) -> str:
        sprites.get_store()
        return "OK"

    def _work_fonts(self) -> str:
        for size in (config.FONT_TINY, config.FONT_SMALL, config.FONT_MID, config.FONT_BIG):
            get_font(size)
        return "OK"

    def _work_ethics(self) -> str:
        return "SKIPPED"

    def _work_save(self) -> str:
        runs = save.load().get("total_runs", 0)
        return f"{runs} FOUND" if runs else "NONE FOUND"

    # ---- typewriter bookkeeping ---------------------------------------------

    def _chars_typed(self) -> int:
        if self._skip_typing:
            return self._total_chars
        return int(self.t * config.BOOT_CPS)

    def _line_progress(self) -> tuple[int, int]:
        """(index of the line being typed, chars revealed on it)."""
        budget = self._chars_typed()
        for i, line in enumerate(self.lines):
            if budget < len(line):
                return i, budget
            budget -= len(line)
        return len(self.lines) - 1, len(self.lines[-1])

    # ---- state interface ------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type not in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            return
        if self.ready:
            self.manager.replace(MenuState())
        else:
            self._skip_typing = True  # impatience is allowed; the min-time still holds

    def update(self, dt: float) -> None:
        self.t += dt
        current_line, _ = self._line_progress()
        # Run at most one work step per frame, once its line is fully typed.
        if self.done_steps < len(self._steps) and current_line > self.done_steps:
            self.statuses[self.done_steps] = self._steps[self.done_steps]()
            self.done_steps += 1
        typed_all = self._chars_typed() >= self._total_chars
        work_done = self.done_steps >= len(self._steps)
        if not self.ready and typed_all and work_done and self.t >= config.LOADING_MIN_TIME:
            self.ready = True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        font = get_font(config.FONT_SMALL)
        current_line, current_chars = self._line_progress()
        x0, y0, line_h = 300, 200, 34

        for i, line in enumerate(self.lines):
            if i > current_line:
                break
            text = line if i < current_line else line[:current_chars]
            if i < len(self.statuses) and self.statuses[i] is not None and i < current_line:
                text = f"{line} {self.statuses[i]}"
            img = font.render(text, True, config.COLOR_GREEN)
            surface.blit(img, (x0, y0 + i * line_h))
            # Blinking block cursor at the end of the line being typed.
            if i == current_line and not self.ready and (self.t * 2) % 1 < 0.5:
                pygame.draw.rect(
                    surface, config.COLOR_GREEN, (x0 + img.get_width() + 5, y0 + i * line_h + 2, 11, 20)
                )

        # Segmented progress bar, one segment per real work step.
        n = len(self._steps)
        seg_w, gap = 52, 8
        bar_x = surface.get_width() // 2 - (n * seg_w + (n - 1) * gap) // 2
        for i in range(n):
            seg = pygame.Rect(bar_x + i * (seg_w + gap), 500, seg_w, 14)
            pygame.draw.rect(surface, config.COLOR_DIM_GREEN, seg, 1)
            if i < self.done_steps:
                pygame.draw.rect(surface, config.COLOR_GREEN, seg.inflate(-6, -6))

        if self.ready and (self.t * 1.6) % 1 < 0.62:
            prompt = font.render("[ PRESS ANY KEY ]", True, config.COLOR_HUD_DIM)
            surface.blit(prompt, prompt.get_rect(center=(surface.get_width() // 2, 566)))

        surface.blit(crt.get_overlay(surface.get_size()), (0, 0))
