import pygame as p
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import board

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

def main():
    screen = p.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),p.RESIZABLE)
    p.display.set_caption("Chess")

    gs = board.gameState()
    w, h = screen.get_size()
    loadImages(min(w, h) // 8)
    running = True

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        
        drawGameState(screen, gs)
        p.display.flip()

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
    ("wQ", "whiteQueen"),
    ("wK", "whiteKing"),
    ("bp", "blackPawns"),
    ("bR", "blackRooks"),
    ("bN", "blackKnights"),
    ("bB", "blackBishops"),
    ("bQ", "blackQueen"),
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




if __name__ == "__main__":
    main()