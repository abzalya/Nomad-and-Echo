// Tiny opening lookup. Matches the longest move-prefix in the table.
// Enough for the most common openings; deeper detection lands in a follow-up
// (the spec suggests pulling an ECO package at implementation time).

const OPENINGS: Array<{ moves: string[]; name: string }> = [
  { moves: ["e4", "c6"], name: "Caro-Kann Defense" },
  { moves: ["e4", "c5"], name: "Sicilian Defense" },
  { moves: ["e4", "e5"], name: "Open Game" },
  { moves: ["e4", "e5", "Nf3", "Nc6", "Bb5"], name: "Ruy López" },
  { moves: ["e4", "e5", "Nf3", "Nc6", "Bc4"], name: "Italian Game" },
  { moves: ["e4", "e6"], name: "French Defense" },
  { moves: ["e4", "d6"], name: "Pirc Defense" },
  { moves: ["e4", "Nf6"], name: "Alekhine's Defense" },
  { moves: ["e4", "g6"], name: "Modern Defense" },
  { moves: ["e4", "d5"], name: "Scandinavian Defense" },
  { moves: ["d4", "d5"], name: "Closed Game" },
  { moves: ["d4", "d5", "c4"], name: "Queen's Gambit" },
  { moves: ["d4", "Nf6"], name: "Indian Defense" },
  { moves: ["d4", "Nf6", "c4", "g6"], name: "King's Indian Defense" },
  { moves: ["d4", "Nf6", "c4", "e6"], name: "Nimzo-/Queen's Indian" },
  { moves: ["d4", "f5"], name: "Dutch Defense" },
  { moves: ["c4"], name: "English Opening" },
  { moves: ["Nf3"], name: "Réti Opening" },
  { moves: ["b3"], name: "Larsen's Opening" },
  { moves: ["g3"], name: "Benko's Opening" },
];

export function detectOpening(sanMoves: string[]): string | null {
  let best: string | null = null;
  let bestLen = 0;
  for (const entry of OPENINGS) {
    if (entry.moves.length > sanMoves.length) continue;
    let ok = true;
    for (let i = 0; i < entry.moves.length; i++) {
      if (sanMoves[i] !== entry.moves[i]) {
        ok = false;
        break;
      }
    }
    if (ok && entry.moves.length > bestLen) {
      best = entry.name;
      bestLen = entry.moves.length;
    }
  }
  return best;
}
