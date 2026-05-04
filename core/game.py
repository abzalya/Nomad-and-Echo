from core.board import GameState
from core.move_generator import legalMoves
from core.apply_move import applyMove, undoMove
from core.attacks import isSquareAttacked
from core.draw_conditions import fiftyMoveRule, insufficientMaterial, threefoldRepetition
from core.move_log import move_to_str, is_check_checkmate_str
from engine.eval import evaluate

class Game:
    #new class owns the board state, the current legal move list, and the game outcome.
    def __init__(self):
        self.gs = GameState()
        self.legal_moves = legalMoves(self.gs)
        self.status = None

    def apply(self, move):
        #moveLog strings for all legal_moves
        log_entry = move_to_str(self.gs, move, self.legal_moves)
        
        applyMove(self.gs, move)
        self.gs.positionHistory[self.gs.zobristHash] = (
            self.gs.positionHistory.get(self.gs.zobristHash, 0) + 1
        )
        self.legal_moves = legalMoves(self.gs)
        self._update_status()

        #moveLog check/checkmate str detection
        log_entry += is_check_checkmate_str(self.gs, self.status)
        self.gs.moveLog.append(log_entry)
        #testing moveLog as its not implemented yet in pygame
        print(f"{len(self.gs.moveLog)}. {log_entry}")

        #statis evaluation test
        eval = evaluate(self.gs)
        print(eval)

    def undo(self):
        if not self.gs.history:
            return
        undoMove(self.gs)
        self.gs.positionHistory[self.gs.zobristHash] = (
            self.gs.positionHistory.get(self.gs.zobristHash, 0) - 1
        )
        self.legal_moves = legalMoves(self.gs)
        self.status = None
        self._update_status()
        #pop moveLog entry
        self.gs.moveLog.pop()
        
    def moves_from(self, sq):
        return [m for m in self.legal_moves if m.from_sq == sq]

    def _update_status(self):
        if not self.legal_moves:
            ownKing = self.gs.whiteKing if self.gs.whiteToMove else self.gs.blackKing
            sq = ownKing.bit_length() - 1
            in_check = isSquareAttacked(sq, self.gs)
            self.status = "Checkmate" if in_check else "Stalemate"
            return
        if fiftyMoveRule(self.gs):
            self.status = "Draw by 50-Move Rule"
        elif insufficientMaterial(self.gs):
            self.status = "Draw - Insufficient Material"
        elif threefoldRepetition(self.gs):
            self.status = "Draw by Threefold Repetition"
