from core import zobrist

def gamestate_from_fen(fen_str):
    gs = GameState()
    gs.whitePawns = gs.whiteRooks = gs.whiteKnights = gs.whiteBishops = gs.whiteQueens = gs.whiteKing = 0
    gs.blackPawns = gs.blackRooks = gs.blackKnights = gs.blackBishops = gs.blackQueens = gs.blackKing = 0
    gs.wKingSideCastle = gs.wQueenSideCastle = gs.bKingSideCastle = gs.bQueenSideCastle = False

    parts = fen_str.split()
    placement, active, castling, ep = parts[0], parts[1], parts[2], parts[3]
    halfmove = int(parts[4]) if len(parts) > 4 else 0

    for r_idx, rank in enumerate(placement.split('/')):
        sq = (7 - r_idx) * 8
        for ch in rank:
            if ch.isdigit():
                sq += int(ch)
            else:
                bit = 1 << sq
                if   ch == 'P': gs.whitePawns   |= bit
                elif ch == 'R': gs.whiteRooks   |= bit
                elif ch == 'N': gs.whiteKnights |= bit
                elif ch == 'B': gs.whiteBishops |= bit
                elif ch == 'Q': gs.whiteQueens  |= bit
                elif ch == 'K': gs.whiteKing    |= bit
                elif ch == 'p': gs.blackPawns   |= bit
                elif ch == 'r': gs.blackRooks   |= bit
                elif ch == 'n': gs.blackKnights |= bit
                elif ch == 'b': gs.blackBishops |= bit
                elif ch == 'q': gs.blackQueens  |= bit
                elif ch == 'k': gs.blackKing    |= bit
                sq += 1

    gs.whiteToMove     = (active == 'w')
    gs.wKingSideCastle  = 'K' in castling
    gs.wQueenSideCastle = 'Q' in castling
    gs.bKingSideCastle  = 'k' in castling
    gs.bQueenSideCastle = 'q' in castling
    gs.halfMoveCounter  = halfmove

    if ep != '-':
        gs.epSquare = (int(ep[1]) - 1) * 8 + (ord(ep[0]) - ord('a'))
    else:
        gs.epSquare = -1

    gs.zobristHash = zobrist.computeHash(gs)
    return gs

class GameState:
    def __init__(self):
        self.whitePawns   = 0b0000000000000000000000000000000000000000000000001111111100000000
        self.whiteRooks   = 0b0000000000000000000000000000000000000000000000000000000010000001
        self.whiteKnights = 0b0000000000000000000000000000000000000000000000000000000001000010
        self.whiteBishops = 0b0000000000000000000000000000000000000000000000000000000000100100
        self.whiteQueens   = 0b0000000000000000000000000000000000000000000000000000000000001000
        self.whiteKing    = 0b0000000000000000000000000000000000000000000000000000000000010000
        self.blackPawns   = 0b0000000011111111000000000000000000000000000000000000000000000000
        self.blackRooks   = 0b1000000100000000000000000000000000000000000000000000000000000000
        self.blackKnights = 0b0100001000000000000000000000000000000000000000000000000000000000
        self.blackBishops = 0b0010010000000000000000000000000000000000000000000000000000000000
        self.blackQueens   = 0b0000100000000000000000000000000000000000000000000000000000000000
        self.blackKing    = 0b0001000000000000000000000000000000000000000000000000000000000000
        #so some bit wise ops for this are &, |, <<8 is move one up 
        #LSB is a1, MSB is h8
        self.whiteToMove = True
        self.moveLog = []
        self.epSquare = -1 #en passant square that was jumped over
        #castling rights check
        self.wKingSideCastle = True
        self.wQueenSideCastle = True
        self.bKingSideCastle = True
        self.bQueenSideCastle = True
        #50 move rule counter
        self.halfMoveCounter = 0
        #zobrist hash
        self.positionHistory = {}
        self.zobristHash = zobrist.computeHash(self)
        #undo move history
        self.history = []