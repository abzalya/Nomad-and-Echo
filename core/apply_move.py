from core.move import MoveFlag
from core.bitboard import iterateBits, PIECE_BITBOARDS, RANK_2, RANK_7
from core.zobrist import PIECE_INDEX, ZOBRIST_EP, ZOBRIST_CASTLING, ZOBRIST_PIECES, ZOBRIST_SIDE

def applyMove(gs, move):
    #to undo move we need to save the irreversible stuff
    captured_attr = None
    captured_sq = None
    if move.flags & MoveFlag.CAPTURE:
        to_bb = 1 << move.to_sq
        for attr in PIECE_BITBOARDS:
            if getattr(gs,attr) & to_bb:
                captured_attr = attr
                captured_sq = move.to_sq
                break
    if move.flags & MoveFlag.EN_PASSANT:
        to_bb = 1 << move.to_sq
        en_bb = (to_bb << 8) | (to_bb >> 8)
        en_bb &= ~RANK_2 & ~RANK_7
        for attr in PIECE_BITBOARDS:
            bb = getattr(gs, attr)
            if bb & en_bb:
                captured_attr = attr
                captured_sq = next(iterateBits(bb & en_bb))
                break
    
    gs.history.append((
        move, captured_attr, captured_sq, gs.epSquare, gs.zobristHash,
        gs.wKingSideCastle, gs.wQueenSideCastle,
        gs.bKingSideCastle, gs.bQueenSideCastle,
        gs.halfMoveCounter,
    ))

    #first we xor out the old epSquare before updating
    if gs.epSquare != -1:
        gs.zobristHash ^= ZOBRIST_EP[gs.epSquare % 8]
    #same with castling rights
    for index, castle_right in enumerate([gs.wKingSideCastle, gs.wQueenSideCastle, gs.bKingSideCastle, gs.bQueenSideCastle]):
        if castle_right:
            gs.zobristHash ^= ZOBRIST_CASTLING[index]

    from_bb = 1 << move.from_sq
    to_bb = 1 << move.to_sq

    if move.flags & MoveFlag.CAPTURE:
        for attr, i in PIECE_INDEX.items():
            bb = getattr(gs, attr)
            if bb & to_bb:
                #xor out captured piece
                gs.zobristHash ^= ZOBRIST_PIECES[i][move.to_sq]
                setattr(gs, attr, bb & ~to_bb) #clears the "to" square
                #revoke castling rights if the rooks are captured
                if gs.wQueenSideCastle and to_bb == (1 << 0):
                    gs.wQueenSideCastle = False
                elif gs.wKingSideCastle and to_bb == (1 << 7):
                    gs.wKingSideCastle = False
                elif gs.bQueenSideCastle and to_bb == (1 << 56):
                    gs.bQueenSideCastle = False
                elif gs.bKingSideCastle and to_bb == (1 << 63):
                    gs.bKingSideCastle = False
                break

    if move.flags & MoveFlag.EN_PASSANT:
        for attr, i in PIECE_INDEX.items():
            bb = getattr(gs, attr)
            #we need to clear the position of the double pushed pawn
            #to square is always on rank rank 6 or rank 3
            #the position of the double push pawn is always on rank 4 or 5
            #look in both directions and then clear with masks
            en_bb = (to_bb << 8) | (to_bb >> 8)
            en_bb &= ~RANK_2 & ~RANK_7
            if bb & en_bb:
                #xor out captured pawn
                #needs square
                captured_pawn_bb = bb & en_bb
                captured_pawn_sq = next(iterateBits(captured_pawn_bb))
                gs.zobristHash ^= ZOBRIST_PIECES[i][captured_pawn_sq]
                setattr(gs, attr, bb & ~en_bb) #clears the double push square
                break

    if move.flags & MoveFlag.PROMOTION:
        if gs.whiteToMove:
            gs.whitePawns &= ~from_bb #remove pawn
            pawn_attr = "whitePawns"
        else:
            gs.blackPawns &= ~from_bb
            pawn_attr = "blackPawns"
        #xor out pawn xor in new piece
        gs.zobristHash ^= ZOBRIST_PIECES[PIECE_INDEX[pawn_attr]][move.from_sq]
        gs.zobristHash ^= ZOBRIST_PIECES[PIECE_INDEX[move.promo_piece]][move.to_sq]
        bb = getattr(gs, move.promo_piece)
        setattr(gs, move.promo_piece, bb | to_bb) #set the promotion piece on to_sq
        gs.epSquare = -1

    #because we added the flag, king movemnt is being handles as usual. this needs to only teleport the rook.
    if move.flags & MoveFlag.CASTLE_K:
        if gs.whiteToMove:
            rook_attr = "whiteRooks"
            rook_index = PIECE_INDEX[rook_attr]
            rook_from_sq, rook_to_sq = (7, 5)
            bb = getattr(gs, "whiteRooks")
            rook_from = (1 << 7) #h1
            rook_to = (1 << 5)   #f1
            setattr(gs, "whiteRooks", (bb & ~rook_from) | rook_to)
        else:
            rook_attr = "blackRooks"
            rook_index = PIECE_INDEX[rook_attr]
            rook_from_sq, rook_to_sq = (63, 61)
            bb = getattr(gs, "blackRooks")
            rook_from = (1 << 63) #h8
            rook_to = (1 << 61)   #f8
            setattr(gs, "blackRooks", (bb & ~rook_from) | rook_to)
        #xor out old rook xor in new rook
        gs.zobristHash ^= ZOBRIST_PIECES[rook_index][rook_from_sq]
        gs.zobristHash ^= ZOBRIST_PIECES[rook_index][rook_to_sq]

    if move.flags & MoveFlag.CASTLE_Q:
        if gs.whiteToMove:
            rook_attr = "whiteRooks"
            rook_index = PIECE_INDEX[rook_attr]
            rook_from_sq, rook_to_sq = (0, 3)
            bb = getattr(gs, "whiteRooks")
            rook_from = (1 << 0) #a1
            rook_to = (1 << 3)   #d1
            setattr(gs, "whiteRooks", (bb & ~rook_from) | rook_to)
        else:
            rook_attr = "blackRooks"
            rook_index = PIECE_INDEX[rook_attr]
            rook_from_sq, rook_to_sq = (56, 59)
            bb = getattr(gs, "blackRooks")
            rook_from = (1 << 56) #a8
            rook_to = (1 << 59)   #d8
            setattr(gs, "blackRooks", (bb & ~rook_from) | rook_to)
        gs.zobristHash ^= ZOBRIST_PIECES[rook_index][rook_from_sq]
        gs.zobristHash ^= ZOBRIST_PIECES[rook_index][rook_to_sq]

    for attr in PIECE_BITBOARDS:
        bb = getattr(gs, attr)
        if bb & from_bb:
            #xor out old, xor in new
            gs.zobristHash ^= ZOBRIST_PIECES[PIECE_INDEX[attr]][move.from_sq]
            gs.zobristHash ^= ZOBRIST_PIECES[PIECE_INDEX[attr]][move.to_sq]
            setattr(gs, attr, (bb & ~from_bb) | to_bb) #clears the "from" square and sets "to" square
            if attr in ("whitePawns", "blackPawns") and abs(move.to_sq - move.from_sq) == 16:
                gs.epSquare = (move.from_sq + move.to_sq) // 2
                gs.zobristHash ^= ZOBRIST_EP[gs.epSquare % 8]
            else:
                gs.epSquare = -1
            #revoke castling rights if pieces move from starting squares
            if attr == "whiteKing":
                gs.wKingSideCastle = False
                gs.wQueenSideCastle = False
            if attr == "blackKing":
                gs.bKingSideCastle = False
                gs.bQueenSideCastle = False
            if attr == "whiteRooks":
                if gs.wQueenSideCastle and from_bb == (1 << 0):
                    gs.wQueenSideCastle = False
                elif gs.wKingSideCastle and from_bb == (1 << 7):
                    gs.wKingSideCastle = False
            if attr == "blackRooks":
                if gs.bQueenSideCastle and from_bb == (1 << 56):
                    gs.bQueenSideCastle = False
                elif gs.bKingSideCastle and from_bb == (1 << 63):
                    gs.bKingSideCastle = False
            break

    #update zobrist with new castling rights
    for index, castle_right in enumerate([gs.wKingSideCastle, gs.wQueenSideCastle, gs.bKingSideCastle, gs.bQueenSideCastle]):
        if castle_right:
            gs.zobristHash ^= ZOBRIST_CASTLING[index]

    #50 move rule counter incrementation
    if move.flags & (MoveFlag.CAPTURE | MoveFlag.EN_PASSANT | MoveFlag.PROMOTION) or attr in ("whitePawns", "blackPawns"):
        gs.halfMoveCounter = 0
    else:
        gs.halfMoveCounter += 1

    gs.whiteToMove = not gs.whiteToMove
    #toggle zobrist side
    gs.zobristHash ^= ZOBRIST_SIDE

