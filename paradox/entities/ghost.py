"""Ghosts: past-you, replaying a recorded loop exactly. The core hazard."""

import pygame

from paradox import config
from paradox.systems import sprites
from paradox.systems.recorder import Recording


class Ghost:
    """Plays back one Recording in real time.

    Timeline: t runs from 0 the moment the loop starts. The ghost moves from
    frame one but is HARMLESS until t >= GHOST_PHASE_IN — the shrinking ring
    is that countdown made visible, so nothing that just materialized can
    kill you. It stays lethal until its recording runs out, then collapses
    and is gone for the rest of the loop. Fast previous loops make
    short-lived ghosts — that's the reward for playing clean.
    """

    def __init__(self, recording: Recording, age: int):
        self.recording = recording
        self.age = age  # 0 = your most recent loop; older ghosts decay visually
        self.t = 0.0
        self.despawn_t: float | None = None  # starts counting when the path ends

    def update(self, dt: float) -> None:
        if self.despawn_t is None:
            self.t += dt
            if self.t >= self.recording.duration:
                self.despawn_t = 0.0
        else:
            self.despawn_t += dt

    @property
    def expired(self) -> bool:
        return self.despawn_t is not None and self.despawn_t >= config.GHOST_DESPAWN_TIME

    @property
    def lethal(self) -> bool:
        return self.despawn_t is None and self.t >= config.GHOST_PHASE_IN

    def pos(self) -> tuple[float, float, float]:
        return self.recording.sample(self.t)

    def _tier(self) -> tuple[str, int]:
        """Decay variant + base alpha by AGE (loops since recorded), per ASSETS.md."""
        if self.age <= config.GHOST_FRESH_MAX_AGE:
            return "ghost_fresh", config.GHOST_ALPHA_TIERS[0]
        if self.age <= config.GHOST_WORN_MAX_AGE:
            return "ghost_worn", config.GHOST_ALPHA_TIERS[1]
        return "ghost_faded", config.GHOST_ALPHA_TIERS[2]

    def draw(self, surface: pygame.Surface) -> None:
        x, y, angle = self.pos()
        key, alpha = self._tier()
        frame = sprites.get_store()[key].frame_for(angle)

        if self.despawn_t is not None:
            # Collapse-out fade. (The portal-implosion effect lands in Phase 3.)
            k = 1.0 - self.despawn_t / config.GHOST_DESPAWN_TIME
            if k <= 0:
                return
            alpha = int(alpha * k)
        elif not self.lethal:
            # Phasing in: extra translucent while harmless.
            k = self.t / config.GHOST_PHASE_IN
            alpha = int(alpha * (0.35 + 0.65 * k))

        frame.set_alpha(alpha)
        surface.blit(frame, frame.get_rect(center=(x, y)))
        frame.set_alpha(255)  # cache frames are shared — leave them clean

        if self.despawn_t is None and not self.lethal:
            k = self.t / config.GHOST_PHASE_IN
            ring = config.GHOST_RING_START * (1.0 - k) + config.PLAYER_RADIUS * k
            pygame.draw.circle(surface, config.COLOR_MAGENTA, (x, y), ring, 1)
