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
            allMoves.append(Move(sq, to_sq))
    
    for sq in iterateBits(gs.whiteKnights if gs.whiteToMove else gs.blackKnights):
        bb = knightMoves(sq, ownPieces)
        for to_sq in iterateBits(bb):
            allMoves.append(Move(sq, to_sq))
    
    for sq in iterateBits(gs.whiteKing if gs.whiteToMove else gs.blackKing):
        bb = kingMoves(sq, ownPieces)
        for to_sq in iterateBits(bb):
            allMoves.append(Move(sq, to_sq))
    
    return allMoves

def applyMove(gs, move):
    from_bb = 1 << move.from_sq
    to_bb = 1 << move.to_sq

    for attr in PIECE_BITBOARDS:
        bb = getattr(gs, attr)
        if bb & from_bb:
            setattr(gs, attr, (bb & ~from_bb) | to_bb)
            break

    if move.flags & MoveFlag.CAPTURE:
        for attr in PIECE_BITBOARDS:
            bb = getattr(gs, attr)
            if bb & to_bb:
                setattr(gs, attr, bb & ~to_bb)
                break

    gs.whiteToMove = not gs.whiteToMove




#Selected Piece Logic
def selectedPiece(sq, gs):
    bb = 1 << sq
    for piece in PIECE_BITBOARDS:
        if bb & getattr(gs, piece) != 0:
            return piece
    return None    


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
    return (moves | attacks) & ~ownPieces
        


def verticalRayAttacks(sq):
    #apply a ray on all the squares (empty board)
    #& with bitboards of all pieces
    #find lsb index using iterate bits ?
    pass


#Notes
#global colour check in my head is essentially
#white turn to move & (selectedsquare & whitepieces) for white
#!whiteturntomove & (selectedsquare & blackpieces) for black

#Knights
#8 moves, mask the files that are out of the board
#And with NOT its colour to get legal moves (without the check check)

#pawns
#if whiteturntomove & (selectedsquare & whitepieces) this should check if we clicked white piece and together with white to move
#check if white move and white piece 
#offset is positive to move up. if selectedsquare is rank 2 then allow 1 or 2 moves
#pawn attacks & selected square & blackpieces then legal capture
#this is not including enpassant

#king
#all 8 directions, mask edges
#needs check and needs castling

#rays
#create a hardcoded bitmap of the rays going out from selected square
# & with not colour of piece to leave only squares we can get to
#how to dissallow squares beyond the pieces and only first capture ?

#Knights — correct. Mask A-file for -17, -10, +6, +15 and B-file for -10, +6 (same side). H-file and G-file for the other side. Then & ~own_pieces.

# Pawns — correct logic. One thing to add: the double push should check that the intermediate square is also empty, not just the destination.

# King — correct. The check detection for castling also needs to verify the king doesn't pass through an attacked square, not just land on one.

# Rays — this is the one to think about more carefully. The standard bitboard approach is:


# cast ray in a direction
# & with all occupied pieces → finds the first blocker
# everything beyond the blocker gets masked off
# then & ~own_pieces to allow capturing the blocker if it's an enemy

# --- OVERALL APPROACH ---
# At the start of each turn, generate ALL legal moves for ALL pieces into a flat list:
#   all_legal_moves = [Move(from_sq, to_sq, flags), ...]
# Each Move stores the origin square, destination, and any special flags.
# No two moves will ever share the same (from_sq, to_sq) pair.
#
# When a square is clicked:
#   legal_from_here = [m for m in all_legal_moves if m.from_sq == clicked_sq]
#   highlight all m.to_sq in that list
#
# When a destination is clicked:
#   find Move(from_sq=first_click, to_sq=second_click) in the list → apply it
#
# This list is also used to detect checkmate (empty = checkmate/stalemate)
# and by the engine to search through candidate moves.