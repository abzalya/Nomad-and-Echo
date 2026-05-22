# Engine Testing Log

## Tools
- **cutechess-cli** - auto testing suite (stockfish limited to 1320)
- **Ordo** - elo 

---

## Version history

| Tag | Description | ELO |
|-----|-------------|-----|
| Nomad-v0.1 | Material + PST eval, negamax with alpha-beta | N/A |
| Nomad-v0.2 | + Iterative deepening, time management, quiescence search, MVV-LVA move ordering. | 1 W / 99 L (98 on time) |
| Nomad-v0.3 | + Transposition table via Zobrist hashing. TT move ordering silently broken | 0 W / 100 L (all on time) |
| Nomad-v0.4 | Fix: time check granularity 1024 → 128 nodes. Fix: TT move ordering now works. | 0 W / 99 L / 1 D (62 on time, 37 checkmates) |
| Nomad-v0.5 | using pypy as interpreter | 67 W / 28 L / 5 D (zero time forfeits) |
| Nomad-v0.6 | pseudo-legal + lazy legality + some move_gen optimizations | 82 W / 10 L / 8 D |
| Nomad-v0.8 | MoveFlag int constants, capture-only quiescence gen | 71 W / 28 L / 1 D vs SF1500, 48 W / 47 L / 5 D vs SF1600, 40 W / 52 L / 8 D vs SF1700 APPROX ELO ~1600|
| Nomad-v0.9 | pin-mask legal generation + classical bitboard ray attacks | this version has a gamebreaking color asymmetry bug. details below in the vs|
| Nomad-v0.10pre | killer + history heuristic move ordering | ELO + 195 +- 55 over 0.8. identical logic to 0.9 suggests the abnormal result of 0.9 vs 0.8 is due to slower engine + noise|
| Nomad-v0.10 | killer + history heuristic move ordering | 57 - 41 - 2 vs SF1700 Estimated ELO ~1756 |
| Nomad-v0.11 | SEE + Delta pruning | ELO ~+40 over v0.10. Could be noise  |
| Nomad-v0.12 | LMR | ~+34 ELO over v0.11. Due to large regression observed on the first round, I investigated the cause by isolating features one by one. RFP and lazy eval has contributed some by calling evaluate at every node. lazy eval helped but not as much. RFP was not cutting enough nodes to be worth it. Slowing the engine down too much and loosing performance. These features need to be tuned one by one and added slowly. Adding all at the same time was a mistake. Next is to add PVS which should help RFP and Razoring. |
| Nomad-v0.13 | PVS  + RFP, Razoring (re-enabled) | Good start as an improveemnt over v0.12. This will serve as a foundation for the re-enabled RFP, razoring. Re-enable one by one and confirm improvement before committing and tagging. Re-enabled RFP on top of PVS has shown to be an improvement. Adding Razoring on top is neutral. OK to keep.|
| Nomad-v0.14 | Aspiration Windows | +49 Elo, LOS 94.6% over v0.13 |
| Nomad-v0.15 | Check Extensions + Pawn Hash Table | +45.4 ELO, LOS 93% over v0.14 |
| Nomad-v0.16 | komodo opening book | ~ +21 ELO LOS 77%|

## VS

