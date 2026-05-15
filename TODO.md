#UI TODO
PYGAME UI - BENCHED
- [] game restart
- [] select colour
- [] move log on the side
- [] undo move
- [] end screen with the game restart button


#ENGINE priorities:
- search
    - [X] null move pruning
    - [2] check extensions
    - [3] futility pruning
    - [X] late move reduction
    - [5] aspiration windows
    - [6] repetition detection
- evaluation:
    - [X] pawn structure - doubled/isolated/passed pawns
    - [x] king safety - open files near king, pawn shield
    - [x] piece coordination - bishop pair, rook on open file, rook on 7th
        - connected rooks is expensive calculation. left out for now
    - [4] tapered eval
    - [5] mobility - count legal moves as a bonus, rewards active pieces
    - [6] endgame knowledge
- move ordering
    - [X] killer heuristic
    - [X] history heuristic
    - [X] static exchange eval (SEE) + delta pruning
    - [X] full pipeline - hash, capture (SEE) (good ones), killer, history, quiet (feeds LMR)
    - [?] staged move ordering ? 

- speed thoughts
    - Rewrite hot paths in C pybind11, almost 1 to 1 apart from syntax (if bottlenecking hard)
    - Bitboard attack tables — precomputed magic bitboards for slider attacks instead of ray tracing per call
    - [X] i built a ray attack pattern for pinned piece detection. i can reuse that, slightly modified for my slider pieces. not magic bitboards, but way faster than looping. need to implement

- profile optimizations
    - [X] Kill IntFlag. Replace MoveFlag with plain int constants
    - [X] Stop string-building attribute names. Find every getattr(gs, "white" + x) / getattr(gs, attr) in a hot loop and unroll into direct access.
    - [X] Capture-only move generator.
    - [X] Pin-mask legal generation. Cheaper than apply-undo legality check IMPLEMENT ASAP
    - [X] Apply same legal move generation to quiescense as its still pseudo-legal
    - [X] Killer moves + history heuristic
    - [X] Delta pruning + SEE in qsearch.
    - [7] Magic bitboards for sliding piece attacks