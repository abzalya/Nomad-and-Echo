"use client";

import { Chess, type Move, type Square } from "chess.js";
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { api } from "./api";
import { pickQuip } from "./quips";
import type { Bot } from "@/components/SidePanel";

export type PlayerColor = "w" | "b";
export type GameStatus = "idle" | "playing" | "ended";
export type EndReason =
  | "checkmate"
  | "stalemate"
  | "threefold"
  | "fifty-move"
  | "insufficient"
  | "timeout"
  | "resign";

export type TimeControl =
  | "unlimited"
  | "1+0"
  | "3+2"
  | "10+0"
  | "15+10"
  | "custom";

export type SpeechTrigger =
  | "start"
  | "check-given"
  | "check-received"
  | "big-capture"
  | "win"
  | "loss"
  | "draw";

export type MoveEntry = { uci: string; san: string };

type GameState = {
  initialFen: string;
  fen: string;
  history: string[]; // UCI moves applied on top of initialFen
  moveList: MoveEntry[];
  status: GameStatus;
  result: "user" | "bot" | "draw" | null;
  endReason: EndReason | null;

  opponent: Bot;
  playerColor: PlayerColor;
  timeControl: TimeControl;
  customMinutes: number;
  customIncrement: number;
  whiteTimeMs: number;
  blackTimeMs: number;
  lastTickAt: number | null;

  selectedSquare: Square | null;
  scrubIndex: number | null;

  lastBotMessage: { trigger: SpeechTrigger; text: string } | null;
  hintHighlight: { from: string; to: string } | null;
  pendingPromotion: { from: Square; to: Square } | null;

  botThinking: boolean;
  error: string | null;
  startedAt: number | null;
};

type GameActions = {
  startGame: (opts: {
    opponent: Bot;
    color: PlayerColor | "random";
    timeControl: TimeControl;
    customMinutes?: number;
    customIncrement?: number;
  }) => Promise<void>;
  selectSquare: (sq: Square | null) => void;
  userMove: (from: Square, to: Square, promotion?: "q" | "r" | "b" | "n") => boolean;
  applyPendingPromotion: (piece: "q" | "r" | "b" | "n") => void;
  cancelPromotion: () => void;
  takeback: () => void;
  resign: () => void;
  newGame: () => void;
  rematch: () => Promise<void>;
  requestHint: () => Promise<void>;
  scrubTo: (ply: number | null) => void;
  tickClock: () => void;
  discardSaved: () => void;
};

export type GameSnapshot = GameState & GameActions;

const presetMs: Record<TimeControl, { base: number; inc: number } | null> = {
  unlimited: null,
  "1+0": { base: 60_000, inc: 0 },
  "3+2": { base: 180_000, inc: 2_000 },
  "10+0": { base: 600_000, inc: 0 },
  "15+10": { base: 900_000, inc: 10_000 },
  custom: null,
};

function tcMs(
  tc: TimeControl,
  customMinutes: number,
  customIncrement: number,
): { base: number; inc: number } | null {
  if (tc === "unlimited") return null;
  if (tc === "custom") {
    return { base: customMinutes * 60_000, inc: customIncrement * 1_000 };
  }
  return presetMs[tc];
}

// Builds a { trigger, text } entry — or null if the catalog has no line for
// this trigger (e.g. `start` is intentionally empty).
function makeQuip(
  bot: Bot,
  trigger: SpeechTrigger,
): { trigger: SpeechTrigger; text: string } | null {
  const text = pickQuip(bot, trigger);
  return text ? { trigger, text } : null;
}

const PIECE_VALUE: Record<string, number> = {
  p: 1,
  n: 3,
  b: 3,
  r: 5,
  q: 9,
};

function isBigCapture(move: Move): boolean {
  if (!move.captured) return false;
  return (PIECE_VALUE[move.captured] ?? 0) >= 3;
}

function resolveColor(c: PlayerColor | "random"): PlayerColor {
  if (c === "random") return Math.random() < 0.5 ? "w" : "b";
  return c;
}

function terminalState(chess: Chess): { reason: EndReason; result: "user" | "bot" | "draw" } | null {
  if (chess.isCheckmate()) {
    return { reason: "checkmate", result: "user" };
  }
  if (chess.isStalemate()) return { reason: "stalemate", result: "draw" };
  if (chess.isThreefoldRepetition()) return { reason: "threefold", result: "draw" };
  if (chess.isInsufficientMaterial()) return { reason: "insufficient", result: "draw" };
  if (chess.isDraw()) return { reason: "fifty-move", result: "draw" };
  return null;
}

