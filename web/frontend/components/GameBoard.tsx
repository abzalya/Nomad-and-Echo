"use client";

import { useMemo, type CSSProperties } from "react";
import { Chessboard } from "react-chessboard";
import { Chess, type Square } from "chess.js";
import { useGame, legalMovesFrom, checkedKingSquare, lastMoveSquares } from "@/lib/game";
import { useSettings } from "@/lib/settings";
import { PIECE_GLYPH } from "./Board";

const FILES = ["a", "b", "c", "d", "e", "f", "g", "h"] as const;

// Colors and styling pulled from CSS custom properties — keeps the design
// tokens authoritative. We pass them as raw values because react-chessboard
// inlines styles and `var(--…)` resolution inside `boxShadow` is browser-
// sensitive.
const SQ_LIGHT = "#e8d9c0";
const SQ_DARK = "#8a6440";
const SQ_LAST = "rgba(194, 65, 12, 0.22)";
const SQ_SELECTED = "rgba(194, 65, 12, 0.35)";
const SQ_DOT = "rgba(28, 16, 8, 0.25)";
const SQ_CAPTURE = "rgba(220, 38, 38, 0.55)";
const SQ_CHECK = "rgba(220, 38, 38, 0.45)";
const ACCENT = "#c2410c";

export function GameBoard() {
  const liveFen = useGame((s) => s.fen);
  const initialFen = useGame((s) => s.initialFen);
  const history = useGame((s) => s.history);
  const playerColor = useGame((s) => s.playerColor);
  const selected = useGame((s) => s.selectedSquare);
  const status = useGame((s) => s.status);
  const scrubIndex = useGame((s) => s.scrubIndex);
  const botThinking = useGame((s) => s.botThinking);
  const hint = useGame((s) => s.hintHighlight);
  const pendingPromotion = useGame((s) => s.pendingPromotion);
  const selectSquare = useGame((s) => s.selectSquare);
  const userMove = useGame((s) => s.userMove);
  const applyPendingPromotion = useGame((s) => s.applyPendingPromotion);
  const cancelPromotion = useGame((s) => s.cancelPromotion);

  const showDots = useSettings((s) => s.showDots);
  const showCoords = useSettings((s) => s.showCoords);
  const autoQueen = useSettings((s) => s.autoPromoteQueen);

  // When scrubbing, replay history up to scrubIndex to show the historical FEN.
  const fen = useMemo(() => {
    if (scrubIndex === null) return liveFen;
    const board = new Chess(initialFen);
    for (let i = 0; i <= scrubIndex && i < history.length; i++) {
      const uci = history[i];
      board.move({
        from: uci.slice(0, 2),
        to: uci.slice(2, 4),
        promotion: uci.length === 5 ? (uci[4] as "q" | "r" | "b" | "n") : undefined,
      });
    }
    return board.fen();
  }, [liveFen, initialFen, history, scrubIndex]);

  const interactive =
    status === "playing" &&
    scrubIndex === null &&
    !pendingPromotion &&
    !botThinking;

  // Last-move highlight follows the displayed position, not always the live one.
  const visibleHistory = useMemo(
    () => (scrubIndex === null ? history : history.slice(0, scrubIndex + 1)),
    [history, scrubIndex],
  );
  const last = useMemo(() => lastMoveSquares(visibleHistory), [visibleHistory]);
  const check = useMemo(() => checkedKingSquare(fen), [fen]);
  const legal = useMemo(
    () => (selected && interactive ? legalMovesFrom(fen, selected) : []),
    [selected, fen, interactive],
  );

  const squareStyles = useMemo<Record<string, CSSProperties>>(() => {
    const out: Record<string, CSSProperties> = {};
    if (last) {
      out[last.from] = { ...(out[last.from] ?? {}), boxShadow: `inset 0 0 0 9999px ${SQ_LAST}` };
      out[last.to] = { ...(out[last.to] ?? {}), boxShadow: `inset 0 0 0 9999px ${SQ_LAST}` };
    }
    if (selected) {
      out[selected] = { ...(out[selected] ?? {}), boxShadow: `inset 0 0 0 9999px ${SQ_SELECTED}` };
    }
    if (showDots) {
      for (const m of legal) {
        if (m.captured) {
          out[m.to] = {
            ...(out[m.to] ?? {}),
            boxShadow: `inset 0 0 0 4px ${SQ_CAPTURE}`,
          };
        } else {
          out[m.to] = {
            ...(out[m.to] ?? {}),
            backgroundImage: `radial-gradient(circle, ${SQ_DOT} 14%, transparent 15%)`,
          };
        }
      }
    }
    if (check) {
      out[check] = {
        ...(out[check] ?? {}),
        backgroundImage: `radial-gradient(circle at center, ${SQ_CHECK} 0%, ${SQ_CHECK} 30%, transparent 70%)`,
      };
    }
    if (hint) {
      out[hint.from] = {
        ...(out[hint.from] ?? {}),
        boxShadow: `inset 0 0 0 3px ${ACCENT}`,
      };
      out[hint.to] = {
        ...(out[hint.to] ?? {}),
        boxShadow: `inset 0 0 0 3px ${ACCENT}`,
      };
    }
    return out;
  }, [last, selected, legal, check, hint, showDots]);

  return (
    <div className="board-wrap">
      <Chessboard
        options={{
          position: fen,
          boardOrientation: playerColor === "w" ? "white" : "black",
          showNotation: showCoords,
          allowDragging: interactive,
          animationDurationInMs: 150,
          darkSquareStyle: { backgroundColor: SQ_DARK },
          lightSquareStyle: { backgroundColor: SQ_LIGHT },
          boardStyle: { borderRadius: 10, overflow: "hidden" },
          squareStyles,
          onSquareClick: ({ square, piece }) => {
            if (!interactive) return;
            const sq = square as Square;
            if (selected) {
              if (sq === selected) {
                selectSquare(null);
                return;
              }
              const ok = userMove(selected, sq, autoQueen ? "q" : undefined);
              if (!ok && piece) {
                selectSquare(sq);
              }
              return;
            }
            if (piece) selectSquare(sq);
          },
          onPieceDrop: ({ sourceSquare, targetSquare }) => {
            if (!interactive || !targetSquare) return false;
            const ok = userMove(
              sourceSquare as Square,
              targetSquare as Square,
              autoQueen ? "q" : undefined,
            );
            return ok;
          },
        }}
      />
      {pendingPromotion && (
        <PromotionOverlay
          color={playerColor}
          targetSquare={pendingPromotion.to}
          onPick={applyPendingPromotion}
          onCancel={cancelPromotion}
        />
      )}
    </div>
  );
}

