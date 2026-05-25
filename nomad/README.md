# Nomad

I’ve long been fascinated with the game of chess, and I’ve wanted to make my own chess engine for a while. Something about making mine own engine to beat me at something I do all the time sounded fun.
I also wanted a somewhat approachable project to push me hard but still do it without ANY assitance of LLM's that we see so often. I mean, Claude would be able to code this up in 5 minutes and probably end up being much better than what I will have.

The product is Nomad, a python chess-engine build from the ground up.

**Current version: v1.0** | Estimated strength: **~1900–2000 Elo**  
Runtime: PyPy | Protocol: UCI

---

## Techniques implemented

### Board representation & move generation
- Bitboard representation (little-endian)
- Classical ray attacks (sliding pieces)
- Pin masks and check masks computed at generation time
- Strict-legal move generation (no pseudo-legal filtering loop)
- Separate `generateQuiescence` for captures + promotions
- `attackersTo` for fast SEE

### Search
- Negamax with alpha-beta pruning
- Iterative deepening
- Principal variation search (PVS) — scout `[-α-1, -α]`, re-search on fail-high
- Late move reductions (LMR)
- Null move pruning (R = 2/3, zugzwang-gated)
- Killer moves (2 slots per ply)
- History heuristic
- MVV-LVA move ordering
- Static exchange evaluation (SEE)
- 3-fold repetition detection with contempt

### Quiescence search
- Captures + promotions only
- Stand-pat pruning
- SEE pruning (skipped when in check)
- Delta pruning (skipped in endgame)
- Promotion bonus in SEE and delta thresholds
- Full move generation on check evasions
- Depth cap

### Evaluation
- Material counting
- Piece-square tables with tapered middlegame/endgame interpolation
- Pawn islands penalty
- King safety (zone-based)
- Rook evaluation
- Endgame detection via material threshold
- Lazy evaluation

### Infrastructure
- Zobrist hashing
- Transposition table
- UCI protocol
- Basic time management

---

## Possible v2.0 improvements

| Feature | Expected gain | Notes |
|---|---|---|
| Texel tuning of eval weights | +30–80 Elo | Needs labeled dataset + optimization loop. High-value item. |
| Magic bitboards | Speed | Rewrite of `attacks.py`; modest gain on PyPy but clean ceiling for a C port |
| Aspiration windows | +10–20 Elo | Cheap to add; narrows the search window on each ID iteration |
| Check extensions | +15–25 Elo | Fixes tactical horizon on forcing lines |
| Pawn hash table | +10–20 Elo | Caches expensive pawn eval; translates to extra depth |
| Better time management | +10–20 Elo | Soft/hard limits, instability bonus, easy-move savings |
| Singular extensions | +5–15 Elo | Extend when one move is uniquely good |
| Continuation history / counter-move heuristic | +5–15 Elo | Better quiet-move ordering; prerequisite for safe futility pruning |
| King safety attack-unit model | Eval quality | Full rewrite of the king eval term |
| Personalized opening book | +50–100 effective Elo vs web players | Built from chess.com PGNs; the engine never blunders the opening |
| Syzygy endgame tablebases | Accuracy | Mostly matters in 6-piece endings; low priority for web play |
| NNUE | Large | Requires training pipeline + GPU. Out of scope for a pure-Python project |
| Lazy SMP | Throughput | Python GIL kills threading; multiprocessing with shared TT is possible but complex |

---

## Resources

- [Building a Static Chess Engine](https://www.armand.dev/blog/static-chess-engine/)
- [Chess Programming Wiki](https://www.chessprogramming.org/Main_Page)
- [donna_opening_books](https://github.com/michaeldv/donna_opening_books) — Polyglot opening book format reference
- `python-chess` `polyglot.py` — Polyglot reader reference
