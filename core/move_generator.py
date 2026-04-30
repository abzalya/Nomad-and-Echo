# Move Generation
from core.move import Move, MoveFlag
import copy

#our square function
def iterateBits(bb):
    while bb:
        lsb = bb & -bb
        yield lsb.bit_length() - 1
        bb &= bb - 1

#square map
# 56 57 58 59 60 61 62 63   (rank 8)
# 48 49 50 51 52 53 54 55   (rank 7)
# 40 41 42 43 44 45 46 47   (rank 6)
# 32 33 34 35 36 37 38 39   (rank 5)
# 24 25 26 27 28 29 30 31   (rank 4)
# 16 17 18 19 20 21 22 23   (rank 3)
#  8  9 10 11 12 13 14 15   (rank 2)
#  0  1  2  3  4  5  6  7   (rank 1)

#  a  b  c  d  e  f  g  h

#Piece Bitboards
PIECE_BITBOARDS = [
    "whitePawns",
    "whiteRooks",
    "whiteKnights",
    "whiteBishops",
    "whiteQueens",
    "whiteKing",
    "blackPawns",
    "blackRooks",
    "blackKnights",
    "blackBishops",
    "blackQueens",
    "blackKing",
]

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
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            allMoves.append(Move(sq, to_sq, flag))
    
    for sq in iterateBits(gs.whiteBishops if gs.whiteToMove else gs.blackBishops):
        bb = bishopAttacks(sq, enemyPieces, ownPieces)
        for to_sq in iterateBits(bb):
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            allMoves.append(Move(sq, to_sq, flag))
    
    for sq in iterateBits(gs.whiteRooks if gs.whiteToMove else gs.blackRooks):
        bb = rookAttacks(sq, enemyPieces, ownPieces)
        for to_sq in iterateBits(bb):
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            allMoves.append(Move(sq, to_sq, flag))
    
    for sq in iterateBits(gs.whiteQueens if gs.whiteToMove else gs.blackQueens):
        bb = queenAttacks(sq, enemyPieces, ownPieces)
        for to_sq in iterateBits(bb):
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            allMoves.append(Move(sq, to_sq, flag))
    
    return allMoves

def inCheck(gs): #reverse lookup approach
    whitePieces = gs.whitePawns | gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens | gs.whiteKing
    blackPieces = gs.blackPawns | gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens | gs.blackKing
    #inverse the colours. we apply move first and then check.
    if gs.whiteToMove:
        ownKing = gs.blackKing
        ownPieces = blackPieces
        enemyPieces = whitePieces
        enemyPawns = gs.whitePawns
        enemyKnights = gs.whiteKnights
        enemyBishops = gs.whiteBishops
        enemyRooks = gs.whiteRooks
        enemyQueens = gs.whiteQueens
    else:
        ownKing = gs.whiteKing
        ownPieces = whitePieces
        enemyPieces = blackPieces
        enemyPawns = gs.blackPawns
        enemyKnights = gs.blackKnights
        enemyBishops = gs.blackBishops
        enemyRooks = gs.blackRooks
        enemyQueens = gs.blackQueens

    for sq in iterateBits(ownKing):
        checks  = pawnAttacks(sq, not gs.whiteToMove, enemyPawns, -1)
        checks |= knightAttacks(sq) & enemyKnights
        checks |= bishopAttacks(sq, enemyPieces, ownPieces) & (enemyBishops | enemyQueens)
        checks |= rookAttacks(sq, enemyPieces, ownPieces) & (enemyRooks | enemyQueens)
        if checks:
            return True
    return False

#idea is to. generate_moves, copy gs, apply move, do check, if in check, discard. if not, keep pass to a lower legal_moves list?

