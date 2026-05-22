from core.bitboard import iterateBits
from engine.pawn_eval_masks import ADJACENT_FILES_MASKS, PASSED_MASKS



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

def king_and_pawn(white_passed, black_passed, wk_sq, bk_sq):
    score = 0
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
    return score

#rule of square, uncatchable pawns

def pawn_uncathable(p_sq, k_sq, p_color, side_to_move, all_pieces):
    p_rank = p_sq // 8
    p_file = p_sq % 8

    if p_color == "WHITE":
        queen_sq = p_sq | 56
        distance = 7 - p_rank
        #double push counts as one move
        if p_rank == 1:
            distance = 5
        #path from pawn to queening sq (exclusive of pawn, inclusive of queening sq)
        path_mask = 0
        for r in range(p_rank + 1, 8):
            path_mask |= 1 << (r * 8 + p_file)
    else:
        queen_sq = p_sq & 7
        distance = p_rank
        if p_rank == 6:
            distance = 5
        path_mask = 0
        for r in range(0, p_rank):
            path_mask |= 1 << (r * 8 + p_file)

    #any piece (own or enemy) in the path invalidates the rule of square
    if path_mask & all_pieces:
        return False

    king_dist = chebyshev(k_sq, queen_sq)

    # If pawn's side to move, extra tempo
    if side_to_move == p_color:
        return king_dist > distance
    else:
        return king_dist > distance + 1

UNCATCHABLE_PAWN_BONUS = 250  # dropped from 600 — conservative, search verifies the rest

def unchatable_pawns(white_passed, black_passed, wk_sq, bk_sq, side_to_move, all_pieces):
    score = 0
    for sq in iterateBits(white_passed):
        if pawn_uncathable(sq, bk_sq, "WHITE", side_to_move, all_pieces):
            score += UNCATCHABLE_PAWN_BONUS
    for sq in iterateBits(black_passed):
        if pawn_uncathable(sq, wk_sq, "BLACK", side_to_move, all_pieces):
            score -= UNCATCHABLE_PAWN_BONUS
    return score

#connected passers

CONNECTED_PASSED_BONUS = 50 #per pawn, but 2 connected are about twice as strong*

def connected_passers(white_passed, black_passed):
    score = 0
    for sq in iterateBits(white_passed):
        file = sq % 8
        if ADJACENT_FILES_MASKS[file] & white_passed:
            score += CONNECTED_PASSED_BONUS
    for sq in iterateBits(black_passed):
        file = sq % 8
        if ADJACENT_FILES_MASKS[file] & black_passed:
            score -= CONNECTED_PASSED_BONUS
    return score

#wonrg colour bishop endgame
#return true if wrong bishop
def is_drawn_wrong_bishop(gs, side_attacking):
    if side_attacking == "WHITE":
        bishops = gs.whiteBishops
        pawns = gs.whitePawns
        other = (gs.whiteRooks | gs.whiteKnights | gs.whiteQueens | 
                 gs.blackPawns | gs.blackRooks | gs.blackKnights | 
                 gs.blackBishops | gs.blackQueens)
    else:
        bishops = gs.blackBishops
        pawns = gs.blackPawns
        other = (gs.blackRooks | gs.blackKnights | gs.blackQueens | 
                 gs.whitePawns | gs.whiteRooks | gs.whiteKnights | 
                 gs.whiteBishops | gs.whiteQueens)
    
    if other != 0:
        return False  # other material on board
    if bishops.bit_count() != 1:
        return False
    if pawns.bit_count() != 1:
        return False
    
    pawn_sq = next(iterateBits(pawns))
    pawn_file = pawn_sq % 8
    if pawn_file != 0 and pawn_file != 7:
        return False  # not a rook pawn
    
    bishop_sq = next(iterateBits(bishops))
    bishop_color = (bishop_sq // 8 + bishop_sq % 8) & 1
    
    if side_attacking == "WHITE":
        promo_sq = pawn_file + 56
    else:
        promo_sq = pawn_file
    promo_color = (promo_sq // 8 + promo_sq % 8) & 1
    
    return bishop_color != promo_color


#unite
def endgame_eval(gs):
    side_to_move = "WHITE" if gs.whiteToMove else "BLACK"
    white_passed, black_passed = passed_pawns(gs.whitePawns, gs.blackPawns)
    wk_sq = gs.whiteKing.bit_length() - 1
    bk_sq = gs.blackKing.bit_length() - 1

    #all occupancy for blocker checks
    all_pieces = (gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops |
                  gs.whiteQueens | gs.whiteKing | gs.blackPawns | gs.blackRooks |
                  gs.blackKnights | gs.blackBishops | gs.blackQueens | gs.blackKing)

    k_and_p_score = king_and_pawn(white_passed, black_passed, wk_sq, bk_sq)
    unchatable_pawns_score = unchatable_pawns(white_passed, black_passed, wk_sq, bk_sq, side_to_move, all_pieces)
    connected_passers_score = connected_passers(white_passed, black_passed)

    return k_and_p_score + unchatable_pawns_score + connected_passers_score

