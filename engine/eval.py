#static position evaluation

from core.bitboard import iterateBits
from engine.psts import (PAWN_PST, KNIGHT_PST, BISHOP_PST, ROOK_PST,
                          QUEEN_PST, KING_MG_PST, KING_EG_PST)
from engine.pawn_eval_masks import FILE_MASKS, ADJACENT_FILES_MASKS, PASSED_MASKS
from core.attacks import PAWN_ATTACKS, KING_ATTACKS, EXTENDED_KING_ZONE

def _material_eval(gs):
    wp = gs.whitePawns.bit_count()   * 100
    wr = gs.whiteRooks.bit_count()   * 500
    wn = gs.whiteKnights.bit_count() * 320
    wb = gs.whiteBishops.bit_count() * 330
    wq = gs.whiteQueens.bit_count()  * 900
    bp = gs.blackPawns.bit_count()   * 100
    br = gs.blackRooks.bit_count()   * 500
    bn = gs.blackKnights.bit_count() * 320
    bb = gs.blackBishops.bit_count() * 330
    bq = gs.blackQueens.bit_count()  * 900
    white_total = wp + wr + wn + wb + wq
    black_total = bp + br + bn + bb + bq
    return white_total - black_total, white_total + black_total

ENDGAME_THRESHOLD = 3600

#postiion of the piece using piece square tables
def _position_eval(gs, total_material):
    score = 0
    for sq in iterateBits(gs.whitePawns):   score += PAWN_PST[sq]
    for sq in iterateBits(gs.whiteRooks):   score += ROOK_PST[sq]
    for sq in iterateBits(gs.whiteKnights): score += KNIGHT_PST[sq]
    for sq in iterateBits(gs.whiteBishops): score += BISHOP_PST[sq]
    for sq in iterateBits(gs.whiteQueens):  score += QUEEN_PST[sq]
    #for black PST[sq ^ 56] to mirror the table vertically
    for sq in iterateBits(gs.blackPawns):   score -= PAWN_PST[sq ^ 56]
    for sq in iterateBits(gs.blackRooks):   score -= ROOK_PST[sq ^ 56]
    for sq in iterateBits(gs.blackKnights): score -= KNIGHT_PST[sq ^ 56]
    for sq in iterateBits(gs.blackBishops): score -= BISHOP_PST[sq ^ 56]
    for sq in iterateBits(gs.blackQueens):  score -= QUEEN_PST[sq ^ 56]
    
    #mid/end game decision (tapered eval like stockfish)
    phase = min(total_material/ENDGAME_THRESHOLD, 1.0)
    #white king
    white_king_sq = next(iterateBits(gs.whiteKing))
    black_king_sq = next(iterateBits(gs.blackKing))
    score += (phase * KING_MG_PST[white_king_sq] + (1 - phase) * KING_EG_PST[white_king_sq])
    score -= (phase * KING_MG_PST[black_king_sq ^ 56] + (1 - phase) * KING_EG_PST[black_king_sq ^ 56])
    return score, phase

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

OPEN_FILE_BONUS = 25
ROOK_ON_SEVENTH_BONUS = 20
CONNECTED_ROOKS_BONUS = 15

def _rook_eval(gs):
    score = 0
    wr = gs.whiteRooks
    br = gs.blackRooks
    wp = gs.whitePawns
    bp = gs.blackPawns
    for sq in iterateBits(wr):
        file = sq % 8
        rank = sq // 8
        if (FILE_MASKS[file] & wp) == 0: #no own pawns = semi-open
            score += OPEN_FILE_BONUS
            if (FILE_MASKS[file] & bp) == 0: #if no pawns and no enemy pawns = open
                score += OPEN_FILE_BONUS
        if rank == 6:
            score += ROOK_ON_SEVENTH_BONUS
    for sq in iterateBits(br):
        file = sq % 8
        rank = sq // 8
        if (FILE_MASKS[file] & bp) == 0:
            score -= OPEN_FILE_BONUS
            if (FILE_MASKS[file] & wp) == 0:
                score -= OPEN_FILE_BONUS
        if rank == 1: 
            score -= ROOK_ON_SEVENTH_BONUS
    #need to do connected when attack generation is cheaper
    return score

PAWN_SHIELD_BONUS = 15
DEFENDER_PIECES_BONUS = 5
OPEN_FILE_NEAR_KING_PENALTY = 20
CLOSE_ENEMY_PENALTY = 15 

