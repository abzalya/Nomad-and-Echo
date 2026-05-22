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

FULL        = 0xFFFFFFFFFFFFFFFF
NOT_A_FILE  = 0xFEFEFEFEFEFEFEFE
NOT_H_FILE  = 0x7F7F7F7F7F7F7F7F
NOT_AB_FILE = 0xFCFCFCFCFCFCFCFC
NOT_GH_FILE = 0x3F3F3F3F3F3F3F3F
RANK_2      = 0x000000000000FF00
RANK_7      = 0x00FF000000000000
RANK_18     = 0xFF000000000000FF
