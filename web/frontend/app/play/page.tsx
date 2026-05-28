"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { TopNav } from "@/components/TopNav";
import {
  ActionRow,
  IdentityRow,
  MoveList,
  OpeningStrip,
  PanelFooter,
  SpeechBubble,
  type Bot,
} from "@/components/SidePanel";
import { DecorativeBoard, SETUP_FEN } from "@/components/DecorativeBoard";
import { GameBoard } from "@/components/GameBoard";
import { PlaySetup, type Color, type TimeControl } from "@/components/PlaySetup";
import { AboutModal, SettingsPopover } from "@/components/Modals";
import { GameEndModal } from "@/components/GameEndModal";
import { IconArrowRight } from "@/components/Icons";
import { formatClock, describeEnd, useGame } from "@/lib/game";
import { detectOpening } from "@/lib/openings";

const WELCOME_KEY = "seen_welcome";

function PlayPageInner() {
  const router = useRouter();
  const params = useSearchParams();

  // Setup-only state lives outside the game store — the store is empty until
  // Start game is clicked.
  const initialOpponent: Bot =
    params.get("opponent") === "echo" ? "echo" : "nomad";
  const [setupOpponent, setSetupOpponent] = useState<Bot>(initialOpponent);
  const [setupColor, setSetupColor] = useState<Color>("w");
  const [setupTc, setSetupTc] = useState<TimeControl>("unlimited");

  const status = useGame((s) => s.status);
  const opponent = useGame((s) => s.opponent);
  const playerColor = useGame((s) => s.playerColor);
  const timeControl = useGame((s) => s.timeControl);
  const customMinutes = useGame((s) => s.customMinutes);
  const customIncrement = useGame((s) => s.customIncrement);
  const moveList = useGame((s) => s.moveList);
  const history = useGame((s) => s.history);
  const fen = useGame((s) => s.fen);
  const result = useGame((s) => s.result);
  const endReason = useGame((s) => s.endReason);
  const whiteTimeMs = useGame((s) => s.whiteTimeMs);
  const blackTimeMs = useGame((s) => s.blackTimeMs);
  const lastBotMessage = useGame((s) => s.lastBotMessage);
  const botThinking = useGame((s) => s.botThinking);
  const error = useGame((s) => s.error);
  const scrubIndex = useGame((s) => s.scrubIndex);
  const startedAt = useGame((s) => s.startedAt);

  const startGame = useGame((s) => s.startGame);
  const resign = useGame((s) => s.resign);
  const takeback = useGame((s) => s.takeback);
  const newGame = useGame((s) => s.newGame);
  const rematch = useGame((s) => s.rematch);
  const requestHint = useGame((s) => s.requestHint);
  const scrubTo = useGame((s) => s.scrubTo);
  const tickClock = useGame((s) => s.tickClock);
  const discardSaved = useGame((s) => s.discardSaved);

  const [aboutOpen, setAboutOpen] = useState(false);
  const [welcomeOpen, setWelcomeOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [gameEndOpen, setGameEndOpen] = useState(false);

  // First-visit welcome modal.
  useEffect(() => {
    try {
      if (!localStorage.getItem(WELCOME_KEY)) setWelcomeOpen(true);
    } catch {}
  }, []);
  const dismissWelcome = () => {
    setWelcomeOpen(false);
    try {
      localStorage.setItem(WELCOME_KEY, "1");
    } catch {}
  };

  // Reveal the game-end modal whenever the store enters "ended".
  useEffect(() => {
    if (status === "ended") {
      const t = setTimeout(() => setGameEndOpen(true), 400);
      return () => clearTimeout(t);
    } else {
      setGameEndOpen(false);
    }
  }, [status]);

  // Clock tick — only schedules an interval when the game is timed.
  useEffect(() => {
    if (status !== "playing" || timeControl === "unlimited") return;
    const id = setInterval(() => tickClock(), 250);
    return () => clearInterval(id);
  }, [status, timeControl, tickClock]);

  // Arrow-key scrubbing through the move history. Skip when the user is
  // typing in an input/textarea/contenteditable element.
  useEffect(() => {
    if (status === "idle") return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      const target = e.target as HTMLElement | null;
      if (target) {
        const tag = target.tagName;
        if (
          tag === "INPUT" ||
          tag === "TEXTAREA" ||
          tag === "SELECT" ||
          target.isContentEditable
        ) {
          return;
        }
      }
      const total = history.length;
      if (total === 0) return;
      // currentPly: -1 = pre-first-move (initial fen), 0..total-1 = after that move
      const cur = scrubIndex === null ? total - 1 : scrubIndex;
      const target_ = e.key === "ArrowLeft" ? cur - 1 : cur + 1;
      if (target_ < -1 || target_ > total - 1) return;
      e.preventDefault();
      scrubTo(target_ === total - 1 ? null : target_);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [status, history.length, scrubIndex, scrubTo]);

  // Tab title — spec §17.
  useEffect(() => {
    const opName = opponent === "nomad" ? "Nomad" : "Echo";
    let title = "chess-room";
    if (status === "idle") title = `Chess vs ${setupOpponent === "nomad" ? "Nomad" : "Echo"}`;
    else if (status === "ended") title = "Game over";
    else if (botThinking) title = "⏳ Thinking…";
    else title = `● Your move · vs ${opName}`;
    document.title = title;
  }, [status, opponent, botThinking, setupOpponent]);

  const hasResume = status === "playing" || (status === "ended" && moveList.length > 0);

  const openingName = useMemo(
    () => detectOpening(moveList.map((m) => m.san)),
    [moveList],
  );

  const userClockMs = playerColor === "w" ? whiteTimeMs : blackTimeMs;
  const botClockMs = playerColor === "w" ? blackTimeMs : whiteTimeMs;
  const isTimed = timeControl !== "unlimited";
  const userClockLow = isTimed && userClockMs < 30_000;
  const botClockLow = isTimed && botClockMs < 30_000;

  // moveList ↔ ply indexing for MoveList highlighting / scrub.
  const moveListRows: Array<[string, string | undefined]> = useMemo(() => {
    const rows: Array<[string, string | undefined]> = [];
    for (let i = 0; i < moveList.length; i += 2) {
      rows.push([moveList[i].san, moveList[i + 1]?.san]);
    }
    return rows;
  }, [moveList]);

  // Game-end stats.
  const stats = useMemo(() => {
    let captures = 0;
    const replay = moveList.map((m) => m.san);
    for (const san of replay) {
      if (san.includes("x")) captures += 1;
    }
    const ms = startedAt ? Date.now() - startedAt : 0;
    const totalSeconds = Math.max(0, Math.floor(ms / 1000));
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    return {
      captures: captures.toString(),
      time: `${m}:${s.toString().padStart(2, "0")}`,
    };
  }, [moveList, startedAt]);

  const phase: "setup" | "game" = status === "idle" ? "setup" : "game";

  return (
    <>
      <TopNav onAbout={() => setAboutOpen(true)} />

      {phase === "setup" ? (
        <SetupView
          opponent={setupOpponent}
          setOpponent={setSetupOpponent}
          color={setupColor}
          setColor={setSetupColor}
          timeControl={setupTc}
          setTimeControl={setSetupTc}
          hasResume={hasResume}
          onStart={() =>
            startGame({
              opponent: setupOpponent,
              color: setupColor,
              timeControl: setupTc,
            })
          }
          onResume={() => {
            // Status is already "playing" — nothing to do; just hop into game view.
            if (status === "ended") {
              // Shouldn't happen normally; new game cleans the slate.
              newGame();
            }
          }}
          onDiscard={discardSaved}
        />
      ) : (
        <div className="play-page">
          <div className="play-board-col">
            <IdentityRow
              side="opponent"
              bot={opponent}
              rating={opponent === "nomad" ? "~2200" : "~1500"}
              clock={isTimed ? formatClock(botClockMs) : null}
              clockLow={botClockLow}
              thinking={botThinking}
              onClose={newGame}
            />
            <div style={{ position: "relative" }}>
              <GameBoard />
              {scrubIndex !== null && (
                <button
                  className="return-live mono text-xs"
                  onClick={() => scrubTo(null)}
                  type="button"
                >
                  <IconArrowRight size={14} /> return to live
                </button>
              )}
              {status === "ended" && gameEndOpen && (
                <GameEndModal
                  opponent={opponent}
                  result={describeEnd(result, endReason)}
                  moves={Math.ceil(moveList.length / 2)}
                  captures={stats.captures}
                  time={stats.time}
                  onRematch={() => rematch()}
                  onNewGame={newGame}
                  onReview={() => setGameEndOpen(false)}
                  onPgn={() => downloadPgn(moveList.map((m) => m.san), opponent, result)}
                />
              )}
            </div>
            <IdentityRow
              side="player"
              name="you"
              clock={isTimed ? formatClock(userClockMs) : null}
              clockLow={userClockLow}
            />
          </div>

          <aside className="side-panel">
            {lastBotMessage && (
              <SpeechBubble bot={opponent} text={lastBotMessage.text} />
            )}
            {openingName && <OpeningStrip name={openingName} />}
            <MoveList
              moves={moveListRows.length > 0 ? moveListRows : [["…", undefined]]}
              currentPly={scrubIndex}
              onScrub={(ply) => scrubTo(ply === moveList.length - 1 ? null : ply)}
            />
            <ActionRow
              disabled={botThinking || status !== "playing"}
              onResign={resign}
              onTakeback={takeback}
              onHint={requestHint}
            />
            <PanelFooter onSettings={() => setSettingsOpen(true)} />
            {error && (
              <div
                className="text-xs mono"
                style={{ color: "var(--danger)", padding: "0 16px 12px" }}
              >
                {error}
              </div>
            )}
          </aside>
        </div>
      )}

      {settingsOpen && <SettingsPopover onClose={() => setSettingsOpen(false)} />}
      {welcomeOpen && <AboutModal variant="welcome" onClose={dismissWelcome} />}
      {aboutOpen && !welcomeOpen && (
        <AboutModal variant="about" onClose={() => setAboutOpen(false)} />
      )}
    </>
  );
}

function SetupView({
  opponent,
  setOpponent,
  color,
  setColor,
  timeControl,
  setTimeControl,
  hasResume,
  onStart,
  onResume,
  onDiscard,
}: {
  opponent: Bot;
  setOpponent: (b: Bot) => void;
  color: Color;
  setColor: (c: Color) => void;
  timeControl: TimeControl;
  setTimeControl: (t: TimeControl) => void;
  hasResume: boolean;
  onStart: () => void;
  onResume?: () => void;
  onDiscard?: () => void;
}) {
  return (
    <div className="play-page">
      <div className="play-board-col">
        <IdentityRow side="opponent" bot={opponent} rating={opponent === "nomad" ? "~2200" : "~1500"} />
        <div className="board-wrap">
          <DecorativeBoard fen={SETUP_FEN} dimmed />
        </div>
        <IdentityRow side="player" name="you" />
      </div>
      <PlaySetup
        opponent={opponent}
        setOpponent={setOpponent}
        color={color}
        setColor={setColor}
        timeControl={timeControl}
        setTimeControl={setTimeControl}
        hasResume={hasResume}
        onStart={onStart}
        onResume={onResume}
        onDiscard={onDiscard}
      />
    </div>
  );
}

function downloadPgn(
  sanMoves: string[],
  opponent: Bot,
  result: "user" | "bot" | "draw" | null,
) {
  const pgnResult =
    result === "draw" ? "1/2-1/2" : result === "user" ? "1-0" : result === "bot" ? "0-1" : "*";
  const pairs: string[] = [];
  for (let i = 0; i < sanMoves.length; i += 2) {
    const num = i / 2 + 1;
    const w = sanMoves[i];
    const b = sanMoves[i + 1];
    pairs.push(b ? `${num}. ${w} ${b}` : `${num}. ${w}`);
  }
  const headers = [
    '[Event "chess-room"]',
    `[White "${opponent === "nomad" ? "Nomad" : "Echo"}"]`,
    `[Black "you"]`,
    `[Result "${pgnResult}"]`,
  ].join("\n");
  const body = pairs.join(" ") + " " + pgnResult;
  const pgn = `${headers}\n\n${body}\n`;
  const blob = new Blob([pgn], { type: "application/x-chess-pgn" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `chess-room-${Date.now()}.pgn`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function PlayPage() {
  return (
    <Suspense fallback={null}>
      <PlayPageInner />
    </Suspense>
  );
}
