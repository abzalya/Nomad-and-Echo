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

## VS

| Matchup | Result | Notes |
|---------|--------|-------|
| v0.1 vs v0.2 | v0.2 wins 100-0 | v0.1 ignores clock, times out every game |
| v0.2 vs v0.3 | v0.3 wins 55-45 | Marginal, LOS 15.9% — not significant. Both still drain clock |

## Leightweigh Testing game played in pygame with debug printing of depth, NPS and time

| Tag | Depth | NPS | Notes |
|-----|-------|-----| ----- | 
| Nomad-v0.1 | 3 | ~10k -> ~1.5k | NPS degrading as the position has more legal moves|
| Nomad-v0.4 | 3 |  ~1,662 | |
| Nomad-v0.5(wip) | 3 | ~3150  | apply-undo instead of copy |
| Nomad-v0.5 | 3 | ~8090 | pypy3 as interpreter |
| Nomad-v0.6(wip) | 3 | ~37924 | pseudo-legal moves and lazy legality |


Game: engine = black
e2e4 e7e5 g1f3 d7d6 d2d4 c8g4 d4e5 g4f3 d1f3 d6e5
f1c4 g8f6 f3b3 d8e7 b1c3 c7c6 c1g5 b7b5 c3b5 c6b5
c4b5 b8d7 e1c1 a8d8 d1d7 d8d7 h1d1 e7e6 b5d7 f6d7
b3b8 d7b8 d1d8

mini tests:
After move 16 (b3b8) — engine should see the forced mate
After move 9 (c1g5) — test that it finds the knight sacrifice on b5
After move 22 (a8d8) — material is even, positional test