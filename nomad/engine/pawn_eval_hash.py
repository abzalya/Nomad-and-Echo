#Pawn eval is a slow part of my evaluation, it is only dependent on pawns and therefore doesnt change as much
#repeated positions with the same pawn strcuture are common enough to hit 80%+ hitrate in middle games
from nomad.core.bitboard import iterateBits
from nomad.engine.pawn_eval_masks import FILE_MASKS, ADJACENT_FILES_MASKS, PASSED_MASKS
from nomad.core.attacks import PAWN_ATTACKS

_SIZE = 1 << 20  #1M slots
_PAWN_TT   = [None] * _SIZE

def _pawn_eval_cache(gs):
    key = gs.pawnHash
    idx = key & ((1<<20) - 1)
    entry = _PAWN_TT[idx]
    if entry is not None and entry[0] == key:
        return entry[1]
    score = _pawn_eval(gs)
    _PAWN_TT[idx] = (key, score)
    return score

#moved from eval.py
#Pawn related penalty/bonuses
DOUBLED_PENALTY  = 20
ISOLATED_PENALTY = 20
PASSED_BONUS     = 60
PASSED_RANK_BONUS = [0, 10, 20, 40, 65, 100, 150, 0]
CONNECTED_PAWNS_BONUS = 10
PAWN_ISLAND_PENALTY = 10

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
        #connected pawns
        if (PAWN_ATTACKS[0][sq] & wp).bit_count() != 0:
            score += CONNECTED_PAWNS_BONUS
    for sq in iterateBits(bp):
        file = sq % 8
        if (FILE_MASKS[file] & bp).bit_count() > 1:
            score += DOUBLED_PENALTY
        if (ADJACENT_FILES_MASKS[file] & bp) == 0:
            score += ISOLATED_PENALTY
        if (PASSED_MASKS[1][sq] & wp) == 0:
            rank = sq // 8
            score -= PASSED_BONUS + PASSED_RANK_BONUS[7 - rank]
        if (PAWN_ATTACKS[1][sq] & bp).bit_count() != 0:
            score -= CONNECTED_PAWNS_BONUS
    #pawn islands
    wislands = _pawn_islands(wp)
    bislands = _pawn_islands(bp)
    if wislands >> 1:
        score -= (wislands - 1) * PAWN_ISLAND_PENALTY
    if bislands >> 1:
        score += (bislands - 1) * PAWN_ISLAND_PENALTY
    return score

def _pawn_islands(bb):
    occupied_files = 0
    for file in range(8):
        if FILE_MASKS[file] & bb:
            occupied_files |= (1 << file)
    #count 0 to 1 transitions
    islands, prev = 0, 0
    for file in range(8):
        bit = (occupied_files >> file) & 1
        if bit and not prev:
            islands += 1
        prev = bit
    return islands