import time
from engine.eval import evaluate
from engine.move_order import movesOrdered
from engine.tt import tt_get, tt_store, EXACT, LOWER, UPPER
from core.move_generator import generateMoves, generateQuiescence
from core.move import MoveFlag
from core.apply_move import applyMove, undoMove
from core.attacks import isSquareAttacked
from core.zobrist import ZOBRIST_SIDE, ZOBRIST_EP

MATE_SCORE     = 100000
MATE_THRESHOLD = 90000

def _score_to_tt(score, ply):
    if score > MATE_THRESHOLD:  return score + ply
    if score < -MATE_THRESHOLD: return score - ply
    return score

def _score_from_tt(score, ply):
    if score > MATE_THRESHOLD:  return score - ply
    if score < -MATE_THRESHOLD: return score + ply
    return score

def _uci_score(score):
    #distinguish mating moves with M N
    if score >= MATE_THRESHOLD:
        plies = MATE_SCORE - score
        return f"mate {(plies + 1) // 2}"
    if score <= -MATE_THRESHOLD:
        plies = MATE_SCORE + score
        return f"mate -{(plies + 1) // 2}"
    return f"cp {score}"

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

def _has_pieces(gs):
    if gs.whiteToMove:
        return (gs.whiteRooks | gs.whiteKnights | gs.whiteBishops | gs.whiteQueens) != 0
    return (gs.blackRooks | gs.blackKnights | gs.blackBishops | gs.blackQueens) != 0

def negamax(gs, alpha, beta, depth, info, allow_null=True, ply=0):
    info.nodes += 1
    info.check()
    if info.stop:
        return 0

    count = gs.positionHistory.get(gs.zobristHash, 0)
    if count >= 3:
        return 0
    if count >= 2:
        return -15

    original_alpha = alpha

    tt_move = None #best move from this position that was stored. pass into movesOrdered
    tt_entry = tt_get(gs.zobristHash, depth)
    if tt_entry:
        _, tt_score, _, tt_flag, tt_move = tt_entry
        tt_score = _score_from_tt(tt_score, ply)
        if tt_flag == EXACT: #get exact score return early
            return tt_score
        if tt_flag == LOWER: #instantly tighten window
            alpha = max(alpha, tt_score)
        if tt_flag == UPPER:
            beta = min(beta, tt_score)
        if alpha >= beta:
            return tt_score

    if depth == 0:
        return quiescence(gs, alpha, beta, info, depth=0, ply=ply)

    # Null move pruning — skip in check or zugzwang-prone positions
    if allow_null and depth >= 3 and _has_pieces(gs):
        ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        #guard check cheking as its a slower function
        if not isSquareAttacked(ownKing.bit_length() - 1, gs):
            R = 3 if depth >= 6 else 2
            ep_save = gs.epSquare
            if ep_save != -1:
                gs.zobristHash ^= ZOBRIST_EP[ep_save % 8]
            gs.epSquare = -1
            #skip turn
            gs.whiteToMove = not gs.whiteToMove
            gs.zobristHash ^= ZOBRIST_SIDE
            #negamax on skipped position with reduced depth
            null_score = -negamax(gs, -beta, -beta + 1, depth - 1 - R, info, allow_null=False, ply=ply+1)
            #undo skip
            gs.whiteToMove = not gs.whiteToMove
            gs.zobristHash ^= ZOBRIST_SIDE
            gs.epSquare = ep_save
            if ep_save != -1:
                gs.zobristHash ^= ZOBRIST_EP[ep_save % 8]
            if info.stop:
                return 0
            #if we skip our turn and opponent cant improve past beta, prune
            if null_score >= beta and abs(null_score) < 90000:
                return beta

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
        score = -negamax(gs, -beta, -alpha, depth - 1, info, ply=ply+1)
        undoMove(gs)
        if info.stop:
            return 0
        if score > alpha:
            alpha = score
            best = move
        if alpha >= beta:
            tt_store(gs.zobristHash, _score_to_tt(beta, ply), depth, LOWER, best)
            return beta

    if not legal_move_found:
        ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
        sq = ownKing.bit_length() - 1
        return -(MATE_SCORE - ply) if isSquareAttacked(sq, gs) else 0

    flag = EXACT if alpha > original_alpha else UPPER
    tt_store(gs.zobristHash, _score_to_tt(alpha, ply), depth, flag, best)
    return alpha

#search position for captures until quiet. Should stop blunders in the middle of exchanges on the horizon
def quiescence(gs, alpha, beta, info, depth=0, ply=0):
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

    # in check: must search all moves for evasions; otherwise tactical moves only (captures, EP, all promotions)
    candidates = generateMoves(gs) if in_check else generateQuiescence(gs)

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
        score = -quiescence(gs, -beta, -alpha, info, depth + 1, ply=ply+1)
        undoMove(gs)
        alpha = max(alpha, score)
        if alpha >= beta: return beta

    if in_check and not legal_move_found:
        return -(MATE_SCORE - ply)

    return alpha


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
        score = -negamax(gs, -beta, -alpha, depth - 1, info, ply=1)
        undoMove(gs)
        if info.stop:
            break
        if score > alpha:
            alpha = score
            best = move

    elapsed = time.perf_counter() - info.start
    nps = int(info.nodes / elapsed) if elapsed > 0 else 0 #0 devision guard
    if best is not None:
        score_str = _uci_score(int(alpha))
        print(f"info depth {depth} score {score_str} nodes {info.nodes} nps {nps} time {int(elapsed * 1000)}")
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
