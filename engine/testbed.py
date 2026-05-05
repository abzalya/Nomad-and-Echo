import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.game import Game
from engine.search import iterative_deepening
from engine.uci import uci_to_move, move_to_uci

OPERA_GAME = (
    "e2e4 e7e5 g1f3 d7d6 d2d4 c8g4 d4e5 g4f3 d1f3 d6e5 "
    "f1c4 g8f6 f3b3 d8e7 b1c3 c7c6 c1g5 b7b5 c3b5 c6b5 "
    "c4b5 b8d7 e1c1 a8d8 d1d7 d8d7 h1d1 e7e6 b5d7 f6d7 "
    "b3b8 d7b8 d1d8"
).split()

def run():
    game = Game()

    for i, uci in enumerate(OPERA_GAME):
        side = "white" if game.gs.whiteToMove else "black"
        move = uci_to_move(uci, game.legal_moves, game.gs.whiteToMove)
        if move is None:
            print(f"ERROR move {i+1}: illegal uci '{uci}'")
            break

        engine_move = iterative_deepening(game.gs, max_depth=3)
        engine_uci  = move_to_uci(engine_move) if engine_move else "none"

        # best_move already printed the info line above this
        print(f"  move {i+1:>2} ({side:>5})  game={uci}  engine={engine_uci}")
        print()

        game.apply(move)

    print("done.")

if __name__ == "__main__":
    run()