def applyMove(gs, move):
    from_bb = 1 << move.from_sq
    to_bb = 1 << move.to_sq

    if move.flags & MoveFlag.CAPTURE:
        for attr in PIECE_BITBOARDS:
            bb = getattr(gs, attr)
            if bb & to_bb:
                setattr(gs, attr, bb & ~to_bb) #clears the "to" square
                #revoke castling rights if the rooks are captured
                if to_bb == (1 << 0):
                    gs.wQueenSideCastle = False
                elif to_bb == (1 << 7):
                    gs.wKingSideCastle = False
                elif to_bb == (1 << 56):
                    gs.bQueenSideCastle = False
                elif to_bb == (1 << 63):
                    gs.bKingSideCastle = False
                break

    if move.flags & MoveFlag.EN_PASSANT:
        for attr in PIECE_BITBOARDS:
            bb = getattr(gs, attr)
            #we need to clear the position of the double pushed pawn
            #to square is always on rank rank 6 or rank 3
            #the position of the double push pawn is always on rank 4 or 5
            #look in both directions and then clear with masks
            en_bb = (to_bb << 8)
            en_bb |= (to_bb >> 8)
            en_bb &= ~RANK_2
            en_bb &= ~RANK_7
            if bb & en_bb:
                setattr(gs, attr, bb & ~en_bb) #clears the double push square
                break

    if move.flags & MoveFlag.PROMOTION:
        if gs.whiteToMove:
            gs.whitePawns &= ~from_bb #remove pawn
        else:
            gs.blackPawns &= ~from_bb
        bb = getattr(gs, move.promo_piece)
        setattr(gs, move.promo_piece, bb | to_bb) #set the promotion piece on to_sq
        gs.epSquare = -1

    for attr in PIECE_BITBOARDS:
        bb = getattr(gs, attr)
        if bb & from_bb:
            setattr(gs, attr, (bb & ~from_bb) | to_bb) #clears the "from" square and sets "to" square
            if attr in ("whitePawns", "blackPawns") and abs(move.to_sq - move.from_sq) == 16:
                gs.epSquare = (move.from_sq + move.to_sq) // 2
            else:
                gs.epSquare = -1
            #revoke castling rights if pieces move from starting squares
            if attr == "whiteKing":
                gs.wKingSideCastle = False
                gs.wQueenSideCastle = False
            if attr == "blackKing":
                gs.bKingSideCastle = False
                gs.bQueenSideCastle = False
            if attr == "whiteRooks":
                if from_bb == (1 << 0):
                    gs.wQueenSideCastle = False
                elif from_bb == (1 << 7):
                    gs.wKingSideCastle = False
            if attr == "blackRooks":
                if from_bb == (1 << 56):
                    gs.bQueenSideCastle = False
                elif from_bb == (1 << 63):
                    gs.bKingSideCastle = False
            break

    gs.whiteToMove = not gs.whiteToMove

def legalMoves(gs):
    allLegalMoves = []
    allMoves = generateMoves(gs)
    for move in allMoves:
        gs_copy = copy.copy(gs)
        applyMove(gs_copy, move)
        if not inCheck(gs_copy):
            allLegalMoves.append(move)
    return allLegalMoves


FULL = 0xFFFFFFFFFFFFFFFF
NOT_A_FILE = 0xFEFEFEFEFEFEFEFE
NOT_H_FILE = 0x7F7F7F7F7F7F7F7F
NOT_AB_FILE = 0xFCFCFCFCFCFCFCFC
NOT_GH_FILE = 0x3F3F3F3F3F3F3F3F
RANK_2 = 0x000000000000FF00
RANK_7 = 0x00FF000000000000
RANK_18 = 0xFF000000000000FF

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
            attacks |= (bb << 2)
        if gs.wQueenSideCastle and not (castleQueenSideSquares & allPieces):
            attacks |= (bb >> 2)
    else:
        if gs.bKingSideCastle and not (castleKingSideSquares & allPieces):
            attacks |= (bb << 2)
        if gs.bQueenSideCastle and not (castleQueenSideSquares & allPieces):
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


#Notes

#pawns
#enpassant
#2 push can jump over stuff right now

#king
#needs check and needs castling
#The check detection for castling also needs to verify the king doesn't pass through an attacked square, not just land on one.
    
#rays
#create a hardcoded bitmap of the rays going out from selected square
# & with not colour of piece to leave only squares we can get to
#how to dissallow squares beyond the pieces and only first capture ?

# cast ray in a direction
# & with all occupied pieces → finds the first blocker
# everything beyond the blocker gets masked off
# then & ~own_pieces to allow capturing the blocker if it's an enemy