import copy
from core.move_generator import legalMoves, applyMove

#Counting total legal nodes at each depth from a starting position
def perft(gs, depth):
    if depth == 0:
        return 1
    moves = legalMoves(gs)
    if depth == 1:
        return len(moves)
    count = 0
    for move in moves:
        gs_copy = copy.deepcopy(gs)
        applyMove(gs_copy, move)
        count += perft(gs_copy, depth - 1) #recursive function
    return count