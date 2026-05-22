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

def king_and_pawn(gs):
    white_passed, black_passed = passed_pawns(gs.whitePawns, gs.blackPawns)
    wk_sq = gs.whiteKing.bit_length() - 1
    bk_sq = gs.blackKing.bit_length() - 1
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