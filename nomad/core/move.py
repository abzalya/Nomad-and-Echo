#Plain int constants
class MoveFlag:
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

    def __eq__(self, other):
        return (isinstance(other, Move)
                and self.from_sq == other.from_sq
                and self.to_sq == other.to_sq
                and self.promo_piece == other.promo_piece)
