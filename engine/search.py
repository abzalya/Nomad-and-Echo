import time
from engine.eval import evaluate
from engine.move_order import movesOrdered, see, pieceValueOnSq
from engine.tt import tt_get, tt_store, EXACT, LOWER, UPPER
from core.move_generator import generateMoves, generateQuiescence
from core.move import MoveFlag
from core.apply_move import applyMove, undoMove
from core.attacks import isSquareAttacked, attackedBy, inCheck
from core.zobrist import ZOBRIST_SIDE, ZOBRIST_EP

MATE_SCORE     = 100000
MATE_THRESHOLD = 90000

LATE_MOVE_REDUCTION = {10: 1, 15:2, 20:3}

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
    __slots__ = ("nodes", "start", "limit", "stop", "killers", "history",
                 "last_score", "last_depth")

    def __init__(self, limit):
        self.nodes = 0
        self.start = time.perf_counter()
        self.limit = limit
        self.stop = False
        #ply index. Sized generously: extensions / deep tactical lines can
        #push ply past max_depth, and an IndexError here crashes the search.
        self.killers = [[None, None] for _ in range(256)]
        self.history = [[0] * 64 for _ in range(64)] #store as[from_sq][to_sq]
        #latest completed-depth score and depth, populated by best_move / iterative_deepening
        #used by the web API to report what the engine settled on
        self.last_score = 0
        self.last_depth = 0
    
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

    #in check 
    ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
    in_check = isSquareAttacked(ownKing.bit_length() - 1, gs) 

    #DISABLING static_eval in negamax until better move ordering and PVS for the other features
    #eval at the top of search for incoming RFP, FP, Razoring
    if in_check:
        static_eval = None
    else:
        static_eval, _ = evaluate(gs, alpha, beta)
        if not gs.whiteToMove:
            static_eval = -static_eval

    pv_node = (beta - alpha) > 1
    #will be false for a scout node, we can RFP and Razor prune here

    #DISABLING RFP AND RAZORING
    #RFP
    #doing so good that we can simply return static_eval
    if (1 <= depth <= 3 #depth can be tuned
        and not in_check
        and not pv_node 
        and abs(beta) < MATE_THRESHOLD):
        RFP_MARGIN = 120 * depth #margin can be tuned
        if static_eval - RFP_MARGIN >= beta:
            return beta #be conservative and return beta

    # #Razoring
    # #so hopeless that qsearch is below alpha, trust qsearch results
    if (1 <= depth <= 2 
        and not in_check 
        and not pv_node
        and abs(alpha) < MATE_THRESHOLD):
        RAZOR_MARGIN = 300 * depth #margin can be tuned
        if static_eval + RAZOR_MARGIN <= alpha:
            q_score = quiescence(gs, alpha, beta, info, depth=0, ply=ply)
            if q_score <= alpha:
                return q_score #qsearch cant save us. return early

    #main 40 – PVS+RFP 37 – 23 draws (score: 0.515, +10.4 Elo, LOS 63%). HMMMM

    if depth <= 0:
        return quiescence(gs, alpha, beta, info, depth=0, ply=ply)


    # Null move pruning — skip in check or zugzwang-prone positions
    if allow_null and depth >= 3 and _has_pieces(gs):
        if not in_check:
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

    #small optimization
    moves, _ = generateMoves(gs)
    moves = movesOrdered(moves, gs, tt_move, killers=info.killers[ply], history=info.history)
    
    #main search
    best = None
    legal_move_found = False
    move_index = 0
    for move in moves:
        #FP
        #quiet moves that dont increase eval above alpha with a margin are futile, skip
        #disable FP for now
        # if (depth <= 2 
        #     and not in_check 
        #     and not (move.flags & MoveFlag.CAPTURE) 
        #     and not (move.flags & MoveFlag.PROMOTION) 
        #     and abs(alpha) < MATE_THRESHOLD):
        #     FP_MARGIN = 150 * depth #margin can be tuned
        #     if static_eval + FP_MARGIN <= alpha:
        #         if not move.flags & MoveFlag.EN_PASSANT:
        #             legal_move_found = True
        #         continue
        
        
        applyMove(gs, move)
        if move.flags & MoveFlag.EN_PASSANT:
            gs.whiteToMove = not gs.whiteToMove
            moverKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
            illegal = isSquareAttacked(moverKing.bit_length() - 1, gs)
            gs.whiteToMove = not gs.whiteToMove
            if illegal:
                undoMove(gs)
                continue

        legal_move_found = True

        #PVS + LMR
        is_killer = move in info.killers[ply]
        if move_index == 0:
            #first move: full window, full depth (this is the PV move)
            score = -negamax(gs, -beta, -alpha, depth - 1, info, ply=ply+1)
        else:
            #scout with zero window
            if (depth >= 3 and move_index >= 10
                    and not in_check
                    and not (move.flags & MoveFlag.CAPTURE)
                    and not (move.flags & MoveFlag.PROMOTION)
                    and not is_killer):
                #LMR: reduced-depth scout
                reduction = max((r for t, r in LATE_MOVE_REDUCTION.items() if move_index >= t), default=1)
                score = -negamax(gs, -alpha - 1, -alpha, depth - 1 - reduction, info, ply=ply+1)
                if score > alpha:
                    #LMR failed high: re-search at full depth, still zero window
                    score = -negamax(gs, -alpha - 1, -alpha, depth - 1, info, ply=ply+1)
            else:
                #normal scout at full depth
                score = -negamax(gs, -alpha - 1, -alpha, depth - 1, info, ply=ply+1)

            #PVS re-search: scout suggests this might be a new PV
            if alpha < score < beta:
                score = -negamax(gs, -beta, -alpha, depth - 1, info, ply=ply+1)

        undoMove(gs)
        if info.stop:
            return 0
        if score > alpha:
            alpha = score
            best = move
        if alpha >= beta:
            #if a quiet moved caused a beta-cutoff in a sibling node at same depth, =killer
            if not (move.flags & MoveFlag.CAPTURE):
                if move != info.killers[ply][0]:
                    info.killers[ply][1] = info.killers[ply][0]
                    info.killers[ply][0] = move
                #tracks how often a move* caused a beta-cutoff in entirety of the search
                info.history[move.from_sq][move.to_sq] += depth * depth
            tt_store(gs.zobristHash, _score_to_tt(beta, ply), depth, LOWER, best)
            return beta

        move_index += 1

    if not legal_move_found:
        return -(MATE_SCORE - ply) if in_check else 0

    flag = EXACT if alpha > original_alpha else UPPER
    tt_store(gs.zobristHash, _score_to_tt(alpha, ply), depth, flag, best)
    return alpha

