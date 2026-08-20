# PARADOX — Verbs, Survival, and Sectors

> Successor to `PARADOX_depth_design.md`. Read Section 1 first.

---

## 1. Diagnosis: one verb

Right now the player's entire input vocabulary is a direction. Pickup happens on contact. Banking happens on contact. Space only skips the survey. There is no moment where the player *decides to do a thing* — only where they decide to be.

That is the whole reason it feels like a moving arrow. Art won't fix it. Difficulty won't fix it. The fix is more verbs, and a resource that makes those verbs cost something.

Target: **three verbs and one resource.** Not ten. Three verbs that interact well beats a menu of abilities nobody remembers.

---

## 2. Verb two — VENT (Space)

A short directional burst: ~150px over 0.15s, with invulnerability for its duration. 1.2s cooldown.

The design detail that matters: **your recording keeps the vent.** Your ghost vents too. A panic-dash now becomes a sudden unpredictable lunge in the same spot next loop, at the same timestamp, forever.

This is the whole game in one button. The escape that saves you today is the thing that kills you tomorrow, and you know it while you're pressing it.

- Costs **12 power** (§4). Cannot vent below that.
- The i-frames mean the skill ceiling is venting *through* a ghost rather than around it. Reward it: venting through a lethal ghost scores +150 and shakes the screen.
- Draw the vent as a hard streak with chromatic split, and draw ghost vents identically so they're recognisable a loop later.

---

## 3. Verb three — ECHO (E)

Drop a marker. It does nothing this loop.

**Next loop, at the same timestamp, that marker becomes a 3-second safe bubble** — ghosts pass through it without killing you.

You are leaving a gift for future-you, and you have to *be there at the right time* to collect it. Placing an echo at 0:14 means planning to be at that spot around 0:14 next loop, while also collecting cores and staying alive.

- **Two per loop.** Scarcity is what makes it a decision.
- During the next loop, show each pending echo as a dim ring with a countdown, so it's plannable rather than a surprise. It brightens as its window approaches, is live for 3s, then fades permanently.
- If you're not there, you wasted it. That's the game.

This is the brain mechanic from the last document, expressed as a button instead of arena furniture. Same idea as resonance gates, far less code, and fully under player control — which makes it better as the *first* thinking mechanic. Gates can come later as the environmental version.

---

## 4. The survival layer — POWER

This is the "survival scheme" you're after, and it fixes a structural hole: right now cores are optional. A skilled player could theoretically dodge forever and never collect anything. Nothing forces engagement.

A battery, 100 units, shown as a ring around the player and a bar in the HUD.

| State | Drain |
|---|---|
| Stationary | 1.5 /s |
| Moving | 4 /s, scaling to 9 /s at full speed |
| Vent | 12 flat |

| Gain | Amount |
|---|---|
| Core collected | +14 |
| Per core banked | +8 |
| Sector transition | full restore |

**Zero power is death**, with a distinct death cause so it never reads as a bug: `SYSTEM FAILURE — POWER EXHAUSTED`.

Warn hard below 25: the ring flashes, the audio drone detunes downward, the arena desaturates toward grey. The player should feel the lights going out.

### Why this is the right resource

It converts every existing decision into a two-sided one. "How long do I stay out?" now costs both ghost length *and* power. "Do I grab that far core?" is now also "can I afford the trip?" And carrying cores slows you, which drains less per second but takes longer overall — a genuinely non-obvious optimisation the player gets to discover.

### The elegant part: camping solves itself

Standing still is the cheapest way to conserve power. But standing still means **your ghost stands still too** — you've built a stationary pillar of death in that exact corner for every subsequent loop.

The game punishes hiding using nothing but its own core mechanic. No timer, no anti-camp rule, no zone that forces you out. Just consequence. Do not add a camping penalty; you already have one, and discovering it is a great moment.

---

## 5. The squeeze — RESIDUE

Ghost paths scar the floor permanently, on the same coarse grid as the core-placement heatmap (32x18, reuse it).

| Times crossed | Effect |
|---|---|
| 1-3 | Visual scarring only, faint magenta staining |
| 4-7 | Movement slowed 20% across the cell |
| 8+ | **Lethal**, from Sector III onward |

