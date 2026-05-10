# Move Generation
from core.move import Move, MoveFlag
from core.bitboard import iterateBits, RANK_18
from core.attacks import pawnActions, pawnAttacks, pawnMoves, knightMoves, kingMoves, bishopAttacks, rookAttacks, queenAttacks, isSquareAttacked, KING_ATTACKS
from core.apply_move import applyMove, undoMove

def generateMoves(gs, attacked_bb=None):
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
                flag |= MoveFlag.PROMOTION
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
        bb = kingMoves(sq, ownPieces, allPieces, gs, attacked_bb)
        for to_sq in iterateBits(bb):
            if (1 << to_sq) & enemyPieces:
                flag = MoveFlag.CAPTURE
            else:
                flag = MoveFlag.NORMAL
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

#generating captures and promotion moves only specially for quiescence to eliminate all move overhead from that search
def generateQuiescence(gs):
    allMoves = []
    whitePieces = gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens | gs.whiteKing
    blackPieces = gs.blackPawns | gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens | gs.blackKing
    allPieces = whitePieces | blackPieces

    if gs.whiteToMove:
        ownPieces = whitePieces
        enemyPieces = blackPieces
        own_pawns   = gs.whitePawns
        own_knights = gs.whiteKnights
        own_bishops = gs.whiteBishops
        own_rooks   = gs.whiteRooks
        own_queens  = gs.whiteQueens
        own_king    = gs.whiteKing
        promo_pieces = ("whiteQueens", "whiteRooks", "whiteBishops", "whiteKnights")
    else:
        ownPieces = blackPieces
        enemyPieces = whitePieces
        own_pawns   = gs.blackPawns
        own_knights = gs.blackKnights
        own_bishops = gs.blackBishops
        own_rooks   = gs.blackRooks
        own_queens  = gs.blackQueens
        own_king    = gs.blackKing
        promo_pieces = ("blackQueens", "blackRooks", "blackBishops", "blackKnights")

    ep_sq = gs.epSquare

    #Pawns: captures + EP via pawnAttacks; quiet promotions via pawnMoves filtered to last rank
    for sq in iterateBits(own_pawns):
        cap_bb = pawnAttacks(sq, gs.whiteToMove, enemyPieces, ep_sq)
        for to_sq in iterateBits(cap_bb):
            if to_sq == ep_sq:
                allMoves.append(Move(sq, to_sq, MoveFlag.EN_PASSANT))
            elif (1 << to_sq) & RANK_18:
                flag = MoveFlag.CAPTURE | MoveFlag.PROMOTION
                for promo in promo_pieces:
                    allMoves.append(Move(sq, to_sq, flag, promo))
            else:
                allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))
        #quiet promotion with no capture
        for to_sq in iterateBits(pawnMoves(sq, gs.whiteToMove, allPieces) & RANK_18):
            for promo in promo_pieces:
                allMoves.append(Move(sq, to_sq, MoveFlag.PROMOTION, promo))

    #Other pieces: attack masked to enemy squares only
    for sq in iterateBits(own_knights):
        for to_sq in iterateBits(knightMoves(sq, ownPieces) & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    for sq in iterateBits(own_bishops):
        for to_sq in iterateBits(bishopAttacks(sq, allPieces, ownPieces) & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    for sq in iterateBits(own_rooks):
        for to_sq in iterateBits(rookAttacks(sq, allPieces, ownPieces) & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    for sq in iterateBits(own_queens):
        for to_sq in iterateBits(queenAttacks(sq, allPieces, ownPieces) & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    #King captures only
    for sq in iterateBits(own_king):
        for to_sq in iterateBits(KING_ATTACKS[sq] & enemyPieces):
            allMoves.append(Move(sq, to_sq, MoveFlag.CAPTURE))

    return allMoves

#pin-mask legal generation
#the current generation of legal moves relies on apply-undo and incheck checking for each move generated
#for speed reasons the legality check has been moved within the searching and that has produced results
#however, apart from magic botboards being probably the largest remaining improvement on move generation (shelved for now but on todo)
#there is an option that is done by modern engines that i was unaware of
#idea
#we will, generate a bitboard of pinned-pieces and for each piece we will keep the ray its pinned along
#non-pinned and non-king moves are all passed as legal instantly
#pinned pieces are restricted to movement along their pinned ray
#king is allowed AND against ~attacked_squares bitboard
#en-passant we will simply do our apply undo check as its easier and its a rare move anyway
