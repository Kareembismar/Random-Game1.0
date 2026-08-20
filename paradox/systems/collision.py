"""Swept (continuous) collision between two moving points.

Testing only end-of-frame positions is a tunneling bug waiting to happen: at
420px/s the player covers 7px per frame, and a ghost coming the other way
covers 7px too, so a head-on pass moves 14px of relative distance per frame
against a 17px kill radius. That is survivable today, but every planned
speed modifier (SURGE +80%, OVERCLOCK x1.75, desync x1.15) and every dropped
frame (dt is clamped at 50ms = 21px per step) pushes the step past the
radius, at which point the player walks through a ghost untouched.

So instead of asking "are they overlapping right now?", ask "how close did
they get at any point during this frame?" — both points move in a straight
line over the frame, so the answer is a one-variable minimum of a quadratic,
solved in closed form below. The same number also drives near-miss
detection, which means a graze and a kill are measured by the identical
quantity and can never disagree.
"""

import math


def closest_approach(
    p0: tuple[float, float],
    p1: tuple[float, float],
    g0: tuple[float, float],
    g1: tuple[float, float],
) -> tuple[float, float]:
    """Minimum distance between two points moving linearly over one frame.

    p0 -> p1 and g0 -> g1 are the frame's start/end positions. Returns
    (min_distance, s) where s in [0, 1] is the fraction of the frame at which
    that minimum occurred — s is what lets callers place a graze effect at
    the point the two actually passed each other.
    """
    # Work in the ghost's frame of reference: the gap vector and how it moves.
    dx = p0[0] - g0[0]
    dy = p0[1] - g0[1]
    rvx = (p1[0] - p0[0]) - (g1[0] - g0[0])
    rvy = (p1[1] - p0[1]) - (g1[1] - g0[1])

    # |gap(s)|^2 is a parabola in s; its vertex is where they're closest.
    a = rvx * rvx + rvy * rvy
    if a <= 1e-12:  # no relative motion this frame — the gap is constant
        return math.hypot(dx, dy), 0.0
    s = -(dx * rvx + dy * rvy) / a
    s = 0.0 if s < 0.0 else (1.0 if s > 1.0 else s)  # clamp: the vertex may
    # lie outside this frame, in which case the nearest point is an endpoint
    return math.hypot(dx + rvx * s, dy + rvy * s), s