def _king_eval(gs, phase):
    score = 0
    wk = gs.whiteKing
    bk = gs.blackKing
    wp = gs.whitePawns
    bp = gs.blackPawns
    whitePieces = gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens 
    blackPieces = gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens 
    for sq in iterateBits(wk):
        num_of_pawn_shield = (KING_ATTACKS[sq] & wp).bit_count()
        if num_of_pawn_shield:
            score += int(PAWN_SHIELD_BONUS * num_of_pawn_shield * phase)
        num_of_defenders = (KING_ATTACKS[sq] & whitePieces).bit_count()
        if num_of_defenders:
            score += int(DEFENDER_PIECES_BONUS * num_of_defenders * phase)
        num_of_attackers = (EXTENDED_KING_ZONE[sq] & blackPieces).bit_count()
        if num_of_attackers:
            score -= int(CLOSE_ENEMY_PENALTY * num_of_attackers * phase)
        file = sq % 8
        for f in range(max(0, file-1), min(8, file+2)):
            if (FILE_MASKS[f] & wp) == 0:
                score -= int(OPEN_FILE_NEAR_KING_PENALTY * phase)
    for sq in iterateBits(bk):
        num_of_pawn_shield = (KING_ATTACKS[sq] & bp).bit_count()
        if num_of_pawn_shield:
            score -= int(PAWN_SHIELD_BONUS * num_of_pawn_shield * phase)
        num_of_defenders = (KING_ATTACKS[sq] & blackPieces).bit_count()
        if num_of_defenders:
            score -= int(DEFENDER_PIECES_BONUS * num_of_defenders * phase)
        num_of_attackers = (EXTENDED_KING_ZONE[sq] & whitePieces).bit_count()
        if num_of_attackers:
            score += int(CLOSE_ENEMY_PENALTY * num_of_attackers * phase)
        file = sq % 8
        for f in range(max(0, file-1), min(8, file+2)):
            if (FILE_MASKS[f] & bp) == 0:
                score += int(OPEN_FILE_NEAR_KING_PENALTY * phase)
    return score

BISHOP_PAIR_BONUS = 30

def _bishop_eval(gs):
    score = 0
    wb = gs.whiteBishops
    bb = gs.blackBishops
    if wb.bit_count() > 1:
        score += BISHOP_PAIR_BONUS
    if bb.bit_count() > 1:
        score -= BISHOP_PAIR_BONUS
    return score

MOPUP_EDGE_BONUS    = 20
MOPUP_APPROACH      = 10
MOPUP_CUTOFF_BONUS  = 15

def _mopup_eval(gs):
    score = 0
    black_only_king = (gs.blackPawns | gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens) == 0
    white_only_king = (gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens) == 0

    if black_only_king:
        bk_sq = gs.blackKing.bit_length() - 1
        wk_sq = gs.whiteKing.bit_length() - 1
        bk_rank, bk_file = bk_sq // 8, bk_sq % 8
        wk_rank, wk_file = wk_sq // 8, wk_sq % 8
        # reward enemy king near edge/corner
        edge = (3 - min(bk_rank, 7 - bk_rank)) + (3 - min(bk_file, 7 - bk_file))
        score += edge * MOPUP_EDGE_BONUS
        # reward own king approaching enemy king
        dist = abs(wk_rank - bk_rank) + abs(wk_file - bk_file)
        score += (14 - dist) * MOPUP_APPROACH
        # rook cut-off: reward rooks that are trapping the enemy king toward an edge
        for sq in iterateBits(gs.whiteRooks):
            rook_rank = sq // 8
            rook_file = sq % 8
            if rook_rank != bk_rank:
                score += max(0, 3 - abs(rook_rank - bk_rank)) * MOPUP_CUTOFF_BONUS
            if rook_file != bk_file:
                score += max(0, 3 - abs(rook_file - bk_file)) * MOPUP_CUTOFF_BONUS

    if white_only_king:
        wk_sq = gs.whiteKing.bit_length() - 1
        bk_sq = gs.blackKing.bit_length() - 1
        wk_rank, wk_file = wk_sq // 8, wk_sq % 8
        bk_rank, bk_file = bk_sq // 8, bk_sq % 8
        edge = (3 - min(wk_rank, 7 - wk_rank)) + (3 - min(wk_file, 7 - wk_file))
        score -= edge * MOPUP_EDGE_BONUS
        dist = abs(bk_rank - wk_rank) + abs(bk_file - wk_file)
        score -= (14 - dist) * MOPUP_APPROACH
        for sq in iterateBits(gs.blackRooks):
            rook_rank = sq // 8
            rook_file = sq % 8
            if rook_rank != wk_rank:
                score -= max(0, 3 - abs(rook_rank - wk_rank)) * MOPUP_CUTOFF_BONUS
            if rook_file != wk_file:
                score -= max(0, 3 - abs(rook_file - wk_file)) * MOPUP_CUTOFF_BONUS

    return score

TEMPO_BONUS = 10

def evaluate(gs, alpha, beta):
    #cheap evaluation
    material_score, total_material = _material_eval(gs)
    position_score, phase = _position_eval(gs, total_material)
    is_endgame = False
    if total_material < ENDGAME_THRESHOLD:
        is_endgame = True

    #lazy evaluation
    if not is_endgame:
        lazy = material_score + position_score
        LAZY_MARGIN = 200
        if lazy - LAZY_MARGIN >= beta: #winning by margin
            return lazy, is_endgame
        if lazy + LAZY_MARGIN <= alpha: #losing by margin
            return lazy, is_endgame

    #expensize only call if not winning/losing by margin
    pawn_score = _pawn_eval(gs)
    rook_score = _rook_eval(gs)
    king_score = _king_eval(gs, phase)
    bishop_score = _bishop_eval(gs)
    mopup_score = _mopup_eval(gs)
    tempo = TEMPO_BONUS if gs.whiteToMove else -TEMPO_BONUS
    #endgame bool for search
    return material_score + position_score + pawn_score + rook_score + king_score + bishop_score + mopup_score + tempo, is_endgame

    