DELTA = 200

#search position for captures until quiet. Should stop blunders in the middle of exchanges on the horizon
def quiescence(gs, alpha, beta, info, depth=0, ply=0):
    info.nodes += 1
    info.check()
    if info.stop:
        return 0

    #faster than inCheck, targeted reverse lookup & has early returns. benefited from faster ray attacks implemented earlier
    ownKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
    in_check = isSquareAttacked(ownKing.bit_length() - 1, gs) 

    if not in_check:
        quiet_score, is_endgame = evaluate(gs, alpha, beta)
        quiet_score = quiet_score if gs.whiteToMove else -quiet_score

        #quiescence depth limit. it kept blowing up my search
        if depth >= 8:
            return quiet_score

        if quiet_score >= beta: return beta
        alpha = max(alpha, quiet_score)

    # in check: must search all moves for evasions; otherwise tactical moves only (captures, EP, all promotions)
    if in_check:
        candidates, _ = generateMoves(gs)
    else:
        candidates = generateQuiescence(gs)

    legal_move_found = False
    for move in movesOrdered(candidates, gs):
        if not in_check and not is_endgame: #disable delta pruning in endgames (total material < 3600)
            quiet_promo_score = 0
            if move.flags & MoveFlag.PROMOTION:
                quiet_promo_score = 800
            if quiet_score + pieceValueOnSq(move.to_sq, gs) + DELTA + quiet_promo_score <= alpha:
                continue        
        
        #before searching node, scheck see_score, skip loosing captures
        #even though move ordering orders winning captures* first, we are still checking see here, guard
        if not in_check: #add in_check guard
            victim = pieceValueOnSq(move.to_sq, gs) #classic mvvlva quick check before calling see
            attacker = pieceValueOnSq(move.from_sq, gs)
            if victim < attacker and see(move, gs) < 0:
                continue
        
        applyMove(gs, move)
        
        if move.flags & MoveFlag.EN_PASSANT:
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


def best_move(gs, depth, info, alpha, beta, last_best=None):
    moves, _ = generateMoves(gs)
    moves = movesOrdered(moves, gs, last_best)
    best = None
    best_score = alpha
    for move in moves:
        applyMove(gs, move)
        if move.flags & MoveFlag.EN_PASSANT:
            gs.whiteToMove = not gs.whiteToMove
            moverKing = gs.whiteKing if gs.whiteToMove else gs.blackKing
            illegal = isSquareAttacked(moverKing.bit_length() - 1, gs)
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
            best_score = score

    elapsed = time.perf_counter() - info.start
    nps = int(info.nodes / elapsed) if elapsed > 0 else 0 #0 devision guard
    if best is not None:
        score_str = _uci_score(int(alpha))
        print(f"info depth {depth} score {score_str} nodes {info.nodes} nps {nps} time {int(elapsed * 1000)}")
        #record the score+depth from this completed iteration so callers (web API) can read them
        info.last_score = int(alpha)
        info.last_depth = depth
    return best, best_score

MAX_DEPTH = 32

def iterative_deepening(gs, time_limit=None, max_depth=MAX_DEPTH, info=None):
    #info can be passed in by the caller (web API) to read back score/depth/nodes after the search.
    #for UCI/CLI callers, leaving it None preserves the original behavior.
    if info is None:
        info = _Info(time_limit)
    last_best_move = None

    #aspiration windows
    #search a narrow window around previous score (faster), if fails widen and re-search
    ASPIRATION_WINDOW = 25
    prev_score = 0
    for depth in range(1, max_depth + 1):

        if depth <= 4: #too shallow, full window
            alpha = -10_000_000
            beta  =  10_000_000
        else:
            alpha = prev_score - ASPIRATION_WINDOW
            beta = prev_score + ASPIRATION_WINDOW

        while True:
            candidate, score = best_move(gs, depth, info, alpha, beta, last_best_move)
            if info.stop:
                if candidate is not None:
                    last_best_move = candidate
                break
            if score <= alpha:
                alpha -= ASPIRATION_WINDOW * 2 #fail-low, widen alpha
            elif score >= beta:
                beta += ASPIRATION_WINDOW * 2 # fail-high, widen beta
            else:
                last_best_move = candidate
                prev_score = score
                break

        if info.stop:
            break
    return last_best_move