#move to string for the move log
from nomad.core.move import MoveFlag
from nomad.core.bitboard import PIECE_BITBOARDS
from nomad.core.attacks import isSquareAttacked

PIECE_LETTER = {
    "whitePawns":   "",
    "whiteRooks":   "R",
    "whiteKnights": "N",
    "whiteBishops": "B",
    "whiteQueens":  "Q",
    "whiteKing":    "K",
    "blackPawns":   "",
    "blackRooks":   "R",
    "blackKnights": "N",
    "blackBishops": "B",
    "blackQueens":  "Q",
    "blackKing":    "K",
}

def move_to_str(gs, move, legal_moves):
    files = "abcdefgh"
    def sq(s): 
        return files[s % 8] + str(s // 8 + 1)

    #piece thats moving
    from_bb = 1 << move.from_sq
    for attr in PIECE_BITBOARDS:
        if getattr(gs,attr) & from_bb:
            piece_letter = PIECE_LETTER[attr]
            break

    #disambiguation. if two of the same peices can move to a sq. its file first, then rank
    from_file = ""
    from_rank = ""

    #pawns only during captures
    if piece_letter == "":
        if move.flags & MoveFlag.CAPTURE or move.flags & MoveFlag.EN_PASSANT:
            from_file = files[move.from_sq % 8]
    #pieces
    if piece_letter:
        piece_bb = getattr(gs, attr)
        ambiguous = [
            m for m in legal_moves
            if m.to_sq == move.to_sq
            and m.from_sq != move.from_sq
            and piece_bb & (1 << m.from_sq)
        ]
        if ambiguous:
            real_file = move.from_sq % 8
            real_rank = move.from_sq // 8
            shared_file = any(m.from_sq % 8 == real_file for m in ambiguous)
            if not shared_file:
                from_file = files[real_file]
            else:
                from_rank = str(real_rank + 1)
        
    #capture x
    if_capture = ""
    if move.flags & MoveFlag.CAPTURE:
        if_capture = "x"

    #to square
    to_sq = sq(move.to_sq)

    #promotion = 
    is_promotion = ""
    if move.flags & MoveFlag.PROMOTION:
        promo_letter = PIECE_LETTER[move.promo_piece]
        is_promotion = "=" + promo_letter
    
    #structure of the log
    log_string = piece_letter + from_file + from_rank + if_capture + to_sq + is_promotion

    #castling is completely different and overrides log_string
    if move.flags & MoveFlag.CASTLE_K:
        log_string = "0-0"
    if move.flags & MoveFlag.CASTLE_Q:
        log_string = "0-0-0"
    return log_string

#can only detect after move is applied
def is_check_checkmate_str(gs, game_status):
    king = gs.whiteKing if gs.whiteToMove else gs.blackKing
    king_sq = king.bit_length() - 1
    if game_status == "Checkmate":
        return "#"
    if isSquareAttacked(king_sq, gs):
        return "+"
    return ""