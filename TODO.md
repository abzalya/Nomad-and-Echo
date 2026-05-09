1. CHECK Board state representation (piece locations)
2. CHECK Render the board
3. CHECK Turn management
4. CHECK Piece movement (pseudo-legal)
5. CHECK Special moves — castling, en passant, pawn double push, promotion
6. CHECK Legal move generation (filter moves that leave king in check, pins)
7. CHECK Check detection
8. CHECK Checkmate & stalemate detection
9. CHECK Draw conditions (50-move rule, threefold repetition)
10. CHECK Highlight legal moves
11. CHECK Game result display

#UI TODO
12. need to add some UI
- game restart
- select colour
- move log on the side
- undo move
- end screen with the game restart button


#ENGINE priorities:
- search
    - [X] null move pruning
    - [2] check extensions
    - [3] futility pruning
    - [4] late move reduction
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
    - [1] killer heuristic
    - [2] history heuristic
    - [3] static exchange eval (SEE)
    - [4] full pipeline - hash, capture (SEE), killer, history, quiet (feeds LMR)


- speed thoughts
    - Rewrite hot paths in C pybind11, almost 1 to 1 apart from syntax (if bottlenecking hard)
    - Bitboard attack tables — precomputed magic bitboards for slider attacks instead of ray tracing per call

- profile optimizations
    - [X] Kill IntFlag. Replace MoveFlag with plain int constants
    - [X] Stop string-building attribute names. Find every getattr(gs, "white" + x) / getattr(gs, attr) in a hot loop and unroll into direct access.
    - [X] Capture-only move generator.
    - [4] Pin-mask legal generation. Cheaper than apply-undo legality check IMPLEMENT ASAP
    - [5] Killer moves + history heuristic
    - [6] Magic bitboards for sliding piece attacks
    - [7] Delta pruning + SEE in qsearch.