| Matchup | Result | Notes |
|---------|--------|-------|
| v0.1 vs v0.2 | v0.2 wins 100-0 | v0.1 ignores clock, times out every game |
| v0.2 vs v0.3 | v0.3 wins 55-45 | Marginal, LOS 15.9% — not significant. Both still drain clock |
| v0.7 vs v0.6 | current wins 53.5–46.5 | 12 W / 5 L / 83 D. High draw rate (83%) from 3-fold repetition. |
| v0.8 vs v0.7 |  wins 69–31 | 56 W / 18 L / 26 D. Elo +139.0 ±62.3, LOS 100%. |
| v0.9 vs v0.8 | as white: 12-2-36, as black: 7-34-9 | there is a massive color assymetry. possible bug affecting black. |
| v0.10pre vs v0.8 | 56 - 5 - 39 | ELO + 195 +- 55. identical logic to v0.9 suggests 0.9 "bug" is simply a slower engine affecting black play way harder + some noise|
| v0.11 vs v0.10 | 39 - 33 - 28 | some struggles with slower SEE, managed to make it faster and saw slight improvement on play strength. Not massive elo wise, but should be really good in general.  |
| v0.12pre vs v0.11 | 21W - 63L - 16D (29.0%), Elo difference -155.5 ± 68.6, LOS 0.0%. | regression, 0.12pre is about 155 Elo weaker than v0.11. |
| v0.13pre vs v0.12| 48 - 31 - 21 | +59.6 over v0.12, LOS 97.2% |
| v0.13pre (PVS+RFP) vs v0.13pre (PVS only)| 41 - 30 - 29 | +38, LOS 90% |
| v0.13 vs v0.13pre(PVS+RFP) | 40 - 37 - 23 | Neutral, Keep. |
| v0.14 vs v0.13 | 45 - 31 - 24 | Aspiration windows are an improvement. Interestingly, slightly more dominant as black. |
| v0.15 vs v0.14 | 45 - 32 - 23  | Small improvement. My only incoming changes are going to be tweaks to time management and opening books. This might be the last algorithm changes before v1.0 |
| v0.16 vs v0.15 | 36 - 30 - 34  | Opening book adds a little bit, but the high drawrate indicates the close match strength wise. Expected.  |

## Claude Profile

Workload: 2 positions (Opera middlegame + startpos), depth 4 each. cProfile under PyPy with JIT
disabled — absolute times are slower than real-engine play; relative deltas and hotspot ranking
are what's trustworthy. NPS values are from the engine's own `info` lines during the same
workload, with JIT on.

