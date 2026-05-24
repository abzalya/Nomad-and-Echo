#lc0 is a UCI engine, so we pretend to be a GUI and talk to it that way, forwarding the best move to Echo
import subprocess
from chess import Board

class Maia:
    def __init__(self, elo: int, lc0_path: str, weights_dir: str, threads: int = 4, nodes: int = 3):
        weights = f"{weights_dir}/maia-{elo}.pb.gz"
        self.proc = subprocess.Popen(
            #[lc0_path, f"--weights={weights}", "--backend=blas"], #enable this line for linux
            [lc0_path, f"--weights={weights}"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1
        )
        self._send("uci"); self._read_until("uciok")
        self._send(f"setoption name Threads value {threads}")
        self._send("setoption name Temperature value 1.0")
        self._send("setoption name TempDecayMoves value 0")
        self.nodes = nodes
        self._send("isready"); self._read_until("readyok")

    def _send(self, cmd: str): self.proc.stdin.write(cmd + "\n"); self.proc.stdin.flush()
    def _read_until(self, token: str) -> str:
        while True:
            line = self.proc.stdout.readline()
            if token in line: return line

    def choose_move(self, board: Board) -> tuple[str, int]:
        import time
        self._send(f"position fen {board.fen()}")
        t0 = time.monotonic()
        self._send(f"go nodes {self.nodes}")
        line = self._read_until("bestmove")
        t_ms = int((time.monotonic() - t0) * 1000)
        return line.split()[1], t_ms

    def close(self):
        self._send("quit"); self.proc.wait(timeout=5)