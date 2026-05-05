#https://www.chessprogramming.org/Transposition_Table
#always replace
#but there are some other strategies worth looking at later

EXACT = 0
LOWER = 1
UPPER = 2

_SIZE = 1 << 20  #1M slots
_TT   = [None] * _SIZE

def tt_get(zobrist_hash, depth):
    entry = _TT[zobrist_hash % _SIZE]
    if entry and entry[0] == zobrist_hash and entry[2] >= depth:
        return entry
    return None

def tt_store(zobrist_hash, score, depth, flag, best_move):
    _TT[zobrist_hash % _SIZE] = (zobrist_hash, score, depth, flag, best_move)
