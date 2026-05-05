from core.move import MoveFlag
from core.move_generator import legalMoves, captureMovesOnly
from core.apply_move import applyMove, undoMove
from core.attacks import isSquareAttacked

PIECE_VALUES = {
    "Pawns": 100, "Knights": 320, "Bishops": 330,
    "Rooks": 500, "Queens": 900
}

def _pieceValueOnSq(sq, gs):
    bit = 1 << sq
    for name, val in PIECE_VALUES.items():
        if getattr(gs, "white" + name) & bit or getattr(gs, "black" + name) & bit:
            return val
    return 0

def _mvvlva(move, gs):
    if not (move.flags & MoveFlag.CAPTURE):
        return 0
    #victim - attacker scoring
    return _pieceValueOnSq(move.to_sq, gs) * 10 - _pieceValueOnSq(move.from_sq, gs) #times 10 to sort. 

def movesOrdered(moves, gs):
    moves.sort(key=lambda m: _mvvlva(m, gs), reverse=True)
    return moves
