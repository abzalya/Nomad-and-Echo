from core.bitboard import iterateBits
from engine.psts import (PAWN_PST, KNIGHT_PST, BISHOP_PST, ROOK_PST,
                          QUEEN_PST, KING_MG_PST, KING_EG_PST)
from engine.pawn_eval_masks import FILE_MASKS, ADJACENT_FILES_MASKS, PASSED_MASKS
from core.attacks import PAWN_ATTACKS, KING_ATTACKS, EXTENDED_KING_ZONE
from engine.pawn_eval_hash import _pawn_eval_cache

#passed pawns bitmasks
#for sq in iterateBits(wp):
#         file = sq % 8
#         if (FILE_MASKS[file] & wp).bit_count() > 1:
#             score -= DOUBLED_PENALTY
#         if (ADJACENT_FILES_MASKS[file] & wp) == 0:
#             score -= ISOLATED_PENALTY
#         if (PASSED_MASKS[0][sq] & bp) == 0:
#             rank = sq // 8
#             score += PASSED_BONUS + PASSED_RANK_BONUS[rank]
#         #connected pawns
#         if (PAWN_ATTACKS[0][sq] & wp).bit_count() != 0:
#             score += CONNECTED_PAWNS_BONUS
#     for sq in iterateBits(bp):
#         file = sq % 8
#         if (FILE_MASKS[file] & bp).bit_count() > 1:
#             score += DOUBLED_PENALTY
#         if (ADJACENT_FILES_MASKS[file] & bp) == 0:
#             score += ISOLATED_PENALTY
#         if (PASSED_MASKS[1][sq] & wp) == 0:
#             rank = sq // 8
#             score -= PASSED_BONUS + PASSED_RANK_BONUS[7 - rank]
#         if (PAWN_ATTACKS[1][sq] & bp).bit_count() != 0:
#             score -= CONNECTED_PAWNS_BONUS


def passed_pawns(wp, bp):
    white_passed = 0
    black_passed = 0
    for sq in iterateBits(wp):
        if (PASSED_MASKS[0][sq] & bp) == 0:
            white_passed |= 1 << sq
    for sq in iterateBits(bp):
        if (PASSED_MASKS[1][sq] & wp) == 0:
            black_passed |= 1 << sq
    return white_passed, black_passed


#chebyshev distance
def chebyshev(sq1, sq2):
    r1, f1 = sq1 // 8, sq1 % 8
    r2, f2 = sq2 // 8, sq2 % 8
    return max(abs(r1 - r2), abs (f1 - f2))

KING_ESCORT_BONUS = 6
KING_BLOCK_BONUS = 4

# white_passed, black_passed = passed_pawns(gs.whitePawns, gs.blackPawns)
# wk_sq = gs.whiteKing.bit_length() - 1
# bk_sq = gs.blackKing.bit_length() - 1

def king_and_pawn(white_passed, black_passed, wk_sq, bk_sq):
    for sq in iterateBits(white_passed):
        queen_sq = sq | 56
        own_dist = chebyshev(wk_sq, queen_sq)
        score += (7 - own_dist) * KING_ESCORT_BONUS

        enemy_dist = chebyshev(bk_sq, queen_sq)
        score -= (7-enemy_dist) * KING_BLOCK_BONUS
    for sq in iterateBits(black_passed):
        queen_sq = sq & 7
        own_dist = chebyshev(bk_sq, queen_sq)
        score -= (7 - own_dist) * KING_ESCORT_BONUS
        
        enemy_dist = chebyshev(wk_sq, queen_sq)
        score += (7 - enemy_dist) * KING_BLOCK_BONUS

#rule of square, uncatchable pawns

def pawn_uncathable(p_sq, k_sq, p_color, side_to_move):
    p_file = p_sq % 8
    p_rank = p_sq // 8
    
    if p_color == WHITE:
        queen_sq = p_sq | 56
        distance = 7 - p_rank
        #double push counts as one move
        if p_rank == 1:
            distance = 5
    else:
        queen_sq = p_sq & 7
        distance = p_rank
        if p_rank == 6:
            distance = 5
    
    king_dist = chebyshev(k_sq, queen_sq)
    
    # If pawn's side to move, extra tempo
    if side_to_move == p_color:
        return king_dist > distance
    else:
        return king_dist > distance + 1
    
UNCATCHABLE_PAWN_BONUS = 600

# side_to_move = WHITE if gs.whiteToMove else BLACK

def unchatable_pawns(white_passed, black_passed, wk_sq, bk_sq, side_to_move):
    for sq in iterateBits(white_passed):
        if pawn_uncathable(sq, bk_sq, WHITE, side_to_move):
            score += UNCATCHABLE_PAWN_BONUS
    for sq in iterateBits(black_passed):
        if pawn_uncathable(sq, wk_sq, BLACK, side_to_move):
            score -= UNCATCHABLE_PAWN_BONUS

#connected passers

CONNECTED_PASSED_BONUS = 50 #per pawn, but 2 connected are about twice as strong*

def connected_passers(white_passed, black_passed):
    for sq in iterateBits(white_passed):
        file = sq % 8
        if ADJACENT_FILES_MASKS[file] & white_passed:
            score += CONNECTED_PASSED_BONUS
    for sq in iterateBits(black_passed):
        file = sq % 8
        if ADJACENT_FILES_MASKS[file] & black_passed:
            score -= CONNECTED_PASSED_BONUS