// Thin client for the FastAPI gateway (web/gateway).
// Contract: spec §16.3. Set NEXT_PUBLIC_API_URL to override the default.

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Opponent = "nomad" | "echo";

export type MoveRequest = {
  fen: string;
  history: string[];
  opponent: Opponent;
  think_ms?: number;
};

export type MoveResponse = {
  uci: string;
  san: string;
  eval?: number | null;
  depth?: number | null;
  time_ms: number;
};

export type HintRequest = { fen: string; history: string[] };
export type HintResponse = { uci: string; san: string };
export type HealthResponse = { status: "ok"; version: string };

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  return (await res.json()) as T;
}

export const api = {
  health: async (): Promise<HealthResponse> => {
    const res = await fetch(`${BASE}/api/health`);
    if (!res.ok) throw new Error(`health: ${res.status}`);
    return (await res.json()) as HealthResponse;
  },
  botMove: (req: MoveRequest) => post<MoveResponse>("/api/bot/move", req),
  hint: (req: HintRequest) => post<HintResponse>("/api/hint", req),
};
