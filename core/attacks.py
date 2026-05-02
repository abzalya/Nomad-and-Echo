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

def knightMoves(sq, ownPieces):
    attacks = knightAttacks(sq)
    return attacks & ~ownPieces

#In practice people precompute all 64 results once at startup into a lookup table so you're never recalculating:
#KNIGHT_ATTACKS = [knight_attacks(sq) for sq in range(64)]

def kingAttacks(sq):
    bb = 1 << sq
    attacks = (bb << 8)
    attacks |= (bb >> 8)
    attacks |= ((bb << 1) & NOT_A_FILE)
    attacks |= ((bb >> 1) & NOT_H_FILE)
    attacks |= ((bb << 7) & NOT_A_FILE) #top left
    attacks |= ((bb << 9) & NOT_H_FILE) #top right
    attacks |= ((bb >> 7) & NOT_H_FILE) #bot right
    attacks |= ((bb >> 9) & NOT_A_FILE) #bot left
    return attacks & FULL #there was a legal move that was moving the king off the board preventing checkmate. apply the FULL Mask to fix.

def kingMoves(sq, ownPieces, allPieces, gs):
    attacks = kingAttacks(sq)
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

def pawnAttacks(sq, whiteToMove, enemyPieces, epSquare):
    bb = 1 << sq
    ep_bb = 0
    if whiteToMove:
        attacks  = (bb << 7) & NOT_H_FILE
        attacks |= (bb << 9) & NOT_A_FILE
    else:
        attacks  = (bb >> 7) & NOT_A_FILE
        attacks |= (bb >> 9) & NOT_H_FILE
    if epSquare != -1:
            ep_bb = (1 << epSquare)
    return attacks & (enemyPieces | ep_bb)

def pawnActions(sq, whiteToMove, ownPieces, enemyPieces, epSquare):
    allPieces = ownPieces | enemyPieces
    moves = pawnMoves(sq, whiteToMove, allPieces)
    attacks = pawnAttacks(sq, whiteToMove, enemyPieces, epSquare)
    return moves | (attacks & ~ownPieces)

def positiveRayAttacks(sq, enemyPieces, ownPieces, direction, fileMask=FULL):
    #iterating on the attack squares. move 1 square in a direction and check. if blocker, break, if wrapped file, break,
    #if empty the new start is the currect check sq. do again
    allPieces = ownPieces | enemyPieces
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

def negativeRayAttacks(sq, enemyPieces, ownPieces, direction, fileMask=FULL):
    allPieces = ownPieces | enemyPieces
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

#Directions
#positive
#N, <<8, none
#NE, <<9, not a
#E, <<1, not a
#NW, <<7, not h
#negative
#S, >>8, none
#SE, >>7, not a
#W, >>1, not h
#SW, >>9, not h

def rookAttacks(sq, enemyPieces, ownPieces):
    attacks = positiveRayAttacks(sq, enemyPieces, ownPieces, 8)
    attacks |= positiveRayAttacks(sq, enemyPieces, ownPieces, 1, NOT_A_FILE)
    attacks |= negativeRayAttacks(sq, enemyPieces, ownPieces, 8)
    attacks |= negativeRayAttacks(sq, enemyPieces, ownPieces, 1, NOT_H_FILE)
    return attacks

def bishopAttacks(sq, enemyPieces, ownPieces):
    attacks = positiveRayAttacks(sq, enemyPieces, ownPieces, 9, NOT_A_FILE)
    attacks |= positiveRayAttacks(sq, enemyPieces, ownPieces, 7, NOT_H_FILE)
    attacks |= negativeRayAttacks(sq, enemyPieces, ownPieces, 7, NOT_A_FILE)
    attacks |= negativeRayAttacks(sq, enemyPieces, ownPieces, 9, NOT_H_FILE)
    return attacks

def queenAttacks(sq, enemyPieces, ownPieces):
    attacks = rookAttacks(sq, enemyPieces, ownPieces)
    attacks |= bishopAttacks(sq, enemyPieces, ownPieces)
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
    attacks  = pawnAttacks(sq, gs.whiteToMove, enemyPawns, -1)
    attacks |= knightAttacks(sq) & enemyKnights
    attacks |= kingAttacks(sq) & enemyKing
    attacks |= bishopAttacks(sq, enemyPieces, ownPieces) & (enemyBishops | enemyQueens)
    attacks |= rookAttacks(sq, enemyPieces, ownPieces) & (enemyRooks | enemyQueens)
    return bool(attacks)
