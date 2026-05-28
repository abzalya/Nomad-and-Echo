"use client";

import { useState, type ReactNode } from "react";
import {
  IconArrowUpRight,
  IconChevronRight,
  IconX,
} from "./Icons";
import { useSettings } from "@/lib/settings";

export function AboutModal({
  variant = "about",
  onClose,
}: {
  variant?: "about" | "welcome";
  onClose: () => void;
}) {
  const isWelcome = variant === "welcome";
  const [expanded, setExpanded] = useState({
    intro: true,
    nomad: false,
    echo: false,
    dev: false,
    tech: false,
  });
  const toggle = (k: keyof typeof expanded) =>
    setExpanded((p) => ({ ...p, [k]: !p[k] }));

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div className="wordmark wordmark-sm">
            chess<span className="accent">-room</span>
          </div>
          <button
            className="btn-icon"
            aria-label="Close"
            onClick={onClose}
            type="button"
          >
            <IconX size={18} />
          </button>
        </div>

        <div className="modal-body scroll">
          {isWelcome ? (
            <WelcomeContent onClose={onClose} />
          ) : (
            <>
              <AccordionSection
                title="Intro"
                open={expanded.intro}
                onToggle={() => toggle("intro")}
              >
                <p className="text-base muted">
                  <strong>chess-room</strong> is a portfolio project: a Next.js
                  front-end for a chess engine the developer wrote from scratch
                  in Python. You can play it against the engine itself
                  (<em>Nomad</em>) or against a mimic bot trained on the
                  developer&apos;s own games (<em>Echo</em>).
                </p>
              </AccordionSection>
              <AccordionSection
                title="About Nomad"
                open={expanded.nomad}
                onToggle={() => toggle("nomad")}
              >
                <p className="text-base muted">
                  Hand-rolled in Python. No libraries doing the chess work —
                  only the glue. Plays at default strength in v1.
                </p>
                <div className="tech-list mono text-xs subtle">
                  bitboards · alpha-beta · transposition table · null-move
                  pruning · LMR · aspiration windows · ray-attack pinning ·
                  pawn structure hash
                </div>
                <a className="modal-link mono text-xs" href="#">
                  github.com/dev/nomad <IconArrowUpRight size={12} />
                </a>
              </AccordionSection>
              <AccordionSection
                title="About Echo"
                open={expanded.echo}
                onToggle={() => toggle("echo")}
              >
                <p className="text-base muted">
                  Echo is an experiment: a smaller model trained on the
                  developer&apos;s own games. The goal is a bot that plays in
                  their style, weak openings and all.
                </p>
                <p className="text-xs subtle">
                  Echo is experimental — strength and style will vary as it
                  improves.
                </p>
              </AccordionSection>
              <AccordionSection
                title="About the developer"
                open={expanded.dev}
                onToggle={() => toggle("dev")}
              >
                <p className="text-base muted">
                  Engineer, occasional chess player. This site exists to show
                  the engine in action.
                </p>
                <div className="modal-links">
                  <a className="modal-link mono text-xs" href="#">
                    github <IconArrowUpRight size={12} />
                  </a>
                  <a className="modal-link mono text-xs" href="#">
                    linkedin <IconArrowUpRight size={12} />
                  </a>
                  <a className="modal-link mono text-xs" href="#">
                    email <IconArrowUpRight size={12} />
                  </a>
                </div>
              </AccordionSection>
              <AccordionSection
                title="Tech stack"
                open={expanded.tech}
                onToggle={() => toggle("tech")}
              >
                <div className="tech-list mono text-xs subtle">
                  next.js · fastapi · python · react-chessboard · chess.js ·
                  tailwind · zustand
                </div>
              </AccordionSection>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function WelcomeContent({ onClose }: { onClose: () => void }) {
  return (
    <div className="welcome-content">
      <div className="welcome-eyebrow mono text-xs subtle">FIRST VISIT</div>
      <h2 className="text-xl weight-700">Welcome.</h2>
      <p className="text-md muted">
        Play chess against a custom engine (
        <strong className="weight-500">Nomad</strong>), or against a mimic of
        its developer (<strong className="weight-500">Echo</strong>). No
        account, no history, no tracking — just a board.
      </p>
      <ul className="welcome-list text-base muted">
        <li>
          <span className="mono accent">·</span> Your game saves on this device
          — refresh keeps your position.
        </li>
        <li>
          <span className="mono accent">·</span> Resign, take back, or ask for
          a hint at any time.
        </li>
        <li>
          <span className="mono accent">·</span> Hints always come from the
          engine. Echo gives bad hints by design.
        </li>
      </ul>
      <div className="welcome-cta">
        <button
          className="btn btn-primary btn-lg"
          onClick={onClose}
          type="button"
        >
          Got it, let&apos;s play
        </button>
      </div>
    </div>
  );
}

function AccordionSection({
  title,
  open,
  onToggle,
  children,
}: {
  title: string;
  open: boolean;
  onToggle: () => void;
  children: ReactNode;
}) {
  return (
    <section className={`acc-section ${open ? "acc-open" : ""}`}>
      <button className="acc-head" onClick={onToggle} type="button">
        <span className="text-lg weight-500">{title}</span>
        <IconChevronRight
          size={18}
          style={{
            transform: open ? "rotate(90deg)" : undefined,
            transition: "transform 240ms cubic-bezier(.2,.8,.2,1)",
          }}
        />
      </button>
      {open && <div className="acc-body">{children}</div>}
    </section>
  );
}

export function SettingsPopover({ onClose }: { onClose: () => void }) {
  const boardTheme = useSettings((s) => s.boardTheme);
  const pieceSet = useSettings((s) => s.pieceSet);
  const sound = useSettings((s) => s.sound);
  const showDots = useSettings((s) => s.showDots);
  const showCoords = useSettings((s) => s.showCoords);
  const autoPromoteQueen = useSettings((s) => s.autoPromoteQueen);
  const set = useSettings((s) => s.set);

  return (
    <>
      <div className="settings-scrim" onClick={onClose} />
      <div className="settings-popover">
        <div className="settings-head">
          <span className="text-sm weight-500">Settings</span>
          <button
            className="btn-icon"
            onClick={onClose}
            aria-label="Close"
            type="button"
          >
            <IconX size={16} />
          </button>
        </div>
        <SettingRow label="Board theme">
          <select
            className="settings-select mono text-xs"
            value={boardTheme}
            onChange={(e) =>
              set("boardTheme", e.target.value as typeof boardTheme)
            }
          >
            <option value="walnut">walnut</option>
            <option value="parchment">parchment</option>
            <option value="steel">steel</option>
          </select>
        </SettingRow>
        <SettingRow label="Piece set">
          <select
            className="settings-select mono text-xs"
            value={pieceSet}
            onChange={(e) =>
              set("pieceSet", e.target.value as typeof pieceSet)
            }
          >
            <option value="cburnett">cburnett</option>
            <option value="merida">merida</option>
          </select>
        </SettingRow>
        <SettingToggle
          label="Sound"
          value={sound}
          onChange={(v) => set("sound", v)}
        />
        <SettingToggle
          label="Show legal move dots"
          value={showDots}
          onChange={(v) => set("showDots", v)}
        />
        <SettingToggle
          label="Show coordinates"
          value={showCoords}
          onChange={(v) => set("showCoords", v)}
        />
        <SettingToggle
          label="Auto-promote to Queen"
          value={autoPromoteQueen}
          onChange={(v) => set("autoPromoteQueen", v)}
        />
      </div>
    </>
  );
}

function SettingRow({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="setting-row">
      <span className="text-sm">{label}</span>
      {children}
    </div>
  );
}

function SettingToggle({
  label,
  value,
  onChange,
}: {
  label: string;
  value: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className="setting-row">
      <span className="text-sm">{label}</span>
      <button
        className={`setting-toggle ${value ? "setting-toggle-on" : ""}`}
        onClick={() => onChange(!value)}
        role="switch"
        aria-checked={value}
        type="button"
      >
        <span className="setting-toggle-dot" />
      </button>
    </div>
  );
}
