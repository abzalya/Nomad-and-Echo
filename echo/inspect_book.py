import sys
import pickle
import chess
import chess.pgn
import chess.polyglot
from pathlib import Path

ECHO_ROOT = Path(__file__).parent
ARTIFACTS = ECHO_ROOT / "artifacts"
BOOK_PATH = ARTIFACTS / "echo_book.pkl"


def load_book() -> dict:
    with open(BOOK_PATH, "rb") as f:
        return pickle.load(f)


def cmd_stats(book: dict):
    total_positions = len(book)
    total_events = sum(sum(c.values()) for c in book.values())
    seen_2 = sum(1 for c in book.values() if sum(c.values()) >= 2)
    seen_5 = sum(1 for c in book.values() if sum(c.values()) >= 5)
    seen_10 = sum(1 for c in book.values() if sum(c.values()) >= 10)
    mean_moves = sum(len(c) for c in book.values()) / total_positions if total_positions else 0

    print(f"Total positions:           {total_positions:>10,}")
    print(f"Total move-events:         {total_events:>10,}")
    print(f"Positions seen >=2 times:  {seen_2:>10,}")
    print(f"Positions seen >=5 times:  {seen_5:>10,}")
    print(f"Positions seen >=10 times: {seen_10:>10,}")
    print(f"Mean moves per position:   {mean_moves:>10.2f}")


def cmd_lookup(book: dict, board: chess.Board):
    key = chess.polyglot.zobrist_hash(board)
    moves = book.get(key)
    if not moves:
        print("Position not in book.")
        return
    total = sum(moves.values())
    print(f"{total} times — move distribution:")
    for uci, count in sorted(moves.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {uci}: {count} ({pct:.0f}%)")


def parse_fen(fen: str) -> chess.Board:
    board = chess.Board(fen)
    return board


def parse_moves(moves_str: str) -> chess.Board:
    board = chess.Board()
    for uci in moves_str.split():
        board.push(chess.Move.from_uci(uci))
    return board


def usage():
    print("Usage:")
    print("  python inspect_book.py stats")
    print('  python inspect_book.py lookup "<fen>"')
    print('  python inspect_book.py lookup --after "e2e4 c7c5"')
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        usage()

    book = load_book()

    if args[0] == "stats":
        cmd_stats(book)

    elif args[0] == "lookup":
        if len(args) < 2:
            usage()
        if args[1] == "--after":
            if len(args) < 3:
                usage()
            board = parse_moves(args[2])
        else:
            board = parse_fen(args[1])
        cmd_lookup(book, board)

    else:
        usage()
