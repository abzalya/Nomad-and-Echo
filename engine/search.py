import time
from engine.eval import evaluate
from engine.move_order import movesOrdered
from engine.tt import tt_get, tt_store, EXACT, LOWER, UPPER
from core.move_generator import generateMoves
from core.move import MoveFlag
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
        #check counter every 128 nodes. the time management was super off for python
        if self.limit and (self.nodes & 127) == 0:
            if time.perf_counter() - self.start >= self.limit: #limit is set externally. if exceeded,
                self.stop = True #pull abort flag to True

def negamax(gs, alpha, beta, depth, info):
    info.nodes += 1
    info.check()
    if info.stop:
        return 0

    if gs.positionHistory.get(gs.zobristHash, 0) >= 2:
        return 0

    original_alpha = alpha

    tt_move = None #best move from this position that was stored. pass into movesOrdered
    tt_entry = tt_get(gs.zobristHash, depth)
    if tt_entry:
        _, tt_score, _, tt_flag, tt_move = tt_entry
        if tt_flag == EXACT: #get exact score return early
            return tt_score
        if tt_flag == LOWER: #instantly tighten window
            alpha = max(alpha, tt_score)
        if tt_flag == UPPER:
            beta = min(beta, tt_score)
        if alpha >= beta:
            return tt_score

    if depth == 0:
        return quiescence(gs, alpha, beta, info, depth=0)

    moves = movesOrdered(generateMoves(gs), gs, tt_move)

    best = None
    legal_move_found = False
    for move in moves:
        applyMove(gs, move)

        #lazy legality check
        gs.whiteToMove = not gs.whiteToMove
        ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        sq = ownKing.bit_length() - 1
        illegal = isSquareAttacked(sq, gs)
        gs.whiteToMove = not gs.whiteToMove

        if illegal:
            undoMove(gs)
            continue

        legal_move_found = True
        score = -negamax(gs, -beta, -alpha, depth - 1, info)
        undoMove(gs)
        if info.stop:
            return 0
        if score > alpha:
            alpha = score
            best = move
        if alpha >= beta:
            tt_store(gs.zobristHash, beta, depth, LOWER, best)
            return beta

    if not legal_move_found:
        ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        sq = ownKing.bit_length() - 1
        return -100000 if isSquareAttacked(sq, gs) else 0

    flag = EXACT if alpha > original_alpha else UPPER
    tt_store(gs.zobristHash, alpha, depth, flag, best)
    return alpha

#search position for captures until quiet. Should stop blunders in the middle of exchanges on the horizon
def quiescence(gs, alpha, beta, info, depth=0):
    info.nodes += 1
    info.check()
    if info.stop:
        return 0

    ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
    in_check = isSquareAttacked(ownKing.bit_length() - 1, gs)

    if not in_check:
        quiet_score = evaluate(gs)
        quiet_score = quiet_score if gs.whiteToMove else -quiet_score

        #quiescence depth limit. it kept blowing up my search
        if depth >= 8:
            return quiet_score

        if quiet_score >= beta: return beta
        alpha = max(alpha, quiet_score)

    all_pseudo = generateMoves(gs)
    # in check: must search all moves for evasions; otherwise captures only
    candidates = all_pseudo if in_check else [m for m in all_pseudo if m.flags & MoveFlag.CAPTURE]

    legal_move_found = False
    for move in movesOrdered(candidates, gs):
        applyMove(gs, move)
        gs.whiteToMove = not gs.whiteToMove
        moverKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        illegal = isSquareAttacked(moverKing.bit_length() - 1, gs)
        gs.whiteToMove = not gs.whiteToMove

        if illegal:
            undoMove(gs)
            continue

        legal_move_found = True
        score = -quiescence(gs, -beta, -alpha, info, depth + 1)
        undoMove(gs)
        alpha = max(alpha, score)
        if alpha >= beta: return beta

    if in_check and not legal_move_found:
        return -100000

    return alpha
#as an optimisation it could be worth making a capture only generator down the line. I wonder how much an improvement it would be time wise. 



def best_move(gs, depth, info, last_best=None):
    moves = movesOrdered(generateMoves(gs), gs, last_best)
    best = None
    alpha = -10_000_000 #completely stop infinity from appearing large int values
    beta  =  10_000_000
    for move in moves:
        applyMove(gs, move)
        #lazy legality check
        gs.whiteToMove = not gs.whiteToMove
        ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        sq = ownKing.bit_length() - 1
        illegal = isSquareAttacked(sq, gs)
        gs.whiteToMove = not gs.whiteToMove

        if illegal:
            undoMove(gs)
            continue
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

MAX_DEPTH = 32

def iterative_deepening(gs, time_limit=None, max_depth=MAX_DEPTH):
    info = _Info(time_limit)
    last_best = None
    for depth in range(1, max_depth + 1):
        candidate = best_move(gs, depth, info, last_best)
        if info.stop and last_best is not None:
            break
        last_best = candidate #only returns best move of full depth X
    return last_best
