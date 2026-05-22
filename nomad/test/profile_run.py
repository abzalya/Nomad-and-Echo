import cProfile
import pstats
import io
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
print("starting profile...", flush=True)
from nomad.core.game import Game
from nomad.core.move import MoveFlag
from nomad.engine.search import iterative_deepening
from nomad.engine.uci import uci_to_move

# Position from the Opera game, just before the queen sac — rich middlegame
OPENING = "e2e4 e7e5 g1f3 d7d6 d2d4 c8g4 d4e5 g4f3 d1f3 d6e5 f1c4 g8f6 f3b3 d8e7 b1c3 c7c6 c1g5 b7b5 c3b5 c6b5 c4b5 b8d7 e1c1 a8d8".split()

# A second position — the starting position — to see eval cost without much development
STARTPOS = []

def make_game(moves):
    g = Game()
    for u in moves:
        m = uci_to_move(u, g.legal_moves, g.gs.whiteToMove)
        if m is None:
            raise SystemExit(f"illegal move {u}")
        g.apply(m)
    return g

def workload():
    # Two positions, depth 4 each. Quick enough in interpreted mode.
    print("  searching opening position...", flush=True)
    g1 = make_game(OPENING)
    iterative_deepening(g1.gs, max_depth=4)
    print("  searching startpos...", flush=True)
    g2 = make_game(STARTPOS)
    iterative_deepening(g2.gs, max_depth=4)
    print("  done.", flush=True)

if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    workload()
    pr.disable()

    print("=" * 80)
    print("TOP 25 BY CUMULATIVE TIME (includes time spent in callees)")
    print("=" * 80)
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(25)
    print(s.getvalue())

    print("=" * 80)
    print("TOP 25 BY TOTTIME (time spent IN the function itself, exclusive)")
    print("=" * 80)
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(25)
    print(s.getvalue())

    print("=" * 80)
    print("CALLERS OF HOTTEST FUNCTIONS")
    print("=" * 80)
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats("tottime").print_callers(15)
    print(s.getvalue())
