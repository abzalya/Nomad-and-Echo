1. CHECK Board state representation (piece locations)
2. CHECK Render the board
3. CHECK Turn management
4. CHECK Piece movement (pseudo-legal)
5. Special moves — castling, en passant, pawn double push, promotion
6. CHECK Legal move generation (filter moves that leave king in check, pins)
7. CHECK Check detection
8. CHECK Checkmate & stalemate detection
9. Draw conditions (50-move rule, threefold repetition)
10. CHECK Highlight legal moves
11. SEMI-CHECK Game result display

draw conditions
insufficient material is easy
50-move and threefold need history add later

12. need to add some UI
- game restart
- select colour
- move log on the side
- undo move
- end screen with the game restart button


ENGINE
1. position evaluation.
- piece costs
- extra points for positions of knights and kings all pieces really

2. minimax + alpha-beta