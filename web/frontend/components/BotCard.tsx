"use client";

import { BotAvatar, type Bot } from "./SidePanel";
import { IconArrowRight } from "./Icons";

export function BotCard({
  bot,
  title,
  tagline,
  tech,
  onPlay,
}: {
  bot: Bot;
  title: string;
  tagline: string;
  tech: string[];
  onPlay: () => void;
}) {
  return (
    <div className="bot-card">
      <div className="row gap-16" style={{ alignItems: "center" }}>
        <BotAvatar bot={bot} size={52} />
        <div className="col gap-4">
          <span className="text-lg weight-500">{title}</span>
          <span className="text-xs subtle mono">
            {bot === "nomad" ? "engine · default strength" : "mimic · experimental"}
          </span>
        </div>
      </div>
      <p className="bot-card-tagline text-base muted">{tagline}</p>
      <div className="bot-card-tech mono text-xs subtle">
        {tech.map((t, i) => (
          <span key={t}>
            {t}
            {i < tech.length - 1 && <span className="bot-card-dot"> · </span>}
          </span>
        ))}
      </div>
      <button className="btn btn-secondary" onClick={onPlay} type="button">
        Play {title}
        <IconArrowRight size={16} />
      </button>
    </div>
  );
}
