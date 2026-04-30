import pygame as p
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import board
from core import move_generator
from core.move import MoveFlag

p.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
BLACK_SQUARE_COLOUR = (181,136,99)
WHITE_SQUARE_COLOUR = (240,217,181)
OVERLAY_SQUARE_COLOUR = (230, 112, 112)

IMAGES = {}

def loadImages(square_size):
    pieces = [key for key, _ in PIECE_BITBOARDS]
    piece_size = int(square_size * 0.9)
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("assets/pieces/" + piece + ".png"), (piece_size, piece_size))

def drawGameState(screen, gs):
    w, h = screen.get_size()
    square_size = min(w, h) // 8
    board_start_x = (w - square_size * 8) // 2
    board_start_y = (h - square_size * 8) // 2
    
    drawBoard(square_size, board_start_x, board_start_y, screen)
    drawPieces(square_size, board_start_x, board_start_y, screen, gs)

def drawBoard(square_size, board_start_x, board_start_y, screen):
    for i in range(8):
        for j in range(8):
            boardx = board_start_x + square_size * j
            boardy = board_start_y + square_size * i
            colour = WHITE_SQUARE_COLOUR if (i + j) % 2 == 0 else BLACK_SQUARE_COLOUR
            p.draw.rect(screen, colour, (boardx, boardy, square_size, square_size))

def iterateBits(bb):
    while bb:
        lsb = bb & -bb
        yield lsb.bit_length() - 1
        bb &= bb - 1

PIECE_BITBOARDS = [
    ("wp", "whitePawns"),
    ("wR", "whiteRooks"),
    ("wN", "whiteKnights"),
    ("wB", "whiteBishops"),
    ("wQ", "whiteQueens"),
    ("wK", "whiteKing"),
    ("bp", "blackPawns"),
    ("bR", "blackRooks"),
    ("bN", "blackKnights"),
    ("bB", "blackBishops"),
    ("bQ", "blackQueens"),
    ("bK", "blackKing"),
]

