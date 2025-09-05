import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || "http://localhost:8000",
  timeout: 8000,
});

export type Player = {
  id: number;
  first_name: string;
  last_name: string;
  jersey_number?: number | null;
  created_at: string;
  // Aggregated stats
  games_played: number;
  plate_appearances: number;
  at_bats: number;
  hits: number;
  singles: number;
  doubles: number;
  triples: number;
  home_runs: number;
  rbis: number;
  walks: number;
  strikeouts: number;
  sac_bunts: number;
  sac_flies: number;
  total_bases: number;
  average: number;
  slugging: number;
  on_base_percent: number;
  on_base_percent_plus_slugging: number;
  errors: number;
  hit_by_pitches: number;
};

export type Game = {
  id: number;
  opponent: string;
  date: string; // yyyy-mm-dd
  time?: string | null;
  location?: string | null;
  notes?: string | null;
  created_at: string;
  score_ours?: number | null;
  score_opponent?: number | null;
};

export type Stat = {
  id: number;
  player_id: number;
  player_first_name: string;
  player_last_name: string;
  game_id: number;
  at_bats: number;
  hits: number;
  singles: number;
  doubles: number;
  triples: number;
  home_runs: number;
  rbis: number;
  walks: number;
  strikeouts: number;
  sac_flies: number;
  hit_by_pitches: number;
  errors: number;
  created_at: string;
};

export type StatInput = {
  player_id: number;
  game_id: number;
  at_bats: number;
  hits: number;
  singles: number;
  doubles: number;
  triples: number;
  home_runs: number;
  rbis: number;
  walks: number;
  strikeouts: number;
  sac_flies: number;
  hit_by_pitches: number;
  errors: number;
};

function getToken() { return localStorage.getItem("ADMIN_TOKEN") || ""; }

api.interceptors.request.use((config) => {
  const t = getToken();
  if (t && config && config.headers) {
    (config.headers as any).Authorization = `Bearer ${t}`;
  }
  return config;
});

export function setToken(token: string){
  if (token) localStorage.setItem("ADMIN_TOKEN", token);
  else localStorage.removeItem("ADMIN_TOKEN");
}

export function isAuthed(){ return !!localStorage.getItem("ADMIN_TOKEN"); }

export async function listPlayers() {
  const { data } = await api.get<Player[]>("/players");
  return data;
}

export async function createPlayer(payload: {first_name: string; last_name: string; jersey_number?: number | null}) {
  const { data } = await api.post<Player>("/players", payload);
  return data;
}

export async function listGames() {
  const { data } = await api.get<Game[]>("/games");
  return data;
}

export async function createGame(payload: {opponent: string; date: string; time?: string; location?: string; notes?: string}) {
  const { data } = await api.post<Game>("/games", payload);
  return data;
}

export async function upsertStat(payload: StatInput) {
  const { data } = await api.post("/stats", payload);
  return data;
}

export async function aggregate(params: {
  player_id?: number; game_id?: number; date_from?: string; date_to?: string;
}) {
  const { data } = await api.get("/stats/aggregate", { params });
  return data as {
    at_bats:number; hits:number; singles:number; doubles:number; triples:number; home_runs:number;
    rbis:number; walks:number; strikeouts:number; sac_flies:number; hit_by_pitches:number; errors:number;
    total_bases:number; average:number; slugging:number; on_base_percent:number; on_base_percent_plus_slugging:number;
  };
}

export async function listStats(params: { player_id?: number; game_id?: number }) {
  const { data } = await api.get<Stat[]>("/stats", { params });
  return data;
}

export async function getPlayer(id: number) {
  const list = await listPlayers();
  return list.find(p => p.id === id) ?? null;
}

export async function getGame(id: number) {
  const list = await listGames();
  return list.find(g => g.id === id) ?? null;
}

export async function listPlayersQ(params: { q?: string }) {
  const { data } = await api.get<Player[]>("/players", { params });
  return data;
}

export async function listGamesQ(params: { opponent?: string; date_from?: string; date_to?: string }) {
  const { data } = await api.get<Game[]>("/games", { params });
  return data;
}
