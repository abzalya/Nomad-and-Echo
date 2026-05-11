from core.bitboard import FULL, NOT_A_FILE, NOT_H_FILE, NOT_AB_FILE, NOT_GH_FILE, RANK_2, RANK_7
from core.bitboard import iterateBits
from core.ray_attacks import RAY_ATTACKS

def knightAttacks(sq):
    bb = 1 << sq
    attacks  = ((bb << 17) & NOT_A_FILE)
    attacks |= ((bb << 15) & NOT_H_FILE)
    attacks |= ((bb << 10) & NOT_AB_FILE)
    attacks |= ((bb <<  6) & NOT_GH_FILE)
    attacks |= ((bb >> 17) & NOT_H_FILE)
    attacks |= ((bb >> 15) & NOT_A_FILE)
    attacks |= ((bb >> 10) & NOT_GH_FILE)
    attacks |= ((bb >>  6) & NOT_AB_FILE)
    return attacks

KNIGHT_ATTACKS = [knightAttacks(sq) for sq in range(64)]

def knightMoves(sq, ownPieces):
    attacks = KNIGHT_ATTACKS[sq]
    return attacks & ~ownPieces

def kingAttacks(sq):
    bb = 1 << sq
    attacks = (bb << 8)
    attacks |= (bb >> 8)
    attacks |= ((bb << 1) & NOT_A_FILE)
    attacks |= ((bb >> 1) & NOT_H_FILE)
    attacks |= ((bb << 7) & NOT_H_FILE) #top left
    attacks |= ((bb << 9) & NOT_A_FILE) #top right
    attacks |= ((bb >> 7) & NOT_A_FILE) #bot right
    attacks |= ((bb >> 9) & NOT_H_FILE) #bot left
    return attacks & FULL #there was a legal move that was moving the king off the board preventing checkmate. apply the FULL Mask to fix.

KING_ATTACKS = [kingAttacks(sq) for sq in range(64)]

#for king evaluation
def _extended_king_zone(sq):
    zone = KING_ATTACKS[sq] | (1 << sq)
    result  = (zone << 8)
    result |= (zone >> 8)
    result |= ((zone << 1) & NOT_A_FILE)
    result |= ((zone >> 1) & NOT_H_FILE)
    result |= ((zone << 7) & NOT_H_FILE)
    result |= ((zone << 9) & NOT_A_FILE)
    result |= ((zone >> 7) & NOT_A_FILE)
    result |= ((zone >> 9) & NOT_H_FILE)
    return (result | zone) & FULL

EXTENDED_KING_ZONE = [_extended_king_zone(sq) for sq in range(64)]

def kingMoves(sq, ownPieces, allPieces, gs, attacked_bb):
    attacks = KING_ATTACKS[sq]
    bb = 1 << sq
    castleKingSideSquares = ((bb << 1) | (bb << 2))
    castleQueenSideSquares = ((bb >> 1) | (bb >> 2) | (bb >> 3))

    if gs.whiteToMove:
        ks_right = gs.wKingSideCastle
        qs_right = gs.wQueenSideCastle
    else:
        ks_right = gs.bKingSideCastle
        qs_right = gs.bQueenSideCastle

    #castling: rights still valid + path clear of own/enemy pieces
    can_ks = ks_right and not (castleKingSideSquares & allPieces)
    can_qs = qs_right and not (castleQueenSideSquares & allPieces)

    if can_ks or can_qs:
        if can_ks:
            #king path: e1->f1->g1 (or e8->f8->g8) — none can be attacked
            ks_path = bb | (bb << 1) | (bb << 2)
            if not (attacked_bb & ks_path):
                attacks |= (bb << 2)
        if can_qs:
            #king path: e1->d1->c1 (or e8->d8->c8) — b1/b8 must be empty (already checked above)
            #but doesn't need to be unattacked since the king doesn't pass through it
            qs_path = bb | (bb >> 1) | (bb >> 2)
            if not (attacked_bb & qs_path):
                attacks |= (bb >> 2)
    return attacks & ~ownPieces

def pawnMoves(sq, whiteToMove, allPieces):
    bb = 1 << sq
    if whiteToMove:
        moves = (bb << 8) & ~allPieces
        if (bb & RANK_2) and moves: #fixing pawn jumping over pieces on double-push
            moves |= (bb << 16) & ~allPieces
    else:
        moves = (bb >> 8) & ~allPieces
        if (bb & RANK_7) and moves:
            moves |= (bb >> 16) & ~allPieces
    return moves & FULL

def _pawnAttacks(sq, white):
    bb = 1 << sq
    if white:
        attacks  = (bb << 7) & NOT_H_FILE
        attacks |= (bb << 9) & NOT_A_FILE
    else:
        attacks  = (bb >> 7) & NOT_A_FILE
        attacks |= (bb >> 9) & NOT_H_FILE
    return attacks

PAWN_ATTACKS = [
    [_pawnAttacks(sq, True)  for sq in range(64)],  # 0 = white
    [_pawnAttacks(sq, False) for sq in range(64)],  # 1 = black
]

def pawnAttacks(sq, whiteToMove, enemyPieces, epSquare):
    ep_bb = (1 << epSquare) if epSquare != -1 else 0
    return PAWN_ATTACKS[0 if whiteToMove else 1][sq] & (enemyPieces | ep_bb)