| Stage | Wall time | Calls | Notes |
|-------|-----------|-------|-------|
| baseline (~v0.7) | 15.09s | 27.04M | Top hotspots: `generateMoves` 13%, sliding rays combined 17%, `applyMove` 9%, `isSquareAttacked` 6%. **Surprises**: `enum.IntFlag.__and__` 6.3% and `getattr` builtin 3.1% — both stdlib overhead from how `MoveFlag` and string-keyed attribute access were written. |
| + IntFlag → int, getattr unrolled, apply/undo unrolled | 9.86s | 13.89M | −35% wall, −49% calls. `IntFlag` and `getattr` drop out of the top 25 entirely. `applyMove` −34%, `undoMove` −25%. Downstream wins on `isSquareAttacked` (−25%) and ray attacks (−30%) just from less surrounding overhead. |
| v0.8 (+ generateQuiescence: captures + EP + all promotions) | 8.32s | 11.98M | −45% cumulative wall. NPS doubled at startpos (8,499 → 17,511) and +74% at middlegame (3,257 → 5,658) in the actual engine. New top: sliding rays still ~15%, `applyMove` 9%, `generateQuiescence` ~10% (replaces the old pseudo-legal generate-and-filter pattern). |
| main pre-v0.9 (legal generator for `generateMoves`: pin masks, check detection, attacked_bb king filter) | 8.74s | 13.18M | Effectively neutral wall time vs v0.8 (within noise). **The big shifts**: `applyMove` calls −33% (74K → 50K), `isSquareAttacked` calls −75% (123K → 31K). New hotspot `attackedBy` at 0.59s / 54K calls. Upfront pin/check cost in `generateMoves` (+18% self-time) roughly cancels the per-move savings — break-even because most nodes only have ~10 moves and only ~1 illegal. EP-discovered-check edge case bug surfaced in tournament (1 illegal-move forfeit, "h5g5" — fxg3 wasn't generated as legal in single-check because `check_mask` only contained the checker's square, not the EP destination). |
| v0.9pre (+ legal `generateQuiescence` with pin masks + king attack filter, EP-only legality check everywhere) | 8.82s | 13.78M | Wall time still neutral (within noise). `isSquareAttacked` drops out of top 25 entirely — EP-only legality check is doing its job. **Architectural win, not a perf win**: bookkeeping shifted from per-move (per applyMove cycle) to per-node (one `findPinnedPieces` + one `attackedBy` upfront). `generateQuiescence` self-time jumped 0.55s → 0.79s, cumulative 1.21s → 2.11s — pin/attack work added inside. `findPinnedPieces` is now visible at 0.27s. Together `generateQuiescence` + `generateMoves` are 42% of total runtime; both bottle-necked on the slider ray-walk loops that v0.10 will replace. EP-discovered-check bug fixed. |
| v0.9 (+ classical-bitboard slider attacks via `RAY_ATTACKS`, unified `rayAttack` helper) | 8.56s | 14.63M | −3% wall, **+4% NPS startpos d4** (17,771 → 18,471), +2.6% NPS middlegame (5,243 → 5,379). Per-ray cost dropped from ~720 ns to ~290 ns (≈2.5×). `negativeRayAttacks` + `positiveRayAttacks` ray-walking versions gone. `attackedBy` cumulative −26% (1.77s → 1.31s) because it calls slider attacks repeatedly. **New top hotspot is `evaluate` at 25% of wall** — `_position_eval` / `_pawn_eval` / `_king_eval` iterating bitboards. The next target if you keep pushing. |
| v0.10pre (+killer & history heuristic move ordering) | N/A - running on a different machine | 9.6M | -34% of total calls. -64% negamax and -40% quiescence calls. Massive downstream gains on all other function calls as well due to earlier beta-cutoffs. Play strength TBD|
| main (v0.12pre: +LMR +RFP +Razoring +FP +lazy eval) vs v0.11 | — (proportional only) | 3.21M vs 3.63M | **Pure proportional comparison, main vs v0.11.** Node count at opening pos depth 4: **8,962 vs 13,852 (−35%)** — LMR is working as advertised. Tree-expansion functions all fall: `applyMove` −0.6pp, `generateQuiescence` −1.1pp, `quiescence` own −0.8pp, `generateMoves` −0.3pp, `see` −0.4pp. Eval-related % rises because RFP calls `evaluate()` at the top of every interior node: `iterateBits` +1.6pp, `_position_eval` +1.6pp, `_pawn_eval` +0.8pp. Eval-per-call cost flat (~3.6µs) — pure call-count increase, not regression. **Lazy eval firing rate only 14.4%** (1,583 / 10,968 evaluate calls short-circuit); `LAZY_MARGIN=300` is too conservative given typical expensive-term swing ~150–200cp. Lowering to 200 should ~2–3× the firing rate. Hotspot ranking is unchanged from v0.11 — additive search-side change, no eval regression. |
| v0.13pre (+PVS +aspiration, RFP/Razoring tuned, FP off) | 1.153s | 2.73M | Same workload. −39% wall vs v0.12pre with ~same node count → ~40% faster per node. PVS scout windows narrowed everything: `generateQuiescence` calls −37%, `quiescence` calls −13%, `applyMove` calls −9%. Lazy eval firing rate up to **22%** (margin 200 + is_endgame guard). Eval still dominates at ~47% of total — pawn hash is next. |
| + pawn hash (initial impl had 2 bugs: wrong piece indices in initial compute, plus incorrect side-to-move toggle — both fixed) | 1.169s | 2.73M | Wall time flat but **`_pawn_eval` dropped from 7.9% → <0.9% of runtime (−87%)** and fell out of top 25. `_pawn_islands` also dropped out. Cache hit rate ~90%+ on the ~10.6k non-lazy eval calls. Savings converted into more search depth: **Opera d4 nodes 8,614 → 11,771 (+37%)**, NPS up 27%, depth-4 score moved from cp 165 → cp 210 (more confident, deeper-informed). The expected "speed → depth" loop fired exactly as intended. |