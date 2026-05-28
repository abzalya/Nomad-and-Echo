"use client";

import {
  IconBook,
  IconCompass,
  IconDownload,
  IconFlag,
  IconLightbulb,
  IconSettings,
  IconUndo2,
  IconX,
} from "./Icons";

export type Bot = "nomad" | "echo";

export function BotAvatar({
  bot = "nomad",
  size = 32,
  thinking = false,
}: {
  bot?: Bot;
  size?: number;
  thinking?: boolean;
}) {
  const isNomad = bot === "nomad";
  return (
    <span
      className={`bot-avatar ${isNomad ? "bot-nomad" : "bot-echo"} ${
        thinking ? "bot-thinking" : ""
      }`}
      style={{ width: size, height: size, fontSize: size * 0.5 }}
    >
      <span className="mono">{isNomad ? "N" : "E"}</span>
    </span>
  );
}

export function IdentityRow({
  side = "opponent",
  bot = "nomad",
  name,
  rating,
  clock,
  clockLow = false,
  thinking = false,
  onClose,
}: {
  side?: "opponent" | "player";
  bot?: Bot;
  name?: string;
  rating?: string;
  clock?: string | null;
  clockLow?: boolean;
  thinking?: boolean;
  onClose?: () => void;
}) {
  const isOpponent = side === "opponent";
  const displayName =
    name ?? (isOpponent ? (bot === "nomad" ? "Nomad" : "Echo") : "You");
  return (
    <div className="identity-row">
      <div className="row gap-12" style={{ alignItems: "center" }}>
        {isOpponent ? (
          <BotAvatar bot={bot} size={36} thinking={thinking} />
        ) : (
          <span className="player-avatar mono">Y</span>
        )}
        <div className="col gap-4">
          <div className="row gap-8" style={{ alignItems: "baseline" }}>
            <span className="weight-500 text-md">{displayName}</span>
            {rating && <span className="mono text-xs muted">{rating}</span>}
          </div>
          {isOpponent && (
            <div className="row gap-8 text-xs muted">
              <span className={`pip ${thinking ? "thinking" : ""}`} />
              <span>{thinking ? "thinking…" : "engine ready"}</span>
            </div>
          )}
          {!isOpponent && <div className="text-xs subtle">anonymous</div>}
        </div>
      </div>
      <div className="row gap-12" style={{ alignItems: "center" }}>
        {clock && (
          <span className={`clock mono ${clockLow ? "clock-low" : ""}`}>
            {clock}
          </span>
        )}
        {isOpponent && onClose && (
          <button
            className="btn-icon"
            aria-label="Abandon game"
            onClick={onClose}
            type="button"
          >
            <IconX size={18} />
          </button>
        )}
        {!isOpponent && (
          <button
            className="btn-icon"
            aria-label="Set display name"
            type="button"
          >
            <IconFlag size={18} />
          </button>
        )}
      </div>
    </div>
  );
}

export function SpeechBubble({
  bot = "nomad",
  text,
}: {
  bot?: Bot;
  text: string;
}) {
  return (
    <div className={`speech ${bot === "nomad" ? "speech-nomad" : "speech-echo"}`}>
      <span className="speech-tail" aria-hidden="true" />
      <span className="text-sm">{text}</span>
    </div>
  );
}

export function OpeningStrip({ name = "Caro–Kann Defense" }: { name?: string }) {
  return (
    <div className="opening-strip">
      <span className="mono text-xs">{name}</span>
      <span className="row gap-8 subtle">
        <IconBook size={14} />
        <IconCompass size={14} />
      </span>
    </div>
  );
}

export const SAMPLE_MOVES: Array<[string, string | undefined]> = [
  ["e4", "c6"],
  ["d4", "d5"],
  ["Nc3", "dxe4"],
  ["Nxe4", "Bf5"],
  ["Ng3", "Bg6"],
  ["h4", "h6"],
  ["Nf3", "Nd7"],
  ["h5", "Bh7"],
  ["Bd3", "Bxd3"],
  ["Qxd3", "Ngf6"],
  ["Bd2", "e6"],
  ["O-O-O", "Be7"],
  ["Ne4", "Nxe4"],
];

export function MoveList({
  moves = SAMPLE_MOVES,
  currentPly = null,
  onScrub,
}: {
  moves?: Array<[string, string | undefined]>;
  currentPly?: number | null;
  onScrub?: (ply: number) => void;
}) {
  const totalPlies = moves.flat().filter(Boolean).length;
  const activePly = currentPly == null ? totalPlies - 1 : currentPly;
  return (
    <div className="move-list scroll">
      <table className="move-table">
        <tbody>
          {moves.map(([w, b], i) => {
            const wPly = i * 2;
            const bPly = i * 2 + 1;
            return (
              <tr key={i}>
                <td className="move-num mono">{i + 1}.</td>
                <td
                  className={`move-cell mono ${
                    activePly === wPly ? "move-active" : ""
                  }`}
                  onClick={() => onScrub?.(wPly)}
                >
                  {w}
                </td>
                <td
                  className={`move-cell mono ${
                    activePly === bPly ? "move-active" : ""
                  }`}
                  onClick={() => b && onScrub?.(bPly)}
                >
                  {b ?? ""}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export function ActionRow({
  disabled = false,
  onResign,
  onTakeback,
  onHint,
}: {
  disabled?: boolean;
  onResign?: () => void;
  onTakeback?: () => void;
  onHint?: () => void;
}) {
  return (
    <div className="action-row">
      <button
        className="action-btn"
        disabled={disabled}
        onClick={onResign}
        type="button"
      >
        <IconFlag size={20} />
        <span className="text-xs">Resign</span>
      </button>
      <button
        className="action-btn"
        disabled={disabled}
        onClick={onTakeback}
        type="button"
      >
        <IconUndo2 size={20} />
        <span className="text-xs">Takeback</span>
      </button>
      <button
        className="action-btn"
        disabled={disabled}
        onClick={onHint}
        type="button"
      >
        <IconLightbulb size={20} />
        <span className="text-xs">Hint</span>
      </button>
    </div>
  );
}

export function PanelFooter({ onSettings }: { onSettings?: () => void }) {
  return (
    <div className="panel-footer">
      <button className="btn-icon" aria-label="Export PGN" type="button">
        <IconDownload size={18} />
      </button>
      <button
        className="btn-icon"
        aria-label="Settings"
        onClick={onSettings}
        type="button"
      >
        <IconSettings size={18} />
      </button>
    </div>
  );
}

export const SAMPLE_SPEECH: Record<Bot, Record<string, string>> = {
  nomad: {
    start: "Calculated. Begin.",
    "check-given": "Predictable.",
    "check-received": "Acceptable.",
    "big-capture": "A reasonable trade.",
    win: "Outcome confirmed.",
    loss: "Recalibrating.",
    draw: "Insufficient force.",
  },
  echo: {
    start: "Felt natural to open like this.",
    "check-given": "That's something I'd play.",
    "check-received": "Yeah, you got me.",
    "big-capture": "You'd probably play that too.",
    win: "Familiar shape.",
    loss: "Hm. Off-style.",
    draw: "Reasonable outcome.",
  },
};