def pawnActions(sq, whiteToMove, ownPieces, enemyPieces, epSquare):
    allPieces = ownPieces | enemyPieces
    moves = pawnMoves(sq, whiteToMove, allPieces)
    attacks = pawnAttacks(sq, whiteToMove, enemyPieces, epSquare)
    return moves | (attacks & ~ownPieces)

def rayAttack(sq, allPieces, ownPieces, direction):
    ray = RAY_ATTACKS[direction][sq]
    blockers = ray & allPieces
    if blockers == 0:
        return ray & ~ownPieces
    if direction <= 2 or direction == 7:
        first_sq = (blockers & -blockers).bit_length() - 1
        return (ray & ((1 << (first_sq + 1)) - 1)) & ~ownPieces
    else:
        first_sq = blockers.bit_length() - 1
        return (ray & ~((1 << first_sq) - 1)) & ~ownPieces


def rookAttacks(sq, allPieces, ownPieces):
    attacks = rayAttack(sq, allPieces, ownPieces, 0)
    attacks |= rayAttack(sq, allPieces, ownPieces, 2)
    attacks |= rayAttack(sq, allPieces, ownPieces, 4)
    attacks |= rayAttack(sq, allPieces, ownPieces, 6)
    return attacks

def bishopAttacks(sq, allPieces, ownPieces):
    attacks = rayAttack(sq, allPieces, ownPieces, 1)
    attacks |= rayAttack(sq, allPieces, ownPieces, 3)
    attacks |= rayAttack(sq, allPieces, ownPieces, 5)
    attacks |= rayAttack(sq, allPieces, ownPieces, 7)
    return attacks

def queenAttacks(sq, allPieces, ownPieces):
    attacks = rookAttacks(sq, allPieces, ownPieces)
    attacks |= bishopAttacks(sq, allPieces, ownPieces)
    return attacks

def isSquareAttacked(sq, gs): #reverse lookup approach for any arbitrary square on the board
    whitePieces = gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens | gs.whiteKing
    blackPieces = gs.blackPawns | gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens | gs.blackKing
    if gs.whiteToMove:
        ownPieces = whitePieces
        enemyPieces = blackPieces
        enemyPawns = gs.blackPawns
        enemyKnights = gs.blackKnights
        enemyBishops = gs.blackBishops
        enemyRooks = gs.blackRooks
        enemyQueens = gs.blackQueens
        enemyKing = gs.blackKing
    else:
        ownPieces = blackPieces
        enemyPieces = whitePieces
        enemyPawns = gs.whitePawns
        enemyKnights = gs.whiteKnights
        enemyBishops = gs.whiteBishops
        enemyRooks = gs.whiteRooks
        enemyQueens = gs.whiteQueens
        enemyKing = gs.whiteKing
    allPieces = ownPieces | enemyPieces
    #shortcut: cheap checks first, return early if any attack found
    if PAWN_ATTACKS[0 if gs.whiteToMove else 1][sq] & enemyPawns: return True
    if KNIGHT_ATTACKS[sq] & enemyKnights: return True
    if KING_ATTACKS[sq] & enemyKing: return True
    if bishopAttacks(sq, allPieces, ownPieces) & (enemyBishops | enemyQueens): return True
    if rookAttacks(sq, allPieces, ownPieces) & (enemyRooks | enemyQueens): return True
    return False

def attackedBy(gs, exclude_defender_king=False):
    white_attacking = not gs.whiteToMove
    
    #sometimes we would want to not include our king in allPieces to see what enemy sliders are x-raying through our king. 
    allPieces = (gs.whitePawns | gs.whiteRooks | gs.whiteKnights |
                 gs.whiteBishops | gs.whiteQueens | gs.whiteKing |
                 gs.blackPawns | gs.blackRooks | gs.blackKnights |
                 gs.blackBishops | gs.blackQueens | gs.blackKing)

    if exclude_defender_king:
        if white_attacking:
            allPieces &= ~gs.blackKing  # remove the defender's king
        else:
            allPieces &= ~gs.whiteKing

    attacked = 0
    if white_attacking:
        for sq in iterateBits(gs.whitePawns):
            attacked |= PAWN_ATTACKS[0][sq]
        for sq in iterateBits(gs.whiteKnights):
            attacked |= KNIGHT_ATTACKS[sq]
        for sq in iterateBits(gs.whiteKing):
            attacked |= KING_ATTACKS[sq]
        for sq in iterateBits(gs.whiteBishops | gs.whiteQueens):
            attacked |= bishopAttacks(sq, allPieces, ownPieces=0)
        for sq in iterateBits(gs.whiteRooks | gs.whiteQueens):
            attacked |= rookAttacks(sq, allPieces, ownPieces=0)
    else:
        for sq in iterateBits(gs.blackPawns):
            attacked |= PAWN_ATTACKS[1][sq]
        for sq in iterateBits(gs.blackKnights):
            attacked |= KNIGHT_ATTACKS[sq]
        for sq in iterateBits(gs.blackKing):
            attacked |= KING_ATTACKS[sq]
        for sq in iterateBits(gs.blackBishops | gs.blackQueens):
            attacked |= bishopAttacks(sq, allPieces, ownPieces=0)
        for sq in iterateBits(gs.blackRooks | gs.blackQueens):
            attacked |= rookAttacks(sq, allPieces, ownPieces=0)
    return attacked

def inCheck(gs):
    ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
    return bool(attackedBy(gs) & ownKing)