const INITIAL_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function initial(): GameState {
  return {
    initialFen: INITIAL_FEN,
    fen: INITIAL_FEN,
    history: [],
    moveList: [],
    status: "idle",
    result: null,
    endReason: null,
    opponent: "nomad",
    playerColor: "w",
    timeControl: "unlimited",
    customMinutes: 5,
    customIncrement: 3,
    whiteTimeMs: 0,
    blackTimeMs: 0,
    lastTickAt: null,
    selectedSquare: null,
    scrubIndex: null,
    lastBotMessage: null,
    hintHighlight: null,
    pendingPromotion: null,
    botThinking: false,
    error: null,
    startedAt: null,
  };
}

export const useGame = create<GameSnapshot>()(
  persist(
    (set, get) => {
      // Apply the bot's move from the gateway response onto current state.
      async function requestBotMove() {
        const st = get();
        if (st.status !== "playing") return;
        const chess = new Chess(st.fen);
        if (chess.turn() === st.playerColor) return;
        set({ botThinking: true, error: null });
        try {
          // Engine reconstructs the board from `fen` then replays `history`.
          // Send the starting fen + full history so e.g. e2e4 stays legal on
          // turn 1 of a fresh game (sending current-fen would mean replaying
          // already-applied moves).
          const res = await api.botMove({
            fen: st.initialFen,
            history: st.history,
            opponent: st.opponent,
            think_ms: st.timeControl === "unlimited" ? undefined : 1500,
          });
          // Re-read state — user may have abandoned while we were waiting.
          const cur = get();
          if (cur.status !== "playing") return;
          const board = new Chess(cur.fen);
          const move = board.move({
            from: res.uci.slice(0, 2),
            to: res.uci.slice(2, 4),
            promotion: res.uci.length === 5 ? (res.uci[4] as "q" | "r" | "b" | "n") : undefined,
          });
          if (!move) {
            set({
              botThinking: false,
              error: "Engine returned an illegal move.",
              status: "ended",
              result: "user",
              endReason: "resign",
            });
            return;
          }
          const inc = tcMs(cur.timeControl, cur.customMinutes, cur.customIncrement)?.inc ?? 0;
          // Bot just moved → add increment to bot's clock (the side that moved).
          const botColor: PlayerColor = cur.playerColor === "w" ? "b" : "w";
          const whiteTimeMs =
            cur.timeControl === "unlimited"
              ? cur.whiteTimeMs
              : botColor === "w"
              ? cur.whiteTimeMs + inc
              : cur.whiteTimeMs;
          const blackTimeMs =
            cur.timeControl === "unlimited"
              ? cur.blackTimeMs
              : botColor === "b"
              ? cur.blackTimeMs + inc
              : cur.blackTimeMs;

          const term = terminalState(board);
          let result: GameState["result"] = null;
          let endReason: EndReason | null = null;
          let status: GameStatus = "playing";
          // Quips live for at most one move — default to null and overwrite
          // only when this move's trigger has a line.
          let speech: GameState["lastBotMessage"] = null;

          if (term) {
            status = "ended";
            // Checkmate by bot means user lost.
            result = term.reason === "checkmate" ? "bot" : term.result;
            endReason = term.reason;
            const trig: SpeechTrigger =
              result === "bot" ? "win" : result === "user" ? "loss" : "draw";
            speech = makeQuip(cur.opponent, trig);
          } else if (board.inCheck()) {
            speech = makeQuip(cur.opponent, "check-given");
          } else if (isBigCapture(move)) {
            speech = makeQuip(cur.opponent, "big-capture");
          }

          set({
            fen: board.fen(),
            history: [...cur.history, res.uci],
            moveList: [...cur.moveList, { uci: res.uci, san: move.san }],
            botThinking: false,
            whiteTimeMs,
            blackTimeMs,
            lastTickAt: Date.now(),
            status,
            result,
            endReason,
            lastBotMessage: speech,
          });
        } catch (err) {
          set({
            botThinking: false,
            error: err instanceof Error ? err.message : String(err),
          });
        }
      }

      return {
        ...initial(),

        async startGame({ opponent, color, timeControl, customMinutes, customIncrement }) {
          const playerColor = resolveColor(color);
          const cm = customMinutes ?? get().customMinutes;
          const cinc = customIncrement ?? get().customIncrement;
          const tc = tcMs(timeControl, cm, cinc);
          const baseMs = tc?.base ?? 0;
          set({
            ...initial(),
            opponent,
            playerColor,
            timeControl,
            customMinutes: cm,
            customIncrement: cinc,
            whiteTimeMs: baseMs,
            blackTimeMs: baseMs,
            status: "playing",
            lastTickAt: Date.now(),
            startedAt: Date.now(),
            lastBotMessage: null,
          });
          // If user is black, bot moves first.
          if (playerColor === "b") {
            await requestBotMove();
          }
        },

        selectSquare(sq) {
          set({ selectedSquare: sq });
        },

        userMove(from, to, promotion) {
          const st = get();
          if (st.status !== "playing") return false;
          if (st.scrubIndex !== null) return false;
          const chess = new Chess(st.fen);
          if (chess.turn() !== st.playerColor) return false;

          // Promotion check: if pawn reaching last rank, defer until user picks piece.
          if (!promotion) {
            const piece = chess.get(from);
            if (
              piece &&
              piece.type === "p" &&
              ((piece.color === "w" && to[1] === "8") ||
                (piece.color === "b" && to[1] === "1"))
            ) {
              // Verify the move is otherwise legal before opening the popover.
              const legalMoves = chess.moves({ square: from, verbose: true });
              if (!legalMoves.some((m: Move) => m.to === to)) return false;
              set({ pendingPromotion: { from, to }, selectedSquare: null });
              return false;
            }
          }

          let move: Move | null;
          try {
            move = chess.move({ from, to, promotion });
          } catch {
            return false;
          }
          if (!move) return false;

          const inc = tcMs(st.timeControl, st.customMinutes, st.customIncrement)?.inc ?? 0;
          const whiteTimeMs =
            st.timeControl === "unlimited"
              ? st.whiteTimeMs
              : st.playerColor === "w"
              ? st.whiteTimeMs + inc
              : st.whiteTimeMs;
          const blackTimeMs =
            st.timeControl === "unlimited"
              ? st.blackTimeMs
              : st.playerColor === "b"
              ? st.blackTimeMs + inc
              : st.blackTimeMs;

          const uci = move.from + move.to + (move.promotion ?? "");
          const term = terminalState(chess);
          let result: GameState["result"] = null;
          let endReason: EndReason | null = null;
          let status: GameStatus = "playing";
          // Same one-move lifecycle as the bot side — clear unless a trigger
          // on this move says otherwise.
          let speech: GameState["lastBotMessage"] = null;

          if (term) {
            status = "ended";
            result = term.reason === "checkmate" ? "user" : term.result;
            endReason = term.reason;
            const trig: SpeechTrigger =
              result === "user" ? "loss" : result === "bot" ? "win" : "draw";
            speech = makeQuip(st.opponent, trig);
          } else if (chess.inCheck()) {
            speech = makeQuip(st.opponent, "check-received");
          }

          set({
            fen: chess.fen(),
            history: [...st.history, uci],
            moveList: [...st.moveList, { uci, san: move.san }],
            selectedSquare: null,
            pendingPromotion: null,
            hintHighlight: null,
            whiteTimeMs,
            blackTimeMs,
            lastTickAt: Date.now(),
            status,
            result,
            endReason,
            lastBotMessage: speech,
          });

          if (status === "playing") {
            requestBotMove();
          }
          return true;
        },

        applyPendingPromotion(piece) {
          const st = get();
          if (!st.pendingPromotion) return;
          const { from, to } = st.pendingPromotion;
          get().userMove(from, to, piece);
        },

        cancelPromotion() {
          set({ pendingPromotion: null });
        },

        takeback() {
          const st = get();
          if (st.status !== "playing" || st.botThinking) return;
          const replay = new Chess(st.initialFen);
          // Drop the last two plies (user + bot) when possible; if user is on
          // move and only one ply exists (i.e. bot moved first because user is
          // black), drop just that one.
          const dropCount = st.history.length >= 2 ? 2 : st.history.length;
          if (dropCount === 0) return;
          const newHistory = st.history.slice(0, st.history.length - dropCount);
          const newMoveList = st.moveList.slice(0, st.moveList.length - dropCount);
          for (const uci of newHistory) {
            replay.move({
              from: uci.slice(0, 2),
              to: uci.slice(2, 4),
              promotion: uci.length === 5 ? (uci[4] as "q" | "r" | "b" | "n") : undefined,
            });
          }
          set({
            fen: replay.fen(),
            history: newHistory,
            moveList: newMoveList,
            selectedSquare: null,
            pendingPromotion: null,
            scrubIndex: null,
            lastBotMessage: null,
          });
        },

        resign() {
          const st = get();
          if (st.status !== "playing") return;
          set({
            status: "ended",
            result: "bot",
            endReason: "resign",
            lastBotMessage: makeQuip(st.opponent, "win"),
          });
        },

        newGame() {
          set({ ...initial(), status: "idle" });
        },

        async rematch() {
          const st = get();
          await get().startGame({
            opponent: st.opponent,
            color: st.playerColor === "w" ? "b" : "w",
            timeControl: st.timeControl,
            customMinutes: st.customMinutes,
            customIncrement: st.customIncrement,
          });
        },

        async requestHint() {
          const st = get();
          if (st.status !== "playing" || st.botThinking) return;
          const chess = new Chess(st.fen);
          if (chess.turn() !== st.playerColor) return;
          try {
            const res = await api.hint({
              fen: st.initialFen,
              history: st.history,
            });
            const from = res.uci.slice(0, 2);
            const to = res.uci.slice(2, 4);
            set({ hintHighlight: { from, to } });
            setTimeout(() => {
              const cur = get();
              if (
                cur.hintHighlight?.from === from &&
                cur.hintHighlight?.to === to
              ) {
                set({ hintHighlight: null });
              }
            }, 2000);
          } catch (err) {
            set({ error: err instanceof Error ? err.message : String(err) });
          }
        },

        scrubTo(ply) {
          set({ scrubIndex: ply });
        },

        tickClock() {
          const st = get();
          if (st.status !== "playing") return;
          if (st.timeControl === "unlimited") return;
          if (st.lastTickAt === null) return;
          const chess = new Chess(st.fen);
          const now = Date.now();
          const delta = now - st.lastTickAt;
          const turn = chess.turn();
          const whiteTimeMs =
            turn === "w" ? Math.max(0, st.whiteTimeMs - delta) : st.whiteTimeMs;
          const blackTimeMs =
            turn === "b" ? Math.max(0, st.blackTimeMs - delta) : st.blackTimeMs;
          if (whiteTimeMs <= 0 || blackTimeMs <= 0) {
            const userTimedOut =
              (st.playerColor === "w" && whiteTimeMs <= 0) ||
              (st.playerColor === "b" && blackTimeMs <= 0);
            set({
              whiteTimeMs,
              blackTimeMs,
              lastTickAt: now,
              status: "ended",
              result: userTimedOut ? "bot" : "user",
              endReason: "timeout",
              lastBotMessage: makeQuip(st.opponent, userTimedOut ? "win" : "loss"),
            });
            return;
          }
          set({ whiteTimeMs, blackTimeMs, lastTickAt: now });
        },

        discardSaved() {
          set({ ...initial(), status: "idle" });
        },
      };
    },
    {
      name: "chess-room:game",
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({
        initialFen: s.initialFen,
        fen: s.fen,
        history: s.history,
        moveList: s.moveList,
        status: s.status,
        result: s.result,
        endReason: s.endReason,
        opponent: s.opponent,
        playerColor: s.playerColor,
        timeControl: s.timeControl,
        customMinutes: s.customMinutes,
        customIncrement: s.customIncrement,
        whiteTimeMs: s.whiteTimeMs,
        blackTimeMs: s.blackTimeMs,
        startedAt: s.startedAt,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          if (!state.initialFen) state.initialFen = INITIAL_FEN;
          state.lastTickAt = Date.now();
          state.botThinking = false;
          state.error = null;
          state.hintHighlight = null;
          state.pendingPromotion = null;
          state.scrubIndex = null;
          state.selectedSquare = null;
        }
      },
    },
  ),
);

