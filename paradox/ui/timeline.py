"""The ghost timeline (depth design 2.2).

One row per ghost, laid out on a shared time axis: when it arrives, its
harmless phase-in, its lethal window, and where it despawns. A playhead
sweeps across as the loop runs.

The point is scheduling. Reacting to twelve sprites is reflex; seeing that
ghost 3 expires at 6.2s and ghost 5 arrives at 4.0s lets you plan the loop
around the gaps. Rows are coloured by decay tier so a row and the ghost it
describes read as the same object.
"""

import pygame

from paradox import config


def _dim(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int]:
    """Approximate an alpha over the near-black backdrop by scaling RGB.

    The strip sits on the window background, so this is visually identical
    to blending and costs no per-frame alpha surface.
    """
    k = alpha / 255.0
    return tuple(int(c * k) for c in color)


def draw(surface: pygame.Surface, ghosts: list, loop_t: float) -> None:
    if not config.TIMELINE_ENABLED or not ghosts:
        return

    rect = pygame.Rect(config.TIMELINE_RECT)

    # Time axis: long enough for every ghost's full life, and never shorter
    # than the loop so far — so a slow loop visibly stretches the timeline
    # rather than running the playhead off the end.
    span = max([g.gone_at for g in ghosts] + [loop_t, 1e-6])

    n = len(ghosts)
    row_h = min(config.TIMELINE_ROW_MAX, max(1, (rect.height - (n - 1) * config.TIMELINE_GAP) // n))
    total_h = n * row_h + (n - 1) * config.TIMELINE_GAP
    y = rect.top + (rect.height - total_h) // 2

    def x_at(t: float) -> int:
        return rect.left + int(rect.width * (t / span))

    # Newest ghost on top: the one whose path you just walked is the one you
    # remember, so it belongs where the eye lands first.
    for g in sorted(ghosts, key=lambda g: g.age):
        _, alpha = g.tier()
        row = pygame.Rect(rect.left, y, rect.width, row_h)

        pygame.draw.rect(surface, _dim(config.COLOR_GRID, 200), row)  # empty track

        # Phase-in: hollow, because it cannot hurt you yet.
        phase = pygame.Rect(x_at(g.delay), y, max(1, x_at(g.lethal_start) - x_at(g.delay)), row_h)
        pygame.draw.rect(surface, _dim(config.COLOR_MAGENTA, alpha // 3), phase, 1)

        # Lethal window: solid. A recording shorter than the phase-in never
        # becomes lethal at all, so guard the width.
        if g.lethal_end > g.lethal_start:
            lethal = pygame.Rect(
                x_at(g.lethal_start), y, max(1, x_at(g.lethal_end) - x_at(g.lethal_start)), row_h
            )
            pygame.draw.rect(surface, _dim(config.COLOR_MAGENTA, alpha), lethal)

        # Despawn tick: the gap you can plan to exploit.
        gx = min(x_at(g.gone_at), rect.right - 1)
        pygame.draw.rect(surface, _dim(config.COLOR_GREEN, alpha), (gx, y, 1, row_h))

        y += row_h + config.TIMELINE_GAP

    head = x_at(min(loop_t, span))
    pygame.draw.line(surface, config.COLOR_WHITE, (head, rect.top), (head, rect.top + rect.height))
