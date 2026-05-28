"use client";

import { IconDownload } from "./Icons";
import type { Bot } from "./SidePanel";

export function GameEndModal({
  opponent = "nomad",
  result = "Checkmate. You win.",
  moves = 23,
  captures = "7",
  time = "6:42",
  onRematch,
  onNewGame,
  onReview,
  onPgn,
}: {
  opponent?: Bot;
  result?: string;
  moves?: number;
  captures?: string;
  time?: string;
  onRematch?: () => void;
  onNewGame?: () => void;
  onReview?: () => void;
  onPgn?: () => void;
}) {
  return (
    <>
      <div className="board-overlay" />
      <div className="game-end-modal">
        <div className="game-end-badge">
          <div className="text-xs subtle mono">RESULT</div>
          <div className="text-xl weight-700">{result}</div>
          <div className="text-sm muted">
            vs {opponent === "nomad" ? "Nomad" : "Echo"} · {moves} moves
          </div>
        </div>
        <div className="game-end-stats">
          <Stat label="Captures" value={captures} />
          <Stat label="Time" value={time} />
          <Stat label="Accuracy" value="—" />
        </div>
        <div className="game-end-actions">
          <button className="btn btn-primary" onClick={onRematch} type="button">
            Rematch
          </button>
          <button
            className="btn btn-secondary"
            onClick={onNewGame}
            type="button"
          >
            New game
          </button>
          <button className="btn btn-ghost" onClick={onReview} type="button">
            Review
          </button>
          <button className="btn btn-ghost" onClick={onPgn} type="button">
            <IconDownload size={16} /> PGN
          </button>
        </div>
      </div>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="game-end-stat">
      <span className="text-xs subtle mono">{label.toUpperCase()}</span>
      <span className="text-lg weight-500 mono">{value}</span>
    </div>
  );
}
