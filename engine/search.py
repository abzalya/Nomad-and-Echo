import time
from engine.eval import evaluate
from engine.move_order import movesOrdered
from core.move_generator import legalMoves, captureMovesOnly
from core.apply_move import applyMove, undoMove
from core.attacks import isSquareAttacked

class _Info:
    __slots__ = ("nodes", "start", "limit", "stop") #good optimisation for engines
    
    def __init__(self, limit):
        self.nodes = 0
        self.start = time.perf_counter()
        self.limit = limit
        self.stop = False
    
    def check(self):
        #check counter every 1024 nodes
        if self.limit and (self.nodes & 1023) == 0:
            if time.perf_counter() - self.start >= self.limit: #limit is set externally. if exceeded,
                self.stop = True #pull abort flag to True

def negamax(gs, alpha, beta, depth, info):
    info.nodes += 1 #increment nodes counter
    info.check()
    if info.stop:
        return 0

    if depth == 0:
        return quiescence(gs, alpha, beta, info, depth=0)

    moves = movesOrdered(legalMoves(gs),gs)
    if not moves:
        ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        sq = ownKing.bit_length() - 1
        if isSquareAttacked(sq, gs):
            return -100000
        return 0

    for move in moves:
        applyMove(gs, move)
        score = -negamax(gs, -beta, -alpha, depth - 1, info)
        undoMove(gs)
        if info.stop:
            return alpha #return best move so far
        if score > alpha:
            alpha = score
        if alpha >= beta:
            return beta
    return alpha

#search position for captures until quite. Should stop blunders in the middle of exchanges on the horizon
def quiescence(gs, alpha, beta, info, depth=0):
    info.nodes += 1
    info.check()
    if info.stop:
        return 0

    quiet_score = evaluate(gs)
    quiet_score = quiet_score if gs.whiteToMove else -quiet_score
    
    #quiescence depth limit. it kept blowing up my search
    if depth >= 8:
        return quiet_score
    
    if quiet_score >= beta: return beta
    alpha = max(alpha, quiet_score)
    moves = movesOrdered(captureMovesOnly(gs), gs)
    for move in moves:
        applyMove(gs, move)
        score = -quiescence(gs, -beta, -alpha, info, depth + 1)
        undoMove(gs)
        alpha = max(alpha, score)
        if alpha >= beta: return beta
    return alpha
#currently, we are generating all legal moves and then filtering for captures using captureMovesOnly. 
#as an optimisation it could be worth making a capture only generator down the line. I wonder how much an improvement it would be time wise. 



def best_move(gs, depth, time_limit=None):
    info = _Info(time_limit)
    moves = legalMoves(gs)
    best = None
    alpha = -float("inf")
    beta = float("inf")
    for move in moves:
        applyMove(gs, move)
        score = -negamax(gs, -beta, -alpha, depth - 1, info)
        undoMove(gs)
        if info.stop and best is not None:
            #keep best move found so far
            break
        if score > alpha:
            alpha = score
            best = move

    elapsed = time.perf_counter() - info.start
    nps = int(info.nodes / elapsed) if elapsed > 0 else 0 #0 devision guard
    eval = int(alpha) if alpha != -float("inf") else 0
    print(f"info depth {depth} score cp {eval} nodes {info.nodes} nps {nps} time {int(elapsed * 1000)}")
    return best
