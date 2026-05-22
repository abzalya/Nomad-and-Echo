def insufficientMaterial(gs):
    notDrawPieces = gs.whitePawns | gs.whiteRooks | gs.whiteQueens | gs.blackPawns | gs.blackRooks | gs.blackQueens
    if notDrawPieces:
        return False
    wMinorPieces = gs.whiteKnights | gs.whiteBishops
    bMinorPieces =  gs.blackKnights | gs.blackBishops
    wCount = wMinorPieces.bit_count()
    bCount = bMinorPieces.bit_count()
    if wCount <= 1 and bCount <= 1:
        if gs.whiteBishops and gs.blackBishops:
            LIGHT_SQUARES = 0x55AA55AA55AA55AA
            return bool(gs.whiteBishops & LIGHT_SQUARES) == bool(gs.blackBishops & LIGHT_SQUARES)
        return True
    return False

def fiftyMoveRule(gs):
    if gs.halfMoveCounter >= 100:
        return True
    return False

#according to the wiki
#storing the Zobrist hash of each game position in a history stack and checking for three occurrences of the same hash, including castling rights, en passant, and side to move
def threefoldRepetition(gs):
    return gs.positionHistory.get(gs.zobristHash, 0) >= 3
