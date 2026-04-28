# Move Generation
from core.move import Move, MoveFlag

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
        bb = pawnActions(sq, gs.whiteToMove, ownPieces, enemyPieces)
        for to_sq in iterateBits(bb):
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            promo_piece = None
            allMoves.append(Move(sq, to_sq, flag, promo_piece))
    
    for sq in iterateBits(gs.whiteKnights if gs.whiteToMove else gs.blackKnights):
        bb = knightMoves(sq, ownPieces)
        for to_sq in iterateBits(bb):
            flag = MoveFlag.CAPTURE if (1 << to_sq) & enemyPieces else MoveFlag.NORMAL
            allMoves.append(Move(sq, to_sq, flag))
    
    for sq in iterateBits(gs.whiteKing if gs.whiteToMove else gs.blackKing):
        bb = kingMoves(sq, ownPieces)
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

def applyMove(gs, move):
    from_bb = 1 << move.from_sq
    to_bb = 1 << move.to_sq

    if move.flags & MoveFlag.CAPTURE:
        for attr in PIECE_BITBOARDS:
            bb = getattr(gs, attr)
            if bb & to_bb:
                setattr(gs, attr, bb & ~to_bb) #clears the "to" square
                break

    for attr in PIECE_BITBOARDS:
        bb = getattr(gs, attr)
        if bb & from_bb:
            setattr(gs, attr, (bb & ~from_bb) | to_bb) #clears the "from" square and sets "to" square
            break

    gs.whiteToMove = not gs.whiteToMove




#Selected Piece Logic
def selectedPiece(sq, gs):
    bb = 1 << sq
    for piece in PIECE_BITBOARDS:
        if bb & getattr(gs, piece) != 0:
            return piece
    return None    

FULL = 0xFFFFFFFFFFFFFFFF
NOT_A_FILE = 0xFEFEFEFEFEFEFEFE
NOT_H_FILE = 0x7F7F7F7F7F7F7F7F
NOT_AB_FILE = 0xFCFCFCFCFCFCFCFC
NOT_GH_FILE = 0x3F3F3F3F3F3F3F3F
RANK_2 = 0x000000000000FF00
RANK_7 = 0x00FF000000000000

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
    return attacks

def kingMoves(sq, ownPieces):
    attacks = kingAttacks(sq)
    return attacks & ~ownPieces

def pawnMoves(sq, whiteToMove):
    bb = 1 << sq
    if whiteToMove:
        moves = (bb << 8)
        if (bb & RANK_2 != 0):
            moves |= (bb << 16)
        return moves
    else:
        moves = (bb >> 8)
        if (bb & RANK_7 != 0):
            moves |= (bb >> 16)
        return moves 

def pawnAttacks(sq, whiteToMove, enemyPieces):
    bb = 1 << sq
    if whiteToMove:
        attacks  = (bb << 7) & NOT_H_FILE
        attacks |= (bb << 9) & NOT_A_FILE
    else:
        attacks  = (bb >> 7) & NOT_A_FILE
        attacks |= (bb >> 9) & NOT_H_FILE
    return attacks & enemyPieces

def pawnActions(sq, whiteToMove, ownPieces, enemyPieces):
    moves   = pawnMoves(sq, whiteToMove)
    attacks = pawnAttacks(sq, whiteToMove, enemyPieces)
    allPieces = ownPieces | enemyPieces
    return (moves & ~ allPieces) | (attacks & ~ownPieces) #blocking pushing onto enemy pieces
        
def positiveRayAttacks(sq, enemyPieces, ownPieces, direction, fileMask=FULL):
    # we cast a ray in a positive direction and get a bb of attacks. & with all pieces to find blockers.
    # anding with the blockers mask returns all moves negative of the blocker. 
    allPieces = ownPieces | enemyPieces
    bb = 1 << sq
    attacks = 0
    for i in range (1,8):
        attacks |= (bb << (direction * i)) & fileMask & FULL
    blockers = attacks & allPieces
    if blockers:
        lsbOfBlockers = blockers & -blockers
        lsbMask = (lsbOfBlockers << 1) - 1 # fills all lower bits of lsb with 1
        attacks &= lsbMask
    #add breaks on first block detection?
    return attacks & ~ownPieces

def negativeRayAttacks(sq, enemyPieces, ownPieces, direction, fileMask=FULL):
    allPieces = ownPieces | enemyPieces
    bb = 1 << sq
    attacks = 0
    for i in range (1,8):
        attacks |= (bb >> (direction * i)) & fileMask & FULL
    blockers = attacks & allPieces
    if blockers:
        msbOfBlockers = 1 << (blockers.bit_length() -1)
        msbMask = msbOfBlockers - 1
        attacks &= ~msbMask #~on mask required here
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