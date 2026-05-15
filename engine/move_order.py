from core.move import MoveFlag
from core.apply_move import applyMove, undoMove
from core.move_generator import generateMoves, generateQuiescence

def pieceValueOnSq(sq, gs):
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
    return pieceValueOnSq(move.to_sq, gs) * 10 - pieceValueOnSq(move.from_sq, gs) #times 10 to sort. 

#static exchange evaluation, returns expected material gain/loss 
def see(move, gs):
    capture_sq = move.to_sq
    capture_bb = 1 << capture_sq
    if not (move.flags & MoveFlag.CAPTURE):
        return 0

    #record a ;ist of values of pieces on the capture_sq
    if move.flags & MoveFlag.EN_PASSANT:
        gains = [100]
    else:
        gains = [pieceValueOnSq(capture_sq, gs)]
    
    if move.flags & MoveFlag.PROMOTION:
        gains[0] += 800

    #apply move
    applyMove(gs, move)
    depth = 1

    while True:
        #lva for the recapture
        lva_move = None
        lva = 100000
        for move in generateQuiescence(gs):
            if move.to_sq != capture_sq:
                continue
            value = pieceValueOnSq(move.from_sq, gs)
            if value < lva:
                lva = value
                lva_move = move
        
        if lva_move is None:
            break

        #if found, append the new value of the captured piece to the lsit
        gains.append(pieceValueOnSq(capture_sq, gs))
        applyMove(gs, lva_move)
        depth += 1
        #keep going until capture sequence is finished

    #undo all
    for _ in range(depth):
        undoMove(gs)

    score = 0
    for gain in reversed(gains[1:]):
        score = max(0, gain - score)

    return gains[0] - score

#improve mvvlva with see*
def _mvvlva_see(move, gs):
    victim = pieceValueOnSq(move.to_sq, gs)
    attacker = pieceValueOnSq(move.from_sq, gs)

    if victim > attacker: #skip see, expensive, classic mvv-lva
        return 1000000 + victim * 10 - attacker 
    else:#victim <= attacker = check see
        return 500000 #send bad captures that need see verification to the back
        #we are calling see on these moves twice at the moment.
        
        # see_score = see(move, gs)
        # if see_score >= 0:
        #     return 1000000 + see_score
        # else:
        #     return 500000 + see_score #bad captures are below killers/history, still ordered

#move scoring function for sorting
def _score_move(move, gs, killers, history):
    if move.flags & MoveFlag.CAPTURE:
        return _mvvlva_see(move, gs) 
    if killers and move == killers[0]: return 900000 #killer 1
    if killers and move == killers[1]: return 800000 #killer 2
    if history: return history[move.from_sq][move.to_sq]  #rest/quiet move history score
    return 0

def movesOrdered(moves, gs, known_best=None, killers=None, history=None):
    moves.sort(key=lambda m: _score_move(m, gs, killers, history), reverse=True)
    #last best move from depth -1 first in line
    if known_best is not None and known_best in moves:
        moves.remove(known_best)
        moves.insert(0, known_best)
    return moves
