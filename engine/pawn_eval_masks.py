FULL = 0xFFFFFFFFFFFFFFFF

FILE_MASKS = [0x0101010101010101 << file for file in range(8)]

ADJACENT_FILES_MASKS = [
    (FILE_MASKS[file - 1] if file > 0 else 0) | (FILE_MASKS[file + 1] if file < 7 else 0)
    for file in range(8)
]

def _passed_masks():
    white, black = [], []
    for sq in range(64):
        f, r = sq % 8, sq // 8
        files = FILE_MASKS[f] | ADJACENT_FILES_MASKS[f]
        above = (FULL << ((r + 1) * 8)) & FULL
        below = (1 << (r * 8)) - 1
        white.append(files & above)
        black.append(files & below)
    return [white, black]

PASSED_MASKS = _passed_masks()
