#static position evaluation
#things to think about
#piece values
#the location of the pieces (some squares better some worse)
#Standard tables from (https://www.chessprogramming.org/Piece-Square_Tables).
#behaviour (pawn structures, passed pawns should be big +, king safety, open files for rooks)

from core.bitboard import iterateBits
from engine.psts import (PAWN_PST, KNIGHT_PST, BISHOP_PST, ROOK_PST,
                          QUEEN_PST, KING_MG_PST, KING_EG_PST)

#stockfish type material
WHITE_PIECES = [
    ("whitePawns", 100), ("whiteRooks", 500), ("whiteKnights", 320),
    ("whiteBishops", 330), ("whiteQueens", 900), ("whiteKing", 20000)
]
BLACK_PIECES = [
    ("blackPawns", 100), ("blackRooks", 500), ("blackKnights", 320),
    ("blackBishops", 330), ("blackQueens", 900), ("blackKing", 20000)
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
        if attr != "whiteKing":
            total_material += count * value
    for attr, value in BLACK_PIECES:
        count = getattr(gs, attr).bit_count()
        score -= count * value
        if attr != "blackKing":
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


#how would i do pawn structures, king safety, rook seeing the open file
def evaluate(gs):
    material_score, total_material = _material_eval(gs)
    position_score = _position_eval(gs, total_material)
    return (material_score + position_score)/100

