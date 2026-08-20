# PARADOX — Depth Design

> Give to Claude Code with the earlier specs. Read Section 1 before implementing anything;
> it's the reasoning that makes the rest coherent rather than a pile of features.

---

## 1. The principle

The game already contains a deep mechanic that is currently being wasted.

**The player writes the level.** Every loop you play authors the hazard for the next one. That's the premise — but right now it's *passive*. The path is a byproduct of doing something else. You're thinking "get core, get core, reach portal," and the route you leave behind is an accident you'll be annoyed by later.

Making that authorship **intentional** is the entire difference between an arcade game and a thinking game. The target mental state is:

> "If I loop wide left to grab that core, I'm putting a wall across the whole left side for the next three loops. Is that core worth it?"

Everything below serves that one sentence. Features that don't feed it are noise, however clever they sound.

A second principle, equally important: **complexity must be earned, not front-loaded.** Loops 1-3 stay exactly as they are today — move, collect, bank. Each new system unlocks at a stated loop, one at a time, with a one-line on-screen introduction. A player must be able to reach loop 4 without reading anything.

---

## 2. Layer one — make the invisible visible

Cheapest changes, biggest immediate shift. Nothing here adds a rule; it exposes information the game already has. Both convert reflex into planning.

### 2.1 The path you are currently writing

Render the current loop's recorded path as a thin, dim magenta line trailing behind the player — capped at the last ~200 samples so it fades out behind you.

That is the wall you are building. Right now the player cannot see it, so they cannot reason about it. One rendering change and every movement decision becomes visibly consequential.

Keep it dim (alpha ~35). It should read as a suggestion in peripheral vision, not clutter.

### 2.2 The ghost timeline

A horizontal bar across the bottom of the HUD, one thin row per active ghost. Each row shows that ghost's phase-in window, its lethal window, and where it despawns. A playhead sweeps left to right as the loop runs.

Now the player can see that ghost 3 expires at 6.2s and ghost 5 arrives at 4.0s — and can *plan the loop around the gaps*. This is the single highest-leverage addition in this document. It costs one UI widget and it changes the game from reaction to scheduling.

Colour each row to match its decay tier so the timeline and the arena read as the same objects.

### 2.3 Survey beat (loop 5+)

Before each loop begins, hold for up to 3 seconds: arena visible, cores placed, each ghost's starting position marked with a dim outline and its first second of path drawn as a faint line. Player presses Space (or waits it out) to begin.

Three seconds of looking converts panic into decision. Only from loop 5 — earlier loops don't need it and it would slow the opening.

---

## 3. Layer two — routing becomes a real problem

### 3.1 Resonance chain (loop 6+)

Cores spawn numbered `1..N` with the number drawn on them. Collect in ascending order and a chain multiplier builds: `+0.25x` per correctly-ordered pickup, on top of the existing carry multiplier. Grab one out of order and the chain resets to zero — but you keep the core.

Suddenly the arena is a travelling-salesman problem being solved in real time under a moving threat. The optimal collection order and the safe collection order are different, and choosing between them is the game.

Draw a faint line between consecutive-numbered cores so the intended route is legible at a glance.

### 3.2 Volatile cores (loop 8+)

One or two cores per loop spawn with a visible countdown ring (12 seconds). Bank a volatile core in time for **3x its value**. Let it expire while carried and it detonates: you lose everything currently held, but survive.

This forces prioritisation. The greed hook currently asks "how many can I hold?" — volatiles add "and in what order do I need to cash them?"

### 3.3 Heavy cores (loop 10+)

Some cores are worth double and apply triple the movement mass penalty from the Phase 2 spec. Taking one is a commitment: you are slow now, and the sluggish path you're about to walk becomes next loop's ghost.

---

## 4. Layer three — the headline mechanic

**This is the one worth building. Everything above is good; this is the reason the game exists.**

### Resonance gates (loop 7+)

Place a **gate** — a barrier segment across part of the arena, impassable and lethal to touch — and a matching **plate** somewhere else on the floor. The gate is open only while a ghost is standing on its plate.

So on loop 7, you deliberately route yourself across plate B at around the nine-second mark. On loop 8, your ghost from loop 7 stands on plate B at nine seconds — and the gate opens exactly then, for exactly as long as you lingered.

**Your past self stops being only a hazard and becomes a tool you have to program in advance.**

This is the mechanic that makes the title honest. It turns the core loop from "avoid your history" into "choreograph with your history," and it demands genuine forward planning: to open a gate at second 9 of the next loop, you must be somewhere specific at second 9 of *this* one, while also collecting cores and staying alive.

Implementation notes:

- Gate and plate share a colour and an ID letter. Draw a dim connecting line between them so the relationship is unmissable.
- **Any** ghost on the plate opens the gate, not just the newest. With six ghosts you get chaotic partial openings — which is good, and readable via the timeline from §2.2.
- The player standing on a plate does **not** open its own gate. The whole point is that only your past can open your way forward.
- Gates never spawn such that the portal or a core is unreachable if no gate opens. Verify reachability at spawn time with a flood fill; regenerate the layout if it fails. This must be an assertion in code, not a hope.
- Start with exactly one gate/plate pair. Two pairs from loop 11. Never more than three.

Show the plate's "occupied" state loudly — plate lights up, gate visibly retracts with a sound. The player must be able to learn the rule by accident, in one observation, without a tutorial.

---

## 5. Layer four — the divergence draft (loop 4+)

Between loops, offer three cards. Pick one. **Every option trades present advantage against future difficulty** — the game's theme expressed as a decision.

| Card | Now | Later |
|---|---|---|
| **COMPRESS** | Cores worth 25% less this loop | Next ghost's recording is 35% shorter |
| **SURGE** | +80% move speed this loop | Next ghost also moves at +80% |
| **PURGE** | Delete your oldest ghost permanently | No carry multiplier this loop |
| **OVERSPAWN** | 4 extra cores, all double value | Arena shrinks 40px permanently |
| **MIRROR** | Cores worth +50% this loop | Next ghost walks your path mirrored |
| **ANCHOR** | Portal stops relocating this loop | Next loop spawns two ghosts from this recording |

MIRROR is the most interesting one — it creates a hazard that is recognisably yours but spatially wrong, which is both mechanically novel and thematically perfect.

Draw three at random from the pool, weighted so early loops offer gentler trades. Show the pick on the HUD for the loop it affects.

This is what makes runs different from each other, which is what makes people start a fourth one.

---

## 6. Layer five — intersections (loop 9+)

Crossing a ghost's **trail** — the line it has already drawn this loop — at a point where the ghost is not currently standing scores an **intersection**: +50, chaining to +100, +200, +400 within a 2-second window.

Deliberately weaving through the wake of your own history, timed to the gap behind each ghost, is the highest skill expression the game can offer. It reads as showing off, which is exactly what a scoring system should reward at the top end.

Combine with near-miss detection from the Phase 2 spec (still unbuilt) and the ceiling gets very high.

---

## 7. The complexity budget — protect this

More systems is not more depth. Depth is *decisions per second that matter*; complexity is *rules the player must hold in memory*. These trade against each other.

Hard rules:

- **Loops 1-3 add nothing.** They are the game as it exists today. This is the tutorial and it must stay clean.
- **One unlock at a time**, at the stated loop, announced with a single centred line for 2 seconds. Never two new systems in the same loop.
- **Maximum two active complications per loop.** If gates and volatile cores are both live, do not also run a resonance chain that loop. Rotate them.
- **Every system must be readable in under one second.** If a player has to stop and parse the screen, they die, and it feels like the UI killed them rather than a ghost.
- **Nothing may be lethal without being visible for 1.5 seconds first.** This applies to gates too — a gate closing on the player must telegraph.

Suggested unlock ladder:

```
1-3   pure movement + collection            (as today)
4     divergence draft
5     survey beat
6     resonance chain
7     resonance gates            <- the big one
8     volatile cores
9     intersections
10    heavy cores
11    second gate pair
```

---

## 8. Build order

**A.** Finish the outstanding items first: swept collision, `GLOW_ALPHA = 150`, ghost stagger, near-miss detection. Depth built on a game that occasionally fails to register a collision is wasted work.

**B.** Layer one entirely (§2). Path rendering, timeline, survey beat. Play ten runs before adding anything else — these three alone may change the game more than you expect, and they change what the later systems should feel like.

**C.** Divergence draft (§5). Self-contained, high replay value, no interaction with arena geometry.

**D.** Resonance gates (§4). The reachability flood-fill is the hard part; do it properly.

**E.** Resonance chain, volatile cores, intersections, heavy cores (§3, §6) — in unlock order, one per commit.

---

## 9. Acceptance criteria

- [ ] A player can reach loop 4 without reading any instructions
- [ ] The current loop's path is visible while playing, dim enough not to clutter
- [ ] The ghost timeline correctly shows phase-in, lethal window and despawn for every active ghost
- [ ] Resonance gates open **only** for ghosts, never for the player
- [ ] A flood-fill assertion guarantees the portal and every core remain reachable in the worst case where no gate opens
- [ ] No loop ever runs more than two active complications
- [ ] Each unlock announces itself once, in one line, for two seconds
- [ ] Nothing becomes lethal without 1.5 seconds of visible warning
- [ ] Draft cards state their future cost as plainly as their present benefit
- [ ] The game is still fully playable and readable with every system disabled via `config.py`
