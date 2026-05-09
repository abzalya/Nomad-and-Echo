from core.move import MoveFlag
from core.move_generator import legalMoves, captureMovesOnly
from core.apply_move import applyMove, undoMove
from core.attacks import isSquareAttacked

def _pieceValueOnSq(sq, gs):
    bit = 1 << sq
    #ordered by frequency: pawns most common, queens least
    if (gs.whitePawns   | gs.blackPawns)   & bit: return 100
    if (gs.whiteKnights | gs.blackKnights) & bit: return 320
    if (gs.whiteBishops | gs.blackBishops) & bit: return 330
    if (gs.whiteRooks   | gs.blackRooks)   & bit: return 500
    if (gs.whiteQueens  | gs.blackQueens)  & bit: return 900
    return 0

def _mvvlva(move, gs):
    if not (move.flags & MoveFlag.CAPTURE):
        return 0
    #victim - attacker scoring
    return _pieceValueOnSq(move.to_sq, gs) * 10 - _pieceValueOnSq(move.from_sq, gs) #times 10 to sort. 

def movesOrdered(moves, gs, known_best=None):
    moves.sort(key=lambda m: _mvvlva(m, gs), reverse=True)
    #last best move from depth -1 should be first in line
    #remove from list and insert at front
    if known_best is not None and known_best in moves:
        moves.remove(known_best)
        moves.insert(0, known_best)
    return moves
