#mini-max with alpha-beta pruning
#negamax for simplicity
from engine.eval import evaluate
from core.move_generator import legalMoves
from core.apply_move import applyMove, undoMove
from core.attacks import isSquareAttacked

def negamax(gs, alpha, beta, depth):
    if depth == 0:
        score = evaluate(gs)
        return score if gs.whiteToMove else -score

    moves = legalMoves(gs)
    #checkmate, stalemate
    if not moves:
        ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        sq = ownKing.bit_length() - 1
        if isSquareAttacked(sq, gs):
            return -100000
        return 0

    for move in moves:
        applyMove(gs, move)
        score = -negamax(gs, -beta, -alpha, depth - 1)
        undoMove(gs)
        if score > alpha:
            alpha = score
        if alpha >= beta:
            return beta
    return alpha

def best_move(gs, depth):
    moves = legalMoves(gs)
    best = None
    alpha = -float("inf")
    beta = float("inf")
    for move in moves:
        applyMove(gs, move)
        score = -negamax(gs, -beta, -alpha, depth - 1)
        undoMove(gs)
        if score > alpha:
            alpha = score
            best = move
    return best