export function formatClock(ms: number): string {
  if (ms <= 0) return "0:00";
  const total = Math.ceil(ms / 1000);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

export function legalMovesFrom(fen: string, square: Square): Move[] {
  const chess = new Chess(fen);
  return chess.moves({ square, verbose: true });
}

export function pieceAt(fen: string, square: Square) {
  return new Chess(fen).get(square);
}

export function isInCheck(fen: string): boolean {
  return new Chess(fen).inCheck();
}

export function checkedKingSquare(fen: string): Square | null {
  const chess = new Chess(fen);
  if (!chess.inCheck()) return null;
  const turn = chess.turn();
  const board = chess.board();
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      const cell = board[r][c];
      if (cell && cell.type === "k" && cell.color === turn) {
        return cell.square;
      }
    }
  }
  return null;
}

export function lastMoveSquares(history: string[]): { from: Square; to: Square } | null {
  if (history.length === 0) return null;
  const uci = history[history.length - 1];
  return {
    from: uci.slice(0, 2) as Square,
    to: uci.slice(2, 4) as Square,
  };
}

export function describeEnd(
  result: "user" | "bot" | "draw" | null,
  reason: EndReason | null,
): string {
  if (!result || !reason) return "";
  if (reason === "checkmate") {
    return result === "user" ? "Checkmate. You win." : "Checkmate. You lost.";
  }
  if (reason === "stalemate") return "Draw — stalemate.";
  if (reason === "threefold") return "Draw — threefold repetition.";
  if (reason === "fifty-move") return "Draw — 50-move rule.";
  if (reason === "insufficient") return "Draw — insufficient material.";
  if (reason === "timeout") {
    return result === "user" ? "You win on time." : "You lost on time.";
  }
  if (reason === "resign") {
    return result === "user" ? "Bot resigned." : "You resigned.";
  }
  return "";
}