def undoMove(gs):
    (move, captured_attr, captured_sq, ep, zhash, wk, wq, bk, bq, clock) = gs.history.pop()
    from_bb = 1 << move.from_sq
    to_bb   = 1 << move.to_sq

    # moving the piece back
    if move.flags & MoveFlag.PROMOTION:
        pawn_attr = "whitePawns" if not gs.whiteToMove else "blackPawns"
        promoted_bb = getattr(gs, move.promo_piece)
        setattr(gs, move.promo_piece, promoted_bb & ~to_bb)
        pawn_bb = getattr(gs, pawn_attr)
        setattr(gs, pawn_attr, pawn_bb | from_bb)
    else:
        for attr in PIECE_BITBOARDS:
            bb = getattr(gs, attr)
            if bb & to_bb:
                setattr(gs, attr, (bb & ~to_bb) | from_bb)
                break

    #bring back captured piece
    if captured_attr is not None:
        bb = getattr(gs, captured_attr)
        setattr(gs, captured_attr, bb | (1 << captured_sq))

    #bring rooks back from castled squares
    if move.flags & MoveFlag.CASTLE_K:
        if not gs.whiteToMove:  # white castled
            bb = getattr(gs, "whiteRooks")
            setattr(gs, "whiteRooks", (bb & ~(1 << 5)) | (1 << 7))   # f1 → h1
        else:                   # black castled
            bb = getattr(gs, "blackRooks")
            setattr(gs, "blackRooks", (bb & ~(1 << 61)) | (1 << 63)) # f8 → h8

    if move.flags & MoveFlag.CASTLE_Q:
        if not gs.whiteToMove:  # white castled
            bb = getattr(gs, "whiteRooks")
            setattr(gs, "whiteRooks", (bb & ~(1 << 3)) | (1 << 0))   # d1 → a1
        else:                   # black castled
            bb = getattr(gs, "blackRooks")
            setattr(gs, "blackRooks", (bb & ~(1 << 59)) | (1 << 56)) # d8 → a8

    # restore irreversible state
    gs.epSquare = ep
    gs.wKingSideCastle, gs.wQueenSideCastle = wk, wq
    gs.bKingSideCastle, gs.bQueenSideCastle = bk, bq
    gs.halfMoveCounter = clock
    gs.zobristHash = zhash
    gs.whiteToMove = not gs.whiteToMove