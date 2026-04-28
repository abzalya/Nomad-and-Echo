1. CHECK Board state representation (piece locations)
2. CHECK Render the board
3. CHECK Turn management
4. CHECK Piece movement (pseudo-legal)
5. Special moves — castling, en passant, pawn double push, promotion
6. CHECK Legal move generation (filter moves that leave king in check, pins)
7. CHECK Check detection
8. Checkmate & stalemate detection
9. Draw conditions (50-move rule, threefold repetition)
10. CHECK Highlight legal moves
11. Game result display


checkmate and stalemate should be easy
if legalMoves is emply then game over
if in check then checkmate else stalemate
write that up

draw conditions
insufficient material is easy
50-move and threefold need history add later

