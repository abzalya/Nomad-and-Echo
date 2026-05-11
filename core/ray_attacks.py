from core.bitboard import FULL, NOT_A_FILE, NOT_H_FILE


# (shift_amount, file_mask, is_positive_shift)
_DIRECTIONS = (
    (8, FULL,       True),   # 0 N
    (9, NOT_A_FILE, True),   # 1 NE
    (1, NOT_A_FILE, True),   # 2 E
    (7, NOT_A_FILE, False),  # 3 SE
    (8, FULL,       False),  # 4 S
    (9, NOT_H_FILE, False),  # 5 SW
    (1, NOT_H_FILE, False),  # 6 W
    (7, NOT_H_FILE, True),   # 7 NW
)


def _ray(sq, shift, file_mask, positive):
    ray = 0
    bb = 1 << sq
    for _ in range(7):  # max length of a ray on an 8x8 board is 7
        if positive:
            bb = (bb << shift) & file_mask & FULL
        else:
            bb = (bb >> shift) & file_mask & FULL
        if bb == 0:
            break
        ray |= bb
    return ray


# Built once at import time. 8 directions × 64 squares = 512 bitboards.
RAY_ATTACKS = [
    [_ray(sq, shift, file_mask, positive) for sq in range(64)]
    for shift, file_mask, positive in _DIRECTIONS
]


# Direction indices where the nearest blocker is the LOWEST set bit.
# The other four (3, 4, 5, 6) are MSB-relevant
LSB_DIRECTIONS = frozenset({0, 1, 2, 7})
