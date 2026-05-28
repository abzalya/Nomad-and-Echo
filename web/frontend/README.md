# chess-room frontend

## Routes

- `/` — landing (hero + decorative endgame board + Nomad/Echo cards)
- `/play` — setup panel + dimmed board; clicking **Start game** flips to the
  in-game layout (identity rows, board, side panel with speech bubble, opening
  strip, move list, action row, footer)

The Welcome modal fires on first visit (gated by `seen_welcome` in
`localStorage`). The About modal is reachable from the top nav.

In-game design states from the prototype (`idle`, `selected`, `check`,
`promotion`, `bot-thinking`, `scrub`, `game-over`) are reachable via
`?state=<name>` on `/play` for visual review. Wiring them to real engine
responses is the next milestone.

## Layout

```
app/
  layout.tsx        # DM Sans + DM Mono via next/font; binds --font-* vars
  globals.css       # design tokens + all component styles (verbatim port)
  page.tsx          # landing
  play/page.tsx     # /play — setup view + in-game view
components/
  Board.tsx         # placeholder board (Unicode glyphs + design overlays)
  BotCard.tsx
  GameEndModal.tsx
  Icons.tsx         # Lucide-style stroke icons, 1.75px
  Modals.tsx        # About/Welcome modal + Settings popover
  PlaySetup.tsx     # opponent / color / time-control / start
  SidePanel.tsx     # identity row, speech bubble, opening strip, move list…
  TopNav.tsx
lib/
  api.ts            # gateway client (spec §16.3)
```

## Wired

- Real chess via `chess.js` + `react-chessboard`, themed to the design palette
  (square colours, last-move/selected/check overlays, legal dots, capture rings,
  hint highlight).
- Drag-and-drop **and** click-click move input.
- Custom promotion popover anchored to the promotion file (design's styling).
- Gateway integration: `POST /api/bot/move` after every user move; `POST
  /api/hint` from the lightbulb button. Both via `lib/api.ts`.
- Game store (Zustand, `lib/game.ts`) per spec §16.5. Persists to localStorage
  with `partialize` so refresh resumes the position.
- Terminal-state detection: checkmate, stalemate, threefold repetition, 50-move
  rule, insufficient material, timeout, resign.
- Timed clocks: countdown driven by a 250ms interval, low-time turns red,
  timeout ends the game.
- Takeback (drops user + bot plies), resign, rematch (swaps colour), new game,
  PGN download.
- Move scrubbing: click a move in the list to view the historical position;
  board becomes non-interactive; "return to live" pill appears.
- Speech bubble triggers (game start, check given/received, big capture, end).
- Opening name strip via a small ECO subset (`lib/openings.ts`); hides when no
  match.
- Settings popover (board theme, piece set placeholder + functional sound /
  dots / coords / auto-queen) persisted via `useSettings`.
- Welcome modal on first visit, About modal from top nav.
- Tab title per spec §17 (`Thinking…` / `Your move` / `Game over`).

## Backend

This frontend expects the gateway from [web/gateway](../gateway) on
`NEXT_PUBLIC_API_URL` (default `http://localhost:8000`). Start the stack via:

## Still TODO (post-v1)

- Sound effects (move / capture / check / castle / promote / end).
- Larger ECO library (currently ~20 openings).
- Premoves, keyboard board, dark mode (explicitly out of v1 per spec §23).

