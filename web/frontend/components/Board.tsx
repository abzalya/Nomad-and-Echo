"use client";

import { useMemo, type CSSProperties } from "react";

// Unicode glyph placeholders for pieces. Production swap-in is cburnett SVGs
// via react-chessboard; this is good enough at preview fidelity.
export const PIECE_GLYPH: Record<string, string> = {
  wK: "♔", wQ: "♕", wR: "♖", wB: "♗", wN: "♘", wP: "♙",
  bK: "♚", bQ: "♛", bR: "♜", bB: "♝", bN: "♞", bP: "♟",
};

type PieceCode = keyof typeof PIECE_GLYPH | "";
type Row = readonly PieceCode[];
type Position = readonly Row[];

export const POSITIONS: Record<string, Position> = {
  midgame: [
    ["bR", "",   "bB", "bQ", "",   "bR", "bK", ""  ],
    ["bP", "bP", "",   "",   "bN", "bP", "bP", "bP"],
    ["",   "",   "bP", "",   "",   "bN", "",   ""  ],
    ["",   "",   "",   "bP", "bP", "",   "",   ""  ],
    ["",   "",   "",   "wP", "wP", "",   "",   ""  ],
    ["",   "",   "wN", "",   "",   "wN", "",   ""  ],
    ["wP", "wP", "wP", "",   "",   "wP", "wP", "wP"],
    ["wR", "",   "wB", "wQ", "wK", "wB", "",   "wR"],
  ],
  check: [
    ["bR", "",   "",   "",   "",   "bR", "bK", ""  ],
    ["bP", "",   "",   "",   "",   "bP", "bP", "bP"],
    ["",   "",   "bP", "",   "bQ", "bN", "",   ""  ],
    ["",   "",   "",   "bP", "",   "",   "",   ""  ],
    ["",   "",   "",   "wP", "",   "",   "",   ""  ],
    ["",   "",   "wN", "",   "",   "wN", "",   ""  ],
    ["wP", "wP", "wP", "",   "",   "wP", "wP", "wP"],
    ["wR", "",   "wB", "",   "wK", "wB", "",   "wR"],
  ],
  endgame: [
    ["",   "",   "",   "",   "",   "",   "bK", ""  ],
    ["",   "",   "",   "",   "",   "bP", "",   "bP"],
    ["",   "",   "",   "",   "",   "",   "",   ""  ],
    ["",   "",   "",   "bR", "",   "",   "",   ""  ],
    ["",   "",   "",   "",   "",   "",   "wP", ""  ],
    ["",   "",   "",   "",   "",   "wK", "",   ""  ],
    ["wR", "",   "",   "",   "",   "",   "",   ""  ],
    ["",   "",   "",   "",   "",   "",   "",   ""  ],
  ],
  promotion: [
    ["",   "",   "",   "",   "",   "",   "bK", ""  ],
    ["",   "",   "",   "",   "",   "wP", "bP", "bP"],
    ["",   "",   "",   "",   "",   "",   "bP", ""  ],
    ["",   "",   "",   "",   "",   "",   "",   ""  ],
    ["",   "",   "",   "",   "",   "",   "",   ""  ],
    ["",   "",   "wN", "",   "",   "",   "",   ""  ],
    ["wP", "wP", "wP", "",   "",   "wP", "wP", "wP"],
    ["wR", "",   "wB", "wQ", "wK", "wB", "",   "wR"],
  ],
};

const FILES = ["a", "b", "c", "d", "e", "f", "g", "h"] as const;
const RANKS = [8, 7, 6, 5, 4, 3, 2, 1] as const;
const rcToSq = (r: number, c: number) => FILES[c] + RANKS[r];

export type BoardState = "idle" | "selected" | "check" | "promotion" | "scrub";

type Overlay = {
  last?: boolean;
  selected?: boolean;
  check?: boolean;
  dot?: boolean;
  ring?: boolean;
  promoTarget?: boolean;
};

