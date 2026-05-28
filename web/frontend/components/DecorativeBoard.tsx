"use client";

import { Chessboard } from "react-chessboard";

// Reuse the in-game palette so the landing/setup board reads as the same product.
const SQ_LIGHT = "#e8d9c0";
const SQ_DARK = "#8a6440";

// Landing endgame position (R+P vs R+2P · black to move).
// FEN matches the design's `endgame` preset.
export const LANDING_FEN = "6k1/5p1p/8/3r4/6P1/5K2/R7/8 b - - 0 1";
export const SETUP_FEN = "r1bqkb1r/pp2nppp/2p2n2/3pp3/3PP3/2N2N2/PPP2PPP/R1BQKB1R w KQkq - 0 1";

export function DecorativeBoard({
  fen,
  showCoords = false,
  dimmed = false,
  orientation = "white",
}: {
  fen: string;
  showCoords?: boolean;
  dimmed?: boolean;
  orientation?: "white" | "black";
}) {
  return (
    <div className="board" style={{ position: "relative" }}>
      <Chessboard
        options={{
          position: fen,
          boardOrientation: orientation,
          showNotation: showCoords,
          allowDragging: false,
          allowDrawingArrows: false,
          showAnimations: false,
          darkSquareStyle: { backgroundColor: SQ_DARK },
          lightSquareStyle: { backgroundColor: SQ_LIGHT },
          boardStyle: { borderRadius: 10, overflow: "hidden" },
        }}
      />
      {dimmed && <div className="board-dim" />}
    </div>
  );
}
