# Move Generation
from core.move import Move, MoveFlag
from core.bitboard import iterateBits, RANK_18
from core.attacks import pawnActions, knightMoves, kingMoves, bishopAttacks, rookAttacks, queenAttacks, isSquareAttacked
from core.apply_move import applyMove, undoMove

def generateMoves(gs):
    allMoves = []
    whitePieces = gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens | gs.whiteKing
    blackPieces = gs.blackPawns | gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens | gs.blackKing
    allPieces = whitePieces | blackPieces

    if gs.whiteToMove:
        ownPieces = whitePieces
        enemyPieces = blackPieces
    else:
        ownPieces = blackPieces
        enemyPieces = whitePieces

    for sq in iterateBits(gs.whitePawns if gs.whiteToMove else gs.blackPawns):
        bb = pawnActions(sq, gs.whiteToMove, ownPieces, enemyPieces, gs.epSquare)
        for to_sq in iterateBits(bb):
            if to_sq == gs.epSquare:
                flag = MoveFlag.EN_PASSANT
            elif (1 << to_sq) & enemyPieces:
                flag = MoveFlag.CAPTURE
            else:
                flag = MoveFlag.NORMAL
            promo_piece = None

            if ((1 << to_sq) & RANK_18):
                flag |= MoveFlag.PROMOTION #IntFlag allows & for multiple flags.
                if gs.whiteToMove:
                    promotions = ["whiteQueens", "whiteRooks", "whiteBishops", "whiteKnights"]
                else:
                    promotions = ["blackQueens", "blackRooks", "blackBishops", "blackKnights"]
                for promotion in promotions:
                    allMoves.append(Move(sq, to_sq, flag, promotion))
            else:
                allMoves.append(Move(sq, to_sq, flag, promo_piece))

    for sq in iterateBits(gs.whiteKnights if gs.whiteToMove else gs.blackKnights):
        bb = knightMoves(sq, ownPieces)
        for to_sq in iterateBits(bb):
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            allMoves.append(Move(sq, to_sq, flag))

    for sq in iterateBits(gs.whiteKing if gs.whiteToMove else gs.blackKing):
        bb = kingMoves(sq, ownPieces, allPieces, gs)
        for to_sq in iterateBits(bb):
            if (1 << to_sq) & enemyPieces:
                flag = MoveFlag.CAPTURE
            else:
                flag = MoveFlag.NORMAL
            #if castling add the flag, dont overwrite normal
            if (to_sq - sq) == 2:
                flag |= MoveFlag.CASTLE_K
            if (to_sq - sq) == -2:
                flag |= MoveFlag.CASTLE_Q
            allMoves.append(Move(sq, to_sq, flag))

    for sq in iterateBits(gs.whiteBishops if gs.whiteToMove else gs.blackBishops):
        bb = bishopAttacks(sq, allPieces, ownPieces)
        for to_sq in iterateBits(bb):
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            allMoves.append(Move(sq, to_sq, flag))

    for sq in iterateBits(gs.whiteRooks if gs.whiteToMove else gs.blackRooks):
        bb = rookAttacks(sq, allPieces, ownPieces)
        for to_sq in iterateBits(bb):
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            allMoves.append(Move(sq, to_sq, flag))

    for sq in iterateBits(gs.whiteQueens if gs.whiteToMove else gs.blackQueens):
        bb = queenAttacks(sq, allPieces, ownPieces)
        for to_sq in iterateBits(bb):
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            allMoves.append(Move(sq, to_sq, flag))

    return allMoves

def legalMoves(gs):
    allLegalMoves = []
    for move in generateMoves(gs):
        applyMove(gs, move)
        gs.whiteToMove = not gs.whiteToMove  # flip back to check own king
        ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        sq = ownKing.bit_length() - 1
        if not isSquareAttacked(sq, gs):
            allLegalMoves.append(move)
        gs.whiteToMove = not gs.whiteToMove  # restore before undo
        undoMove(gs)
    return allLegalMoves

def captureMovesOnly(gs):
    allLegalMoves = legalMoves(gs)
    allCaptureMoves = []
    for move in allLegalMoves:
        if move.flags & MoveFlag.CAPTURE:
            allCaptureMoves.append(move)
    return allCaptureMoves