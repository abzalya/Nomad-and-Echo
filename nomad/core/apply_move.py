from nomad.core.move import MoveFlag
from nomad.core.bitboard import iterateBits, RANK_2, RANK_7
from nomad.core.zobrist import ZOBRIST_EP, ZOBRIST_CASTLING, ZOBRIST_PIECES, ZOBRIST_SIDE

#Piece-index constants matching the order used in ZOBRIST_PIECES.
_WP, _WR, _WN, _WB, _WQ, _WK = 0, 1, 2, 3, 4, 5
_BP, _BR, _BN, _BB, _BQ, _BK = 6, 7, 8, 9, 10, 11

#Castling rook squares as bitboards
_A1 = 1 << 0
_H1 = 1 << 7
_A8 = 1 << 56
_H8 = 1 << 63

def applyMove(gs, move):
    from_bb = 1 << move.from_sq
    to_bb   = 1 << move.to_sq
    flags   = move.flags

    captured_attr = None
    captured_sq   = None

    #1. Detect captured piece (regular capture)
    if flags & MoveFlag.CAPTURE:
        if gs.whiteToMove:
            #capturing a black piece
            if   gs.blackPawns   & to_bb: captured_attr = "blackPawns"
            elif gs.blackRooks   & to_bb: captured_attr = "blackRooks"
            elif gs.blackKnights & to_bb: captured_attr = "blackKnights"
            elif gs.blackBishops & to_bb: captured_attr = "blackBishops"
            elif gs.blackQueens  & to_bb: captured_attr = "blackQueens"
            elif gs.blackKing    & to_bb: captured_attr = "blackKing"
        else:
            if   gs.whitePawns   & to_bb: captured_attr = "whitePawns"
            elif gs.whiteRooks   & to_bb: captured_attr = "whiteRooks"
            elif gs.whiteKnights & to_bb: captured_attr = "whiteKnights"
            elif gs.whiteBishops & to_bb: captured_attr = "whiteBishops"
            elif gs.whiteQueens  & to_bb: captured_attr = "whiteQueens"
            elif gs.whiteKing    & to_bb: captured_attr = "whiteKing"
        captured_sq = move.to_sq

    #2. Detect captured piece (en passant — always a pawn)
    if flags & MoveFlag.EN_PASSANT:
        en_bb = (to_bb << 8) | (to_bb >> 8)
        en_bb &= ~RANK_2 & ~RANK_7
        if gs.whiteToMove:
            captured_attr = "blackPawns"
            captured_sq = next(iterateBits(gs.blackPawns & en_bb))
        else:
            captured_attr = "whitePawns"
            captured_sq = next(iterateBits(gs.whitePawns & en_bb))

    #3. Save history
    gs.history.append((
        move, captured_attr, captured_sq, gs.epSquare, gs.zobristHash,
        gs.wKingSideCastle, gs.wQueenSideCastle,
        gs.bKingSideCastle, gs.bQueenSideCastle,
        gs.halfMoveCounter, gs.pawnHash
    ))

    #4. XOR out old ep / castling
    if gs.epSquare != -1:
        gs.zobristHash ^= ZOBRIST_EP[gs.epSquare % 8]
    if gs.wKingSideCastle:  gs.zobristHash ^= ZOBRIST_CASTLING[0]
    if gs.wQueenSideCastle: gs.zobristHash ^= ZOBRIST_CASTLING[1]
    if gs.bKingSideCastle:  gs.zobristHash ^= ZOBRIST_CASTLING[2]
    if gs.bQueenSideCastle: gs.zobristHash ^= ZOBRIST_CASTLING[3]

    #5. Process regular capture (clear captured piece + revoke castling rights for rook captures)
    if flags & MoveFlag.CAPTURE:
        if   captured_attr == "blackPawns":
            gs.zobristHash ^= ZOBRIST_PIECES[_BP][move.to_sq]
            gs.blackPawns &= ~to_bb
            gs.pawnHash ^= ZOBRIST_PIECES[_BP][move.to_sq] #pawn hash
        elif captured_attr == "blackRooks":
            gs.zobristHash ^= ZOBRIST_PIECES[_BR][move.to_sq]
            gs.blackRooks &= ~to_bb
            if gs.bQueenSideCastle and to_bb == _A8:
                gs.bQueenSideCastle = False
            elif gs.bKingSideCastle and to_bb == _H8:
                gs.bKingSideCastle = False
        elif captured_attr == "blackKnights":
            gs.zobristHash ^= ZOBRIST_PIECES[_BN][move.to_sq]
            gs.blackKnights &= ~to_bb
        elif captured_attr == "blackBishops":
            gs.zobristHash ^= ZOBRIST_PIECES[_BB][move.to_sq]
            gs.blackBishops &= ~to_bb
        elif captured_attr == "blackQueens":
            gs.zobristHash ^= ZOBRIST_PIECES[_BQ][move.to_sq]
            gs.blackQueens &= ~to_bb
        elif captured_attr == "blackKing":
            gs.zobristHash ^= ZOBRIST_PIECES[_BK][move.to_sq]
            gs.blackKing &= ~to_bb
        elif captured_attr == "whitePawns":
            gs.zobristHash ^= ZOBRIST_PIECES[_WP][move.to_sq]
            gs.pawnHash ^= ZOBRIST_PIECES[_WP][move.to_sq] #pawn hash
            gs.whitePawns &= ~to_bb
        elif captured_attr == "whiteRooks":
            gs.zobristHash ^= ZOBRIST_PIECES[_WR][move.to_sq]
            gs.whiteRooks &= ~to_bb
            if gs.wQueenSideCastle and to_bb == _A1:
                gs.wQueenSideCastle = False
            elif gs.wKingSideCastle and to_bb == _H1:
                gs.wKingSideCastle = False
        elif captured_attr == "whiteKnights":
            gs.zobristHash ^= ZOBRIST_PIECES[_WN][move.to_sq]
            gs.whiteKnights &= ~to_bb
        elif captured_attr == "whiteBishops":
            gs.zobristHash ^= ZOBRIST_PIECES[_WB][move.to_sq]
            gs.whiteBishops &= ~to_bb
        elif captured_attr == "whiteQueens":
            gs.zobristHash ^= ZOBRIST_PIECES[_WQ][move.to_sq]
            gs.whiteQueens &= ~to_bb
        elif captured_attr == "whiteKing":
            gs.zobristHash ^= ZOBRIST_PIECES[_WK][move.to_sq]
            gs.whiteKing &= ~to_bb

    #6. Process en passant capture (clear captured pawn at captured_sq, not to_sq)
    if flags & MoveFlag.EN_PASSANT:
        captured_bit = 1 << captured_sq
        if gs.whiteToMove:
            gs.zobristHash ^= ZOBRIST_PIECES[_BP][captured_sq]
            gs.blackPawns &= ~captured_bit
            gs.pawnHash ^= ZOBRIST_PIECES[_BP][captured_sq] #pawn hash
        else:
            gs.zobristHash ^= ZOBRIST_PIECES[_WP][captured_sq]
            gs.whitePawns &= ~captured_bit
            gs.pawnHash ^= ZOBRIST_PIECES[_WP][captured_sq] #pawn hash

    #7. Promotion: clear pawn from from_sq, set promo piece on to_sq
    if flags & MoveFlag.PROMOTION:
        if gs.whiteToMove:
            gs.whitePawns &= ~from_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_WP][move.from_sq]
            gs.pawnHash ^= ZOBRIST_PIECES[_WP][move.from_sq] #pawn hash
        else:
            gs.blackPawns &= ~from_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_BP][move.from_sq]
            gs.pawnHash ^= ZOBRIST_PIECES[_BP][move.from_sq] #pawn hash
        promo = move.promo_piece
        if   promo == "whiteQueens":
            gs.whiteQueens |= to_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_WQ][move.to_sq]
        elif promo == "whiteRooks":
            gs.whiteRooks |= to_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_WR][move.to_sq]
        elif promo == "whiteBishops":
            gs.whiteBishops |= to_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_WB][move.to_sq]
        elif promo == "whiteKnights":
            gs.whiteKnights |= to_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_WN][move.to_sq]
        elif promo == "blackQueens":
            gs.blackQueens |= to_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_BQ][move.to_sq]
        elif promo == "blackRooks":
            gs.blackRooks |= to_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_BR][move.to_sq]
        elif promo == "blackBishops":
            gs.blackBishops |= to_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_BB][move.to_sq]
        elif promo == "blackKnights":
            gs.blackKnights |= to_bb
            gs.zobristHash ^= ZOBRIST_PIECES[_BN][move.to_sq]
        gs.epSquare = -1

    #8. Castling: move the rook (king is moved by main piece-move block below)
    if flags & MoveFlag.CASTLE_K:
        if gs.whiteToMove:
            gs.whiteRooks = (gs.whiteRooks & ~_H1) | (1 << 5)
            gs.zobristHash ^= ZOBRIST_PIECES[_WR][7]
            gs.zobristHash ^= ZOBRIST_PIECES[_WR][5]
        else:
            gs.blackRooks = (gs.blackRooks & ~_H8) | (1 << 61)
            gs.zobristHash ^= ZOBRIST_PIECES[_BR][63]
            gs.zobristHash ^= ZOBRIST_PIECES[_BR][61]
    if flags & MoveFlag.CASTLE_Q:
        if gs.whiteToMove:
            gs.whiteRooks = (gs.whiteRooks & ~_A1) | (1 << 3)
            gs.zobristHash ^= ZOBRIST_PIECES[_WR][0]
            gs.zobristHash ^= ZOBRIST_PIECES[_WR][3]
        else:
            gs.blackRooks = (gs.blackRooks & ~_A8) | (1 << 59)
            gs.zobristHash ^= ZOBRIST_PIECES[_BR][56]
            gs.zobristHash ^= ZOBRIST_PIECES[_BR][59]

    #9. Move the moving piece — skipped on promotion (pawn already cleared, promo piece placed)
    is_pawn_move = False
    if not (flags & MoveFlag.PROMOTION):
        if gs.whiteToMove:
            if gs.whitePawns & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_WP][move.from_sq] ^ ZOBRIST_PIECES[_WP][move.to_sq]
                gs.whitePawns = (gs.whitePawns & ~from_bb) | to_bb
                gs.pawnHash ^= ZOBRIST_PIECES[_WP][move.from_sq] ^ ZOBRIST_PIECES[_WP][move.to_sq] #pawn hash
                is_pawn_move = True
                if abs(move.to_sq - move.from_sq) == 16:
                    gs.epSquare = (move.from_sq + move.to_sq) // 2
                    gs.zobristHash ^= ZOBRIST_EP[gs.epSquare % 8]
                else:
                    gs.epSquare = -1
            elif gs.whiteRooks & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_WR][move.from_sq] ^ ZOBRIST_PIECES[_WR][move.to_sq]
                gs.whiteRooks = (gs.whiteRooks & ~from_bb) | to_bb
                gs.epSquare = -1
                if gs.wQueenSideCastle and from_bb == _A1:
                    gs.wQueenSideCastle = False
                elif gs.wKingSideCastle and from_bb == _H1:
                    gs.wKingSideCastle = False
            elif gs.whiteKnights & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_WN][move.from_sq] ^ ZOBRIST_PIECES[_WN][move.to_sq]
                gs.whiteKnights = (gs.whiteKnights & ~from_bb) | to_bb
                gs.epSquare = -1
            elif gs.whiteBishops & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_WB][move.from_sq] ^ ZOBRIST_PIECES[_WB][move.to_sq]
                gs.whiteBishops = (gs.whiteBishops & ~from_bb) | to_bb
                gs.epSquare = -1
            elif gs.whiteQueens & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_WQ][move.from_sq] ^ ZOBRIST_PIECES[_WQ][move.to_sq]
                gs.whiteQueens = (gs.whiteQueens & ~from_bb) | to_bb
                gs.epSquare = -1
            elif gs.whiteKing & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_WK][move.from_sq] ^ ZOBRIST_PIECES[_WK][move.to_sq]
                gs.whiteKing = (gs.whiteKing & ~from_bb) | to_bb
                gs.epSquare = -1
                gs.wKingSideCastle = False
                gs.wQueenSideCastle = False
        else:
            if gs.blackPawns & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_BP][move.from_sq] ^ ZOBRIST_PIECES[_BP][move.to_sq]
                gs.blackPawns = (gs.blackPawns & ~from_bb) | to_bb
                gs.pawnHash ^= ZOBRIST_PIECES[_BP][move.from_sq] ^ ZOBRIST_PIECES[_BP][move.to_sq] #pawn hash
                is_pawn_move = True
                if abs(move.to_sq - move.from_sq) == 16:
                    gs.epSquare = (move.from_sq + move.to_sq) // 2
                    gs.zobristHash ^= ZOBRIST_EP[gs.epSquare % 8]
                else:
                    gs.epSquare = -1
            elif gs.blackRooks & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_BR][move.from_sq] ^ ZOBRIST_PIECES[_BR][move.to_sq]
                gs.blackRooks = (gs.blackRooks & ~from_bb) | to_bb
                gs.epSquare = -1
                if gs.bQueenSideCastle and from_bb == _A8:
                    gs.bQueenSideCastle = False
                elif gs.bKingSideCastle and from_bb == _H8:
                    gs.bKingSideCastle = False
            elif gs.blackKnights & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_BN][move.from_sq] ^ ZOBRIST_PIECES[_BN][move.to_sq]
                gs.blackKnights = (gs.blackKnights & ~from_bb) | to_bb
                gs.epSquare = -1
            elif gs.blackBishops & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_BB][move.from_sq] ^ ZOBRIST_PIECES[_BB][move.to_sq]
                gs.blackBishops = (gs.blackBishops & ~from_bb) | to_bb
                gs.epSquare = -1
            elif gs.blackQueens & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_BQ][move.from_sq] ^ ZOBRIST_PIECES[_BQ][move.to_sq]
                gs.blackQueens = (gs.blackQueens & ~from_bb) | to_bb
                gs.epSquare = -1
            elif gs.blackKing & from_bb:
                gs.zobristHash ^= ZOBRIST_PIECES[_BK][move.from_sq] ^ ZOBRIST_PIECES[_BK][move.to_sq]
                gs.blackKing = (gs.blackKing & ~from_bb) | to_bb
                gs.epSquare = -1
                gs.bKingSideCastle = False
                gs.bQueenSideCastle = False

    #10. XOR in new castling rights
    if gs.wKingSideCastle:  gs.zobristHash ^= ZOBRIST_CASTLING[0]
    if gs.wQueenSideCastle: gs.zobristHash ^= ZOBRIST_CASTLING[1]
    if gs.bKingSideCastle:  gs.zobristHash ^= ZOBRIST_CASTLING[2]
    if gs.bQueenSideCastle: gs.zobristHash ^= ZOBRIST_CASTLING[3]

    #11. 50-move counter
    if flags & (MoveFlag.CAPTURE | MoveFlag.EN_PASSANT | MoveFlag.PROMOTION) or is_pawn_move:
        gs.halfMoveCounter = 0
    else:
        gs.halfMoveCounter += 1

    #12. Flip side
    gs.whiteToMove = not gs.whiteToMove
    gs.zobristHash ^= ZOBRIST_SIDE
    #pawnHash intentionally does NOT toggle side — pawn structure is the same
    #regardless of whose turn it is


