# A list of what stockfish does to be, well, stockfish

Source: https://www.chessprogramming.org/Stockfish#Search

---

## Board Representation
- 8x8 Board
- Bitboards with Little-Endian Rank-File Mapping (LERF)
- Magic Bitboards
- BMI2 - PEXT Bitboards *(not recommended for AMD Ryzen prior to Zen 3)*
- Piece-Lists *(until Stockfish 12)*

---

## Classical Evaluation
- Tapered Eval
- Score Grain: ~1/256 of a pawn unit

### Material
- Point Values
  - Midgame: 198, 817, 836, 1270, 2521
  - Endgame: 258, 846, 857, 1278, 2558
- Bishop Pair
- Imbalance Tables
- Material Hash Table

### Piece-Square Tables

### Space & Mobility
- Space
- Mobility
- Trapped Pieces
- Rooks on (Semi) Open Files
- Outposts

### Pawn Structure
- Pawn Hash Table
- Backward Pawn
- Doubled Pawn
- Isolated Pawn
- Phalanx
- Connected Pawns
- Passed Pawn

### King Safety
- Attacking King Zone
- Pawn Shelter
- Pawn Storm
- Square Control

### Evaluation Patterns

---

## Search
- Iterative Deepening
- Aspiration Windows
- Improving Heuristic
- Parallel Search using Threads
  - YBWC *(prior to Stockfish 7)*
  - Lazy SMP *(since Stockfish 7, January 2016)*
- Principal Variation Search

### Transposition Table
- Shared Hash Table
- 10 Bytes per Entry, 3 Entries per Cluster
- Depth-preferred Replacement Strategy
- No PV-Node probing
- Prefetch

### Move Ordering
- Continuation History
- Counter Moves History *(since Stockfish 7, January 2016)*
- Capture History
- History Heuristic
- MVV/LVA
- SEE

### Selectivity

#### Extensions
- Restricted Singular Extensions
- Capture Extensions

#### Pruning
- Futility Pruning
- Move Count Based Pruning
- Null Move Pruning
- Dynamic Depth Reduction based on depth and value
- Static Null Move Pruning
- Verification search at high depths
- ProbCut
- SEE Pruning

#### Reductions
- Late Move Reductions
- Internal Iterative Reductions
- Razoring

### Quiescence Search
