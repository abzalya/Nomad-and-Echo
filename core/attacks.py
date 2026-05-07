from core.bitboard import FULL, NOT_A_FILE, NOT_H_FILE, NOT_AB_FILE, NOT_GH_FILE, RANK_2, RANK_7

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

def kingMoves(sq, ownPieces, allPieces, gs):
    attacks = KING_ATTACKS[sq]
    #i think castling should go here
    bb = 1 << sq
    castleKingSideSquares = ((bb << 1) | (bb << 2))
    castleQueenSideSquares = ((bb >> 1) | (bb >> 2) | (bb >> 3))
    if gs.whiteToMove:
        if gs.wKingSideCastle and not (castleKingSideSquares & allPieces):
            if not isSquareAttacked(sq, gs) and not isSquareAttacked(sq+1, gs) and not isSquareAttacked(sq+2, gs):
                attacks |= (bb << 2)
        if gs.wQueenSideCastle and not (castleQueenSideSquares & allPieces):
            if not isSquareAttacked(sq, gs) and not isSquareAttacked(sq-1, gs) and not isSquareAttacked(sq-2, gs):
                attacks |= (bb >> 2)
    else:
        if gs.bKingSideCastle and not (castleKingSideSquares & allPieces):
            if not isSquareAttacked(sq, gs) and not isSquareAttacked(sq+1, gs) and not isSquareAttacked(sq+2, gs):
                attacks |= (bb << 2)
        if gs.bQueenSideCastle and not (castleQueenSideSquares & allPieces):
            if not isSquareAttacked(sq, gs) and not isSquareAttacked(sq-1, gs) and not isSquareAttacked(sq-2, gs):
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

def positiveRayAttacks(sq, allPieces, ownPieces, direction, fileMask=FULL):
    #iterating on the attack squares. move 1 square in a direction and check. if blocker, break, if wrapped file, break,
    #if empty the new start is the currect check sq. do again
    bb = 1 << sq
    attacks = 0
    for i in range (7):
        attacked_sq = (bb << direction) & fileMask & FULL
        if attacked_sq == 0:
            break
        if attacked_sq & allPieces:
            attacks |= attacked_sq
            break
        else:
            attacks |= attacked_sq
            bb = attacked_sq
    return attacks & ~ownPieces

def negativeRayAttacks(sq, allPieces, ownPieces, direction, fileMask=FULL):
    bb = 1 << sq
    attacks = 0
    for i in range (7):
        attacked_sq = (bb >> direction) & fileMask & FULL
        if attacked_sq == 0:
            break
        if attacked_sq & allPieces:
            attacks |= attacked_sq
            break
        else:
            attacks |= attacked_sq
            bb = attacked_sq
    return attacks & ~ownPieces

def rookAttacks(sq, allPieces, ownPieces):
    attacks = positiveRayAttacks(sq, allPieces, ownPieces, 8)
    attacks |= positiveRayAttacks(sq, allPieces, ownPieces, 1, NOT_A_FILE)
    attacks |= negativeRayAttacks(sq, allPieces, ownPieces, 8)
    attacks |= negativeRayAttacks(sq, allPieces, ownPieces, 1, NOT_H_FILE)
    return attacks

def bishopAttacks(sq, allPieces, ownPieces):
    attacks = positiveRayAttacks(sq, allPieces, ownPieces, 9, NOT_A_FILE)
    attacks |= positiveRayAttacks(sq, allPieces, ownPieces, 7, NOT_H_FILE)
    attacks |= negativeRayAttacks(sq, allPieces, ownPieces, 7, NOT_A_FILE)
    attacks |= negativeRayAttacks(sq, allPieces, ownPieces, 9, NOT_H_FILE)
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
