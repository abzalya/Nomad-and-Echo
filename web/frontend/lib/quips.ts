// Bot speech lines. Edit freely — one entry per line in each array. The store
// picks one at random when a trigger fires.
//
// Triggers (spec §10):
//   check-given     — bot just put you in check
//   check-received  — you just put the bot in check
//   big-capture     — a piece worth ≥3 was captured on the last move
//   win             — bot won the game
//   loss            — bot lost the game
//   draw            — game ended in a draw
//
// (`start` is intentionally absent — no quip at game start.)

import type { SpeechTrigger } from "./game";
import type { Bot } from "@/components/SidePanel";

export const QUIPS: Record<Bot, Record<SpeechTrigger, string[]>> = {
  nomad: {
    start: [],
    "check-given": ["Predictable.", "Anticipated."],
    "check-received": ["Acceptable.", "Recalculating."],
    "big-capture": ["A reasonable trade.", "Equity preserved."],
    win: ["Outcome confirmed."],
    loss: ["Recalibrating."],
    draw: ["Insufficient force."],
  },
  echo: {
    start: [],
    "check-given": ["That's something I'd play.", "Felt right."],
    "check-received": ["Yeah, you got me.", "I'd play that too."],
    "big-capture": ["You'd probably play that too.", "Familiar."],
    win: ["Familiar shape."],
    loss: ["Hm. Off-style."],
    draw: ["Reasonable outcome."],
  },
};

export function pickQuip(bot: Bot, trigger: SpeechTrigger): string | null {
  const lines = QUIPS[bot][trigger];
  if (!lines || lines.length === 0) return null;
  return lines[Math.floor(Math.random() * lines.length)];
}
