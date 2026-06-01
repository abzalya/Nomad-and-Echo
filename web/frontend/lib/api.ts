// Thin client for the FastAPI gateway (web/gateway).
// Contract: spec §16.3.
// BASE is empty by default => calls are relative ("/api/..."), same-origin.
//   prod: Traefik routes <domain>/api/* to the gateway (same origin, no CORS).
//   dev:  next.config.ts rewrites() proxies /api/* to the gateway at runtime.
// NEXT_PUBLIC_API_URL stays as an optional escape hatch; leave it unset so
// nothing is baked into the bundle.
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

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