type BoardProps = {
  position?: keyof typeof POSITIONS;
  state?: BoardState;
  dimmed?: boolean;
  showCoords?: boolean;
  variant?: "main" | "decorative";
  size?: number | string;
};

export function Board({
  position = "midgame",
  state = "idle",
  dimmed = false,
  showCoords = true,
  variant = "main",
  size,
}: BoardProps) {
  const board = POSITIONS[position] ?? POSITIONS.midgame;

  const overlays = useMemo<Record<string, Overlay>>(() => {
    const o: Record<string, Overlay> = {};
    if (state === "idle") {
      o["d2"] = { last: true };
      o["d4"] = { last: true };
    } else if (state === "selected") {
      o["f3"] = { selected: true };
      o["d2"] = { last: true };
      o["d4"] = { last: true };
      ["e5", "g5", "h4", "g1", "e1", "d4"].forEach((sq) => {
        o[sq] = { ...(o[sq] ?? {}), dot: true };
      });
      o["d4"] = { ...(o["d4"] ?? {}), ring: true, dot: false };
    } else if (state === "check") {
      o["e1"] = { check: true };
      o["e4"] = { last: true };
      o["e3"] = { last: true };
    } else if (state === "promotion") {
      o["f7"] = { last: true };
      o["f8"] = { promoTarget: true, last: true };
    } else if (state === "scrub") {
      o["c3"] = { last: true };
      o["f3"] = { last: true };
    }
    return o;
  }, [state]);

  const sizeStyle: CSSProperties | undefined = size
    ? { width: size, height: size }
    : undefined;

  return (
    <div
      className={`board board-${variant} ${dimmed ? "board-dimmed" : ""}`}
      style={sizeStyle}
    >
      <div className="board-grid">
        {board.map((row, r) =>
          row.map((piece, c) => {
            const isDark = (r + c) % 2 === 1;
            const sq = rcToSq(r, c);
            const ov = overlays[sq] ?? {};
            const showFileCoord = showCoords && r === 7;
            const showRankCoord = showCoords && c === 0;
            return (
              <div
                key={sq}
                className={`sq ${isDark ? "sq-dark" : "sq-light"} ${
                  ov.last ? "sq-last" : ""
                } ${ov.selected ? "sq-selected" : ""} ${
                  ov.check ? "sq-check" : ""
                }`}
                data-sq={sq}
              >
                {showRankCoord && (
                  <span className="sq-coord sq-coord-rank mono">{RANKS[r]}</span>
                )}
                {showFileCoord && (
                  <span className="sq-coord sq-coord-file mono">{FILES[c]}</span>
                )}
                {ov.dot && <span className="sq-dot" />}
                {ov.ring && <span className="sq-ring" />}
                {piece && (
                  <span
                    className={`piece ${piece[0] === "w" ? "piece-w" : "piece-b"}`}
                  >
                    {PIECE_GLYPH[piece]}
                  </span>
                )}
                {ov.promoTarget && <PromotionPopover color="w" />}
              </div>
            );
          }),
        )}
      </div>
      {dimmed && <div className="board-dim" />}
    </div>
  );
}

export function PromotionPopover({ color = "w" }: { color?: "w" | "b" }) {
  const pieces =
    color === "w"
      ? (["wQ", "wN", "wR", "wB"] as const)
      : (["bQ", "bN", "bR", "bB"] as const);
  return (
    <div className="promo-popover">
      {pieces.map((p, i) => (
        <button
          key={p}
          className={`promo-piece ${i === 0 ? "promo-piece-active" : ""}`}
          aria-label={`Promote to ${p[1]}`}
          type="button"
        >
          <span className={`piece ${color === "w" ? "piece-w" : "piece-b"}`}>
            {PIECE_GLYPH[p]}
          </span>
        </button>
      ))}
    </div>
  );
}
