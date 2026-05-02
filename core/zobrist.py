import random
random.seed(1)

from core.bitboard import iterateBits, PIECE_BITBOARDS

PIECE_INDEX = {attr: i for i, attr in enumerate(PIECE_BITBOARDS)}

ZOBRIST_PIECES   = [[random.getrandbits(64) for _ in range(64)] for _ in range(12)] #12*64 random numbers for each piece on each square
ZOBRIST_SIDE     = random.getrandbits(64) #1 random number for when its blacks turn to move
ZOBRIST_CASTLING = [random.getrandbits(64) for _ in range(4)] #4 random numbers for castling
ZOBRIST_EP       = [random.getrandbits(64) for _ in range(8)] #8 random numbers for a file of the valid epSquare

#at runtime we will xor all random numbers to get an almost unique value for a given position
# xor-operation is own inverse so its easy to implement incremental updates as gamestate changes

#Initial Hash - ran once on startup
def computeHash(gs):
    hash = 0
    for attr, i in PIECE_INDEX.items():
        for sq in iterateBits(getattr(gs, attr)):
            hash ^= ZOBRIST_PIECES[i][sq]
    if not gs.whiteToMove:
        hash ^= ZOBRIST_SIDE
    for index, castle_right in enumerate([gs.wKingSideCastle, gs.wQueenSideCastle, gs.bKingSideCastle, gs.bQueenSideCastle]):
        if castle_right:
            hash ^= ZOBRIST_CASTLING[index]
    if gs.epSquare != -1:
        hash ^= ZOBRIST_EP[gs.epSquare % 8]
    return hash