The arena visibly fills with your own history as the run goes on. It's automatic escalating difficulty that needs no tuning curve, it's entirely self-inflicted, and it makes late loops look spectacular — a floor almost entirely consumed by where you've been.

Lethal cells must telegraph: they pulse for 1.5s before arming the first time, and stay visually distinct forever after.

---

## 6. Levels — SECTORS

Group loops into blocks of five. Each sector has a name, a colour shift, one new mechanic, and a harder final loop. Between sectors: power fully restores, the draft offers a choice, and the player gets three seconds of quiet.

| Sector | Loops | Introduces | Palette shift |
|---|---|---|---|
| **I — CONTAINMENT** | 1-5 | VENT at loop 3 | Green |
| **II — CASCADE** | 6-10 | ECHO, residue begins | Green→amber |
| **III — COLLAPSE** | 11-15 | Residue turns lethal, arena contracts | Amber→magenta |
| **IV — SINGULARITY** | 16-20 | Resonance gates, sweep beams | Magenta |
| **V — ENDLESS** | 21+ | Everything, no new rules | Bleached white |

Each sector's final loop is a **containment event**: no new cores spawn, all ghosts run at once, and you survive a fixed 25 seconds to advance. Pure survival, no collection — a different verb balance for one loop, which makes the sector break feel like an actual break.

This gives you "levels that get harder" with identity, instead of an undifferentiated ramp where loop 14 feels like loop 13.

---

## 7. Deterministic hazards (Sector IV+)

Still no chasing enemies. The fairness contract holds: nothing kills the player that wasn't visible and predictable. But two additions are pure timing puzzles and fit cleanly.

**Sweep beam.** A containment beam crosses the arena on a fixed, visible schedule — a bright warning line 2s ahead, then the beam. Lethal, but perfectly learnable and identical every loop.

**Breach cells.** Grid cells that flash for 2s, go lethal for 1.5s, then reset, following a repeating pattern that's visible from the survey beat.

Both are learnable, both are the same every run, and neither ever reacts to the player. That's what keeps deaths feeling earned.

---

## 8. Complexity budget

The rules from the previous document still hold, updated:

- **Loops 1-2 stay pure.** Move, collect, bank. VENT arrives at 3.
- **Power is on from loop 1** — it's not a complication, it's the game's metabolism, and learning it late would feel like a rule change.
- One unlock at a time, announced in one line for 2 seconds.
- Never more than two active complications per loop, not counting power.
- Everything readable in under a second.
- Nothing lethal without 1.5s of visible warning. Residue and breach cells included.

---

## 9. Build order

**A.** POWER (§4) first, alone. It touches every existing decision and changes how the current game feels more than anything else here. Play ten runs before adding a verb — you may find the game is already substantially deeper.

**B.** VENT (§2). Make sure the vent lands in the recording and the ghost vents too — that's the point of it, and it's the easiest part to get wrong.

**C.** ECHO (§3).

**D.** RESIDUE (§5), visual scarring first, slow second, lethal last.

**E.** SECTORS (§6) as a structural pass over what exists.

**F.** Hazards (§7).

---

## 10. Acceptance criteria

- [ ] Power drains at three distinct documented rates and death by exhaustion has its own readout
- [ ] Below 25 power the game visibly and audibly degrades
- [ ] A vent performed by the player is reproduced exactly by that loop's ghost
- [ ] Venting through a lethal ghost is survivable, scores, and feels deliberate
- [ ] Echoes activate at their recorded timestamp ±window, and show a countdown beforehand
- [ ] Echoes are capped at two per loop and are lost if unused
- [ ] Residue accumulates on a grid, degrades movement before it degrades survival, and telegraphs before arming
- [ ] Sector transitions restore power, offer a draft, and visibly change the palette
- [ ] Containment-event loops end after a fixed survival duration with no collection
- [ ] Standing still remains mechanically viable but produces a stationary ghost hazard — no explicit anti-camp rule exists anywhere in the codebase
- [ ] Every system can be switched off in `config.py` and the game still runs