def undoMove(gs):
    (move, captured_attr, captured_sq, ep, zhash, wk, wq, bk, bq, clock, phash) = gs.history.pop()
    from_bb = 1 << move.from_sq
    to_bb   = 1 << move.to_sq
    flags   = move.flags

    #Move the moving piece back from to_sq to from_sq.
    if flags & MoveFlag.PROMOTION:
        if not gs.whiteToMove: #white moved
            gs.whitePawns |= from_bb
            promo = move.promo_piece
            if   promo == "whiteQueens":  gs.whiteQueens  &= ~to_bb
            elif promo == "whiteRooks":   gs.whiteRooks   &= ~to_bb
            elif promo == "whiteBishops": gs.whiteBishops &= ~to_bb
            elif promo == "whiteKnights": gs.whiteKnights &= ~to_bb
        else:
            gs.blackPawns |= from_bb
            promo = move.promo_piece
            if   promo == "blackQueens":  gs.blackQueens  &= ~to_bb
            elif promo == "blackRooks":   gs.blackRooks   &= ~to_bb
            elif promo == "blackBishops": gs.blackBishops &= ~to_bb
            elif promo == "blackKnights": gs.blackKnights &= ~to_bb
    else:
        #Find moving piece on to_bb
        if not gs.whiteToMove:
            if   gs.whitePawns   & to_bb: gs.whitePawns   = (gs.whitePawns   & ~to_bb) | from_bb
            elif gs.whiteRooks   & to_bb: gs.whiteRooks   = (gs.whiteRooks   & ~to_bb) | from_bb
            elif gs.whiteKnights & to_bb: gs.whiteKnights = (gs.whiteKnights & ~to_bb) | from_bb
            elif gs.whiteBishops & to_bb: gs.whiteBishops = (gs.whiteBishops & ~to_bb) | from_bb
            elif gs.whiteQueens  & to_bb: gs.whiteQueens  = (gs.whiteQueens  & ~to_bb) | from_bb
            elif gs.whiteKing    & to_bb: gs.whiteKing    = (gs.whiteKing    & ~to_bb) | from_bb
        else:
            if   gs.blackPawns   & to_bb: gs.blackPawns   = (gs.blackPawns   & ~to_bb) | from_bb
            elif gs.blackRooks   & to_bb: gs.blackRooks   = (gs.blackRooks   & ~to_bb) | from_bb
            elif gs.blackKnights & to_bb: gs.blackKnights = (gs.blackKnights & ~to_bb) | from_bb
            elif gs.blackBishops & to_bb: gs.blackBishops = (gs.blackBishops & ~to_bb) | from_bb
            elif gs.blackQueens  & to_bb: gs.blackQueens  = (gs.blackQueens  & ~to_bb) | from_bb
            elif gs.blackKing    & to_bb: gs.blackKing    = (gs.blackKing    & ~to_bb) | from_bb

    #Restore captured piece
    if captured_attr is not None:
        captured_bit = 1 << captured_sq
        if   captured_attr == "blackPawns":   gs.blackPawns   |= captured_bit
        elif captured_attr == "blackRooks":   gs.blackRooks   |= captured_bit
        elif captured_attr == "blackKnights": gs.blackKnights |= captured_bit
        elif captured_attr == "blackBishops": gs.blackBishops |= captured_bit
        elif captured_attr == "blackQueens":  gs.blackQueens  |= captured_bit
        elif captured_attr == "blackKing":    gs.blackKing    |= captured_bit
        elif captured_attr == "whitePawns":   gs.whitePawns   |= captured_bit
        elif captured_attr == "whiteRooks":   gs.whiteRooks   |= captured_bit
        elif captured_attr == "whiteKnights": gs.whiteKnights |= captured_bit
        elif captured_attr == "whiteBishops": gs.whiteBishops |= captured_bit
        elif captured_attr == "whiteQueens":  gs.whiteQueens  |= captured_bit
        elif captured_attr == "whiteKing":    gs.whiteKing    |= captured_bit

    #Restore castled rooks
    if flags & MoveFlag.CASTLE_K:
        if not gs.whiteToMove:
            gs.whiteRooks = (gs.whiteRooks & ~(1 << 5)) | _H1
        else:
            gs.blackRooks = (gs.blackRooks & ~(1 << 61)) | _H8
    if flags & MoveFlag.CASTLE_Q:
        if not gs.whiteToMove:
            gs.whiteRooks = (gs.whiteRooks & ~(1 << 3)) | _A1
        else:
            gs.blackRooks = (gs.blackRooks & ~(1 << 59)) | _A8

    #Restore irreversible state
    gs.epSquare = ep
    gs.wKingSideCastle, gs.wQueenSideCastle = wk, wq
    gs.bKingSideCastle, gs.bQueenSideCastle = bk, bq
    gs.halfMoveCounter = clock
    gs.zobristHash = zhash
    gs.pawnHash = phash
    gs.whiteToMove = not gs.whiteToMove
