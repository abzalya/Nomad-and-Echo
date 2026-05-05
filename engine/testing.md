# Engine Testing Log

## Tools
- **cutechess-cli** - auto testing suite (stockfish limited to 1320)
- **Ordo** - elo 

---

## Version history

| Tag | Description | ELO |
|-----|-------------|-----|
| Nomad-v0.1 | Material + PST eval, negamax with alpha-beta | N/A |


## Leightweigh Testing game played in pygame with debug printing of depth, NPS and time

| Tag | Depth | NPS | Notes |
|-----|-------|-----| ----- | 
| Nomad-v0.1 | 3 | ~10k -> ~1.5k | NPS degrading as the position has more legal moves|

Game: engine = black
e2e4 e7e5 g1f3 d7d6 d2d4 c8g4 d4e5 g4f3 d1f3 d6e5
f1c4 g8f6 f3b3 d8e7 b1c3 c7c6 c1g5 b7b5 c3b5 c6b5
c4b5 b8d7 e1c1 a8d8 d1d7 d8d7 h1d1 e7e6 b5d7 f6d7
b3b8 d7b8 d1d8

mini tests:
After move 16 (b3b8) — engine should see the forced mate
After move 9 (c1g5) — test that it finds the knight sacrifice on b5
After move 22 (a8d8) — material is even, positional test