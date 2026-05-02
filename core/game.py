from core.board import GameState
from core.move_generator import legalMoves
from core.apply_move import applyMove
from core.attacks import isSquareAttacked
from core.draw_conditions import fiftyMoveRule, insufficientMaterial, threefoldRepetition

class Game:
    #new class owns the board state, the current legal move list, and the game outcome.
    def __init__(self):
        self.gs = GameState()
        self.legal_moves = legalMoves(self.gs)
        self.status = None

    def apply(self, move):
        applyMove(self.gs, move)
        self.gs.positionHistory[self.gs.zobristHash] = (
            self.gs.positionHistory.get(self.gs.zobristHash, 0) + 1
        )
        self.legal_moves = legalMoves(self.gs)
        self._update_status()

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
