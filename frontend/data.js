import { SUPABASE_CONFIG } from "./supabase-config.js?v=20260730-cloud";

const SNAPSHOT_DATES = [
  "2026-06-13",
  "2026-06-14",
  "2026-06-15",
  "2026-06-16",
  "2026-06-17",
  "2026-06-18",
  "2026-06-19",
  "2026-06-20",
  "2026-06-22",
  "2026-06-23",
  "2026-06-25",
  "2026-07-01",
  "2026-07-02",
  "2026-07-03",
  "2026-07-04",
  "2026-07-05",
  "2026-07-06",
  "2026-07-07",
  "2026-07-09",
  "2026-07-25",
  "2026-07-26",
  "2026-07-28",
  "2026-07-29",
];

const FIXTURE_SOURCE = Object.freeze({
  kind: "fixture",
  label: "Datos locales versionados",
  badge: "Fallback local",
  ranking: "../data/reviews/rankings/signal-review-ranking-2026-07-28.json",
  snapshots: SNAPSHOT_DATES.map(
    (date) => `../data/signals/daily/daily-radar-${date}.json`,
  ),
  contract: "../docs/contracts/ai-radar-daily.schema.json",
  note: "Supabase Cloud no respondió. La interfaz usa temporalmente los JSON versionados del repositorio.",
});

export const DATA_SOURCE = Object.freeze({
  kind: "supabase",
  label: "Supabase Cloud",
  badge: "Cloud",
  projectId: SUPABASE_CONFIG.projectId,
  url: SUPABASE_CONFIG.url,
  contract: "../docs/contracts/ai-radar-daily.schema.json",
  note: "Lectura pública desde Supabase Cloud con RLS y clave publicable.",
});

async function fetchJson(path) {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(`No se pudo leer ${path} (${response.status})`);
  }

  return response.json();
}

async function fetchSupabase(table, query) {
  const endpoint = `${SUPABASE_CONFIG.url}/rest/v1/${table}?${query}`;
  const response = await fetch(endpoint, {
    headers: {
      apikey: SUPABASE_CONFIG.publishableKey,
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Supabase ${table}: ${response.status}`);
  }
  return response.json();
}

function mapCloudSignal(entry, signal, snapshot) {
  return {
    signalId: entry.signal_id,
    rank: entry.rank,
    score: Number(entry.score),
    dimensions: entry.dimensions,
    reason: entry.reason,
    id: signal.id,
    radarDate: signal.radar_date,
    contractVersion: snapshot?.contract_version,
    title: signal.title,
    source: {
      name: signal.source_name,
      url: signal.source_url,
      publishedAt: signal.published_at,
      retrievedAt: signal.retrieved_at,
    },
    sourceType: signal.source_type,
    evidence: signal.evidence,
    impact: {
      level: signal.impact_level,
      summary: signal.impact_summary,
    },
    action: signal.action,
    status: signal.status,
    tags: signal.tags,
  };
}

async function loadCloudData() {
  const [rankings, entries, signals, snapshots] = await Promise.all([
    fetchSupabase(
      "rankings",
      "select=radar_date,generated_at,weights,audit&order=radar_date.desc&limit=1",
    ),
    fetchSupabase(
      "ranking_entries",
      "select=ranking_date,signal_id,rank,score,dimensions,reason&order=ranking_date.desc,rank.asc",
    ),
    fetchSupabase(
      "signals",
      "select=id,radar_date,title,source_name,source_url,published_at,retrieved_at,source_type,evidence,impact_level,impact_summary,action,status,tags",
    ),
    fetchSupabase(
      "radar_snapshots",
      "select=radar_date,contract_version",
    ),
  ]);

  const ranking = rankings[0];
  if (!ranking) throw new Error("Supabase no contiene rankings publicados.");

  const signalsById = new Map(signals.map((signal) => [signal.id, signal]));
  const snapshotsByDate = new Map(
    snapshots.map((snapshot) => [snapshot.radar_date, snapshot]),
  );
  const rankedSignals = entries
    .filter((entry) => entry.ranking_date === ranking.radar_date)
    .map((entry) => {
      const signal = signalsById.get(entry.signal_id);
      return signal
        ? mapCloudSignal(entry, signal, snapshotsByDate.get(signal.radar_date))
        : null;
    })
    .filter(Boolean);

  return {
    source: DATA_SOURCE,
    generatedAt: ranking.generated_at,
    radarDate: ranking.radar_date,
    rankedSignals,
    totalSignals: signals.length,
    rankedCount: ranking.audit.rankedSignals,
    sourceCount: new Set(signals.map((signal) => signal.source_name)).size,
    weights: ranking.weights,
    degraded: false,
  };
}

async function loadFixtureData() {
  const [ranking, ...snapshots] = await Promise.all([
    fetchJson(FIXTURE_SOURCE.ranking),
    ...FIXTURE_SOURCE.snapshots.map(fetchJson),
  ]);

  const signalsById = new Map();
  snapshots.forEach((snapshot) => {
    snapshot.signals.forEach((signal) => {
      signalsById.set(signal.id, {
        ...signal,
        radarDate: snapshot.radarDate,
        contractVersion: snapshot.contractVersion,
      });
    });
  });

  const rankedSignals = ranking.rankedSignals
    .map((entry) => {
      const signal = signalsById.get(entry.signalId);
      return signal ? { ...entry, ...signal } : null;
    })
    .filter(Boolean);

  const sourceCount = new Set(
    [...signalsById.values()].map((signal) => signal.source.name),
  ).size;

  return {
    source: FIXTURE_SOURCE,
    generatedAt: ranking.generatedAt,
    radarDate: ranking.radarDate,
    rankedSignals,
    totalSignals: signalsById.size,
    rankedCount: ranking.audit.rankedSignals,
    sourceCount,
    weights: ranking.weights,
    degraded: true,
  };
}

export async function loadRadarData({ demoState = "" } = {}) {
  if (demoState === "error") {
    throw new Error("Estado de error solicitado para verificación visual.");
  }

  let data;
  try {
    if (demoState === "fallback") {
      throw new Error("Fallback solicitado para verificación visual.");
    }
    data = await loadCloudData();
  } catch (cloudError) {
    try {
      data = await loadFixtureData();
      data.fallbackReason = cloudError.message;
    } catch (fixtureError) {
      throw new Error(
        `Supabase Cloud y el fallback local fallaron: ${fixtureError.message}`,
      );
    }
  }

  if (demoState === "empty") data.rankedSignals = [];
  return data;
}
