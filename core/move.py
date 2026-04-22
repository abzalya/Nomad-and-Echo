from enum import IntFlag

class MoveFlag(IntFlag):
    NORMAL     = 0
    CAPTURE    = 1
    EN_PASSANT = 2
    CASTLE_K   = 4
    CASTLE_Q   = 8
    PROMOTION  = 16

class Move:
    def __init__(self, from_sq, to_sq, flags=MoveFlag.NORMAL, promo_piece=None):
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.flags = flags
        self.promo_piece = promo_piece
