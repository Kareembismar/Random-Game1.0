"""Path recording and playback — the machine that turns you into the enemy.

A Recording is a list of timestamped positions, appended once per frame while
you play. Playback never steps "one sample per frame": a ghost asks for its
position at an elapsed TIME and gets a point interpolated between the two
samples around that time. That keeps ghosts framerate-independent — a path
recorded at 60 FPS replays identically if the game later runs at 30 or 144.
"""

import bisect


class Recording:
    """One finished loop's path. Immutable once created."""

    def __init__(self, ts: list[float], xs: list[float], ys: list[float], angles: list[float]):
        self.ts = ts
        self.xs = xs
        self.ys = ys
        self.angles = angles
        self.duration = ts[-1] if ts else 0.0

    def sample(self, t: float) -> tuple[float, float, float]:
        """(x, y, angle) at time t, clamped to the recording's range."""
        if not self.ts:
            return 0.0, 0.0, 0.0
        if t <= 0.0:
            return self.xs[0], self.ys[0], self.angles[0]
        if t >= self.duration:
            return self.xs[-1], self.ys[-1], self.angles[-1]
        i = bisect.bisect_right(self.ts, t)  # first sample strictly after t
        t0, t1 = self.ts[i - 1], self.ts[i]
        # How far through this segment we are (guard against dt=0 duplicates).
        f = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
        x = self.xs[i - 1] + (self.xs[i] - self.xs[i - 1]) * f
        y = self.ys[i - 1] + (self.ys[i] - self.ys[i - 1]) * f
        # Angle snaps to the segment's end value: lerping angles wraps badly
        # around ±pi and facing is cosmetic anyway.
        return x, y, self.angles[i]


class Recorder:
    """Accumulates the current loop's samples, then hands over a Recording."""

    def __init__(self) -> None:
        self.start(0.0, 0.0, 0.0)

    def start(self, x: float, y: float, angle: float) -> None:
        self.t = 0.0
        self.ts = [0.0]
        self.xs = [x]
        self.ys = [y]
        self.angles = [angle]

    def add(self, dt: float, x: float, y: float, angle: float) -> None:
        self.t += dt
        self.ts.append(self.t)
        self.xs.append(x)
        self.ys.append(y)
        self.angles.append(angle)

    def finish(self) -> Recording:
        return Recording(self.ts, self.xs, self.ys, self.angles)