function PromotionOverlay({
  color,
  targetSquare,
  onPick,
  onCancel,
}: {
  color: "w" | "b";
  targetSquare: string;
  onPick: (p: "q" | "r" | "b" | "n") => void;
  onCancel: () => void;
}) {
  // The promoting side always reaches the visual TOP of the board: white
  // promotes onto rank 8 (top with orientation=white), black promotes onto
  // rank 1 (top with orientation=black). File ordering flips with orientation.
  const file = FILES.indexOf(targetSquare[0] as (typeof FILES)[number]);
  const visualCol = color === "w" ? file : 7 - file;
  const left = `${(visualCol * 100) / 8}%`;
  const anchorStyle: CSSProperties = { top: 0, left };
  const pieces: Array<"q" | "r" | "b" | "n"> = ["q", "n", "r", "b"];
  return (
    <>
      <div className="settings-scrim" style={{ zIndex: 25 }} onClick={onCancel} />
      <div
        className="promo-popover"
        style={{ width: "12.5%", position: "absolute", zIndex: 26, ...anchorStyle }}
      >
        {pieces.map((p, i) => {
          const code = (color === "w" ? "w" : "b") + p.toUpperCase();
          return (
            <button
              key={p}
              className={`promo-piece ${i === 0 ? "promo-piece-active" : ""}`}
              onClick={() => onPick(p)}
              type="button"
              aria-label={`Promote to ${p.toUpperCase()}`}
            >
              <span className={`piece ${color === "w" ? "piece-w" : "piece-b"}`}>
                {PIECE_GLYPH[code]}
              </span>
            </button>
          );
        })}
      </div>
    </>
  );
}