def getPieceSquares(gs):
    for key, attr in PIECE_BITBOARDS:
        for sq in iterateBits(getattr(gs, attr)):
            yield (key, sq % 8, 7 - sq // 8)

def drawPieces(square_size, board_start_x, board_start_y, screen, gs):
    offset = (square_size - int(square_size * 0.9)) // 2

    for key, col, row in getPieceSquares(gs):
        x = board_start_x + square_size * col + offset
        y = board_start_y + square_size * row + offset
        screen.blit(IMAGES[key], (x, y))


def screenToSquare(mx, my, board_start_x, board_start_y, square_size):
    col = (mx - board_start_x) // square_size
    row = (my - board_start_y) // square_size
    if 0 <= col < 8 and 0 <= row < 8:
        return (7 - row) * 8 + col
    return None

def drawHighlights(screen, moves, square_size, board_start_x, board_start_y):
    radius = square_size // 6
    for m in moves:
        col = m.to_sq % 8
        row = 7 - m.to_sq // 8
        bx = board_start_x + col * square_size
        by = board_start_y + row * square_size
        s = p.Surface((square_size, square_size), p.SRCALPHA)
        p.draw.circle(s, (50, 50, 50, 130), (square_size // 2, square_size // 2), radius)
        screen.blit(s, (bx, by))

PROMO_ATTR_TO_KEY = {
    "whiteQueens": "wQ", "whiteRooks": "wR", "whiteBishops": "wB", "whiteKnights": "wN",
    "blackQueens": "bQ", "blackRooks": "bR", "blackBishops": "bB", "blackKnights": "bN",
}

def drawPromotionPicker(screen, pendingPromotions, whiteToMove):
    w, h = screen.get_size()
    square_size = min(w, h) // 8
    board_start_x = (w - square_size * 8) // 2
    board_start_y = (h - square_size * 8) // 2
    offset = (square_size - int(square_size * 0.9)) // 2

    to_sq = pendingPromotions[0].to_sq
    col = to_sq % 8
    base_row = 7 - to_sq // 8  # 0 for white (rank 8 top), 7 for black (rank 1 bottom)

    background = screen.copy()

    while True:
        screen.blit(background, (0, 0))
        overlay = p.Surface((w, h), p.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        rects = []
        for i, m in enumerate(pendingPromotions):
            picker_row = base_row + i if whiteToMove else base_row - i
            bx = board_start_x + col * square_size
            by = board_start_y + picker_row * square_size
            rect = p.Rect(bx, by, square_size, square_size)
            rects.append((rect, m))
            p.draw.rect(screen, (235, 235, 210), rect)
            p.draw.rect(screen, (80, 80, 80), rect, 2)
            screen.blit(IMAGES[PROMO_ATTR_TO_KEY[m.promo_piece]], (bx + offset, by + offset))

        p.display.flip()

        for e in p.event.get():
            if e.type == p.QUIT:
                return None
            if e.type == p.MOUSEBUTTONDOWN:
                for rect, m in rects:
                    if rect.collidepoint(e.pos):
                        return m

def drawStatus(screen, status):
    font = p.font.SysFont("Helvetica", 48, bold=True)
    w, h = screen.get_size()
    text = font.render(status, True, (220, 20, 20))
    rect = text.get_rect(center=(w//2, h//2))
    # semi-transparent backing
    s = p.Surface((rect.width + 20, rect.height + 10), p.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (rect.x - 10, rect.y - 5))
    screen.blit(text, rect)

def main():
    screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), p.RESIZABLE)
    p.display.set_caption("Chess")

    gs = board.gameState()
    w, h = screen.get_size()
    loadImages(min(w, h) // 8)
    running = True

    allLegalMoves = move_generator.legalMoves(gs)
    selectedSq = None
    movesFromSelected = []
    gameStatus = ""
    pendingPromotions = []

    while running:
        w, h = screen.get_size()
        square_size = min(w, h) // 8
        board_start_x = (w - square_size * 8) // 2
        board_start_y = (h - square_size * 8) // 2

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN and not gameStatus:
                sq = screenToSquare(e.pos[0], e.pos[1], board_start_x, board_start_y, square_size)
                if sq is None:
                    selectedSq = None
                    movesFromSelected = []
                elif selectedSq is None:
                    selectedSq = sq
                    movesFromSelected = [m for m in allLegalMoves if m.from_sq == sq]
                else:
                    move = next((m for m in movesFromSelected if m.to_sq == sq), None)
                    if move:
                        if move.flags & MoveFlag.PROMOTION:
                            pendingPromotions = [m for m in movesFromSelected if m.to_sq == sq]
                            selectedSq = None
                            movesFromSelected = []
                            chosenPromotion = drawPromotionPicker(screen, pendingPromotions, gs.whiteToMove)
                            if chosenPromotion:
                                move_generator.applyMove(gs, chosenPromotion)
                                allLegalMoves = move_generator.legalMoves(gs)
                                pendingPromotions = []
                        else:
                            move_generator.applyMove(gs, move)
                            allLegalMoves = move_generator.legalMoves(gs)
                            selectedSq = None
                            movesFromSelected = []
                            if not allLegalMoves: #due to reverse lookup inCheck function inverting colors. need to flip whiteToMove before calling.
                                gs.whiteToMove = not gs.whiteToMove
                                in_check = move_generator.inCheck(gs)
                                gs.whiteToMove = not gs.whiteToMove
                                gameStatus = "Checkmate" if in_check else "Stalemate"

                    else:
                        # clicking a different piece: swap selection immediately
                        newMoves = [m for m in allLegalMoves if m.from_sq == sq]
                        if newMoves:
                            selectedSq = sq
                            movesFromSelected = newMoves
                        else:
                            selectedSq = None
                            movesFromSelected = []

        drawGameState(screen, gs)
        drawHighlights(screen, movesFromSelected, square_size, board_start_x, board_start_y)
        if gameStatus:
            drawStatus(screen, gameStatus)
        p.display.flip()

if __name__ == "__main__":
    main()