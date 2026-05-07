#static position evaluation
#things to think about
#piece values
#the location of the pieces (some squares better some worse)
#Standard tables from (https://www.chessprogramming.org/Piece-Square_Tables).
#behaviour (pawn structures, passed pawns should be big +, king safety, open files for rooks)

from core.bitboard import iterateBits
from engine.psts import (PAWN_PST, KNIGHT_PST, BISHOP_PST, ROOK_PST,
                          QUEEN_PST, KING_MG_PST, KING_EG_PST)
from engine.pawn_eval_masks import FILE_MASKS, ADJACENT_FILES_MASKS, PASSED_MASKS

#stockfish type material
WHITE_PIECES = [
    ("whitePawns", 100), ("whiteRooks", 500), ("whiteKnights", 320),
    ("whiteBishops", 330), ("whiteQueens", 900)
]
BLACK_PIECES = [
    ("blackPawns", 100), ("blackRooks", 500), ("blackKnights", 320),
    ("blackBishops", 330), ("blackQueens", 900)
]

WHITE_PIECES_PSTS = [
    ("whitePawns", PAWN_PST), ("whiteRooks", ROOK_PST), ("whiteKnights", KNIGHT_PST),
    ("whiteBishops", BISHOP_PST), ("whiteQueens", QUEEN_PST)
]
BLACK_PIECES_PSTS = [
    ("blackPawns", PAWN_PST), ("blackRooks", ROOK_PST), ("blackKnights", KNIGHT_PST),
    ("blackBishops", BISHOP_PST), ("blackQueens", QUEEN_PST)
]

def _material_eval(gs):
    score = 0
    total_material = 0
    for attr, value in WHITE_PIECES:
        count = getattr(gs, attr).bit_count()
        score += count * value
        total_material += count * value
    for attr, value in BLACK_PIECES:
        count = getattr(gs, attr).bit_count()
        score -= count * value
        total_material += count * value
    return score, total_material

#postiion of the piece using piece square tables
def _position_eval(gs, total_material):
    score = 0
    for attr, pst in WHITE_PIECES_PSTS:
        for sq in iterateBits(getattr(gs, attr)):
            score += pst[sq]
    #for black PST[sq ^ 56] to mirror the table vertically
    for attr, pst in BLACK_PIECES_PSTS:
        for sq in iterateBits(getattr(gs, attr)):
            score -= pst[sq ^ 56]
    
    #mid/end game decision (tapered eval like stockfish)
    phase = min(total_material/2600, 1.0)
    #white king
    white_king_sq = next(iterateBits(gs.whiteKing))
    black_king_sq = next(iterateBits(gs.blackKing))
    score += (phase * KING_MG_PST[white_king_sq] + (1 - phase) * KING_EG_PST[white_king_sq])
    score -= (phase * KING_MG_PST[black_king_sq ^ 56] + (1 - phase) * KING_EG_PST[black_king_sq ^ 56])
    return score

#Pawn related penalty/bonuses
DOUBLED_PENALTY  = 20
ISOLATED_PENALTY = 20
PASSED_BONUS     = 60
PASSED_RANK_BONUS = [0, 10, 20, 40, 65, 100, 150, 0]


def _pawn_eval(gs):
    score = 0
    wp = gs.whitePawns
    bp = gs.blackPawns
    for sq in iterateBits(wp):
        file = sq % 8
        if (FILE_MASKS[file] & wp).bit_count() > 1:
            score -= DOUBLED_PENALTY
        if (ADJACENT_FILES_MASKS[file] & wp) == 0:
            score -= ISOLATED_PENALTY
        if (PASSED_MASKS[0][sq] & bp) == 0:
            rank = sq // 8
            score += PASSED_BONUS + PASSED_RANK_BONUS[rank]
    for sq in iterateBits(bp):
        file = sq % 8
        if (FILE_MASKS[file] & bp).bit_count() > 1:
            score += DOUBLED_PENALTY
        if (ADJACENT_FILES_MASKS[file] & bp) == 0:
            score += ISOLATED_PENALTY
        if (PASSED_MASKS[1][sq] & wp) == 0:
            rank = sq // 8
            score -= PASSED_BONUS + PASSED_RANK_BONUS[7 - rank]

    return score

#how would i do pawn structures, king safety, rook seeing the open file
def evaluate(gs):
    material_score, total_material = _material_eval(gs)
    position_score = _position_eval(gs, total_material)
    pawn_score = _pawn_eval(gs)
    return material_score + position_score + pawn_score

