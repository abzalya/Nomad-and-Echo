from nomad.core.move import MoveFlag
from nomad.core.apply_move import applyMove, undoMove
from nomad.core.move_generator import generateMoves, generateQuiescence
from nomad.core.attacks import attackersTo

def pieceValueOnSq(sq, gs):
    bit = 1 << sq
    #ordered by frequency: pawns most common, queens least
    if (gs.whitePawns   | gs.blackPawns)   & bit: return 100
    if (gs.whiteKnights | gs.blackKnights) & bit: return 320
    if (gs.whiteBishops | gs.blackBishops) & bit: return 330
    if (gs.whiteRooks   | gs.blackRooks)   & bit: return 500
    if (gs.whiteQueens  | gs.blackQueens)  & bit: return 900
    return 0

PIECE_VALUE = [100, 320, 330, 500, 900, 10000]  #p, N, B, R, Q, K

def _mvvlva(move, gs):
    if not (move.flags & MoveFlag.CAPTURE):
        return 0
    #victim - attacker scoring
    return pieceValueOnSq(move.to_sq, gs) * 10 - pieceValueOnSq(move.from_sq, gs) #times 10 to sort. 

#static exchange evaluation, returns expected material gain/loss 
def see(move, gs):
    if not (move.flags & MoveFlag.CAPTURE):
        return 0
    
    capture_sq = move.to_sq
    capture_bb = 1 << capture_sq

    see_occ = (gs.whitePawns | gs.whiteKnights | gs.whiteBishops | gs.whiteRooks | gs.whiteQueens | gs.whiteKing   | gs.blackPawns   | gs.blackKnights | gs.blackBishops | gs.blackRooks | gs.blackQueens  | gs.blackKing)
    
    #record a ;ist of values of pieces on the capture_sq
    if move.flags & MoveFlag.EN_PASSANT:
        victim = 100
        ep_pawn_sq = capture_sq - 8 if gs.whiteToMove else capture_sq + 8
        see_occ ^= 1 << ep_pawn_sq
    else:
        victim = pieceValueOnSq(capture_sq, gs)

    gains = [victim]

    #promotion bonus: pawn becomes queen on capture_sq
    if move.flags & MoveFlag.PROMOTION:
        gains[0] += 800
        attacker_val = 900
    else:
        attacker_val = pieceValueOnSq(move.from_sq, gs)

    #remove initial attacker
    see_occ ^= 1 << move.from_sq

    white_recapture = not gs.whiteToMove # who is recapturing
    attackers = attackersTo(capture_sq, gs, see_occ) & see_occ #enemy attackers

    while True:
        #filter
        if white_recapture:
            own = (gs.whitePawns | gs.whiteKnights | gs.whiteBishops |
                   gs.whiteRooks | gs.whiteQueens  | gs.whiteKing)
            piece_bbs = [gs.whitePawns, gs.whiteKnights, gs.whiteBishops,
                         gs.whiteRooks, gs.whiteQueens, gs.whiteKing]
        else:
            own = (gs.blackPawns | gs.blackKnights | gs.blackBishops |
                   gs.blackRooks | gs.blackQueens  | gs.blackKing)
            piece_bbs = [gs.blackPawns, gs.blackKnights, gs.blackBishops,
                         gs.blackRooks, gs.blackQueens, gs.blackKing]

        recapture_attackers = attackers & own
        if not recapture_attackers: #no piece to recapture 
            break
        
        for piece, bb in enumerate(piece_bbs):
            lva = recapture_attackers & bb
            if lva:
                lva_sq = (lva & -lva).bit_length() - 1
                gains.append(attacker_val - gains[-1])
                attacker_val = PIECE_VALUE[piece]
                see_occ ^= 1 << lva_sq
                attackers = attackersTo(capture_sq, gs, see_occ) & see_occ
                break

        white_recapture = not white_recapture

    #see minimax fold
    while len(gains) > 1:
        gains[-2] = -max(-gains[-2], gains[-1])
        gains.pop()
    return gains[0]

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
