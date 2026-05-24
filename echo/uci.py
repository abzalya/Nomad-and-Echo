import sys
import chess
from echo.config import Config
from echo.echo import Echo


def parse_position(line: str) -> chess.Board:
    parts = line.split()
    moves_idx = parts.index("moves") if "moves" in parts else len(parts)
    move_list = parts[moves_idx + 1:]

    if parts[1] == "startpos":
        board = chess.Board()
    elif parts[1] == "fen":
        board = chess.Board(" ".join(parts[2:moves_idx]))
    else:
        board = chess.Board()

    for uci in move_list:
        try:
            board.push(chess.Move.from_uci(uci))
        except ValueError:
            pass
    return board


def print_id_and_options():
    print("id name Echo")
    print("id author Abzal Amirbay")
    print("option name UseBook type check default true")
    print("option name BookOnly type check default false")
    print("option name MaiaElo type combo default 1500 var 1400 var 1600 var 1700 var 1800 var 1900")
    print("uciok", flush=True)


def main():
    sys.stdin.reconfigure(encoding="utf-8-sig")
    cfg = Config()
    engine = Echo(cfg)
    board = chess.Board()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        if line == "uci":
            print_id_and_options()

        elif line == "isready":
            print("readyok", flush=True)

        elif line.startswith("setoption"):
            cfg.apply_setoption(line)

        elif line == "ucinewgame":
            board = chess.Board()

        elif line.startswith("position"):
            board = parse_position(line)

        elif line.startswith("go"):
            move, source = engine.choose_move(board)
            print(f"info string source={source}", flush=True)
            print(f"bestmove {move}", flush=True)

        elif line == "quit":
            break


if __name__ == "__main__":
    main()
