"use client";

import { useState } from "react";
import { BotAvatar, type Bot } from "./SidePanel";
import {
  IconCheck,
  IconChevronDown,
  IconShuffle,
} from "./Icons";

export type Color = "w" | "b" | "random";
export type TimeControl =
  | "unlimited"
  | "1+0"
  | "3+2"
  | "10+0"
  | "15+10"
  | "custom";

export function PlaySetup({
  opponent,
  setOpponent,
  color,
  setColor,
  timeControl,
  setTimeControl,
  hasResume = false,
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
  hasResume?: boolean;
  onStart: () => void;
  onResume?: () => void;
  onDiscard?: () => void;
}) {
  const [customOpen, setCustomOpen] = useState(timeControl === "custom");

  return (
    <div className="setup-panel">
      {hasResume && (
        <div className="resume-card">
          <div className="col gap-4">
            <span className="text-xs subtle mono">RESUME</span>
            <span className="text-sm">
              You have a game in progress vs <strong>Nomad</strong>
            </span>
            <span className="text-xs mono muted">14 moves · 3:42 left</span>
          </div>
          <div className="row gap-8">
            <button
              className="btn btn-primary btn-sm"
              onClick={onResume}
              type="button"
            >
              Resume
            </button>
            <button
              className="btn btn-ghost btn-sm"
              onClick={onDiscard}
              type="button"
            >
              Discard
            </button>
          </div>
        </div>
      )}

      <div className="setup-section">
        <h3 className="setup-label">Opponent</h3>
        <div className="opp-list">
          <OpponentTile
            bot="nomad"
            title="Nomad"
            tagline="Custom engine. Plays to win."
            selected={opponent === "nomad"}
            onClick={() => setOpponent("nomad")}
          />
          <OpponentTile
            bot="echo"
            title="Echo"
            tagline="Mimic of the developer. Experimental."
            selected={opponent === "echo"}
            onClick={() => setOpponent("echo")}
          />
        </div>
      </div>

      <div className="setup-section">
        <h3 className="setup-label">Color</h3>
        <div className="seg">
          {(
            [
              { id: "w", label: "White" },
              { id: "random", label: "Random" },
              { id: "b", label: "Black" },
            ] as const
          ).map((opt) => (
            <button
              key={opt.id}
              className={`seg-btn ${color === opt.id ? "seg-btn-on" : ""}`}
              onClick={() => setColor(opt.id)}
              type="button"
            >
              {opt.id === "random" && <IconShuffle size={14} />}
              {opt.id === "w" && <span className="seg-disc seg-disc-w" />}
              {opt.id === "b" && <span className="seg-disc seg-disc-b" />}
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="setup-section">
        <h3 className="setup-label">Time control</h3>
        <div className="chips">
          {(
            [
              { id: "unlimited", label: "Unlimited" },
              { id: "1+0", label: "1+0", sub: "Bullet" },
              { id: "3+2", label: "3+2", sub: "Blitz" },
              { id: "10+0", label: "10+0", sub: "Rapid" },
              { id: "15+10", label: "15+10", sub: "Classical" },
            ] as const
          ).map((tc) => (
            <button
              key={tc.id}
              className={`chip ${timeControl === tc.id ? "chip-on" : ""}`}
              onClick={() => setTimeControl(tc.id)}
              type="button"
            >
              <span className={tc.id === "unlimited" ? "" : "mono"}>
                {tc.label}
              </span>
              {"sub" in tc && tc.sub && (
                <span className="chip-sub text-xs subtle">{tc.sub}</span>
              )}
            </button>
          ))}
          <button
            className={`chip ${customOpen ? "chip-on" : ""}`}
            onClick={() => {
              setCustomOpen((v) => !v);
              if (!customOpen) setTimeControl("custom");
            }}
            type="button"
          >
            Custom{" "}
            <IconChevronDown
              size={14}
              style={{
                transform: customOpen ? "rotate(180deg)" : undefined,
                transition: "transform 150ms",
              }}
            />
          </button>
        </div>
        {customOpen && (
          <div className="custom-time">
            <label className="custom-time-input">
              <span className="text-xs subtle">Minutes</span>
              <input
                type="number"
                defaultValue={5}
                min={1}
                max={180}
                className="mono"
              />
            </label>
            <span className="custom-time-plus mono">+</span>
            <label className="custom-time-input">
              <span className="text-xs subtle">Increment</span>
              <input
                type="number"
                defaultValue={3}
                min={0}
                max={60}
                className="mono"
              />
            </label>
          </div>
        )}
      </div>

      <button
        className="btn btn-primary btn-lg btn-block setup-start"
        onClick={onStart}
        type="button"
      >
        Start game
      </button>

      <p className="text-xs subtle setup-foot mono">
        engine state stays on this device · no account
      </p>
    </div>
  );
}

function OpponentTile({
  bot,
  title,
  tagline,
  selected,
  onClick,
}: {
  bot: Bot;
  title: string;
  tagline: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      className={`opp-tile ${selected ? "opp-tile-on" : ""}`}
      onClick={onClick}
      type="button"
    >
      <BotAvatar bot={bot} size={44} />
      <div className="col gap-4" style={{ flex: 1, textAlign: "left" }}>
        <span className="text-md weight-500">{title}</span>
        <span className="text-xs muted">{tagline}</span>
      </div>
      <span className={`opp-radio ${selected ? "opp-radio-on" : ""}`}>
        {selected && <IconCheck size={14} />}
      </span>
    </button>
  );
}
