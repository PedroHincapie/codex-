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

export const DATA_SOURCE = Object.freeze({
  kind: "fixture",
  label: "Datos locales versionados",
  ranking: "../data/reviews/rankings/signal-review-ranking-2026-07-28.json",
  snapshots: SNAPSHOT_DATES.map(
    (date) => `../data/signals/daily/daily-radar-${date}.json`,
  ),
  contract: "../docs/contracts/ai-radar-daily.schema.json",
  note: "El frontend lee archivos JSON del repositorio. No consulta una API ni Supabase.",
});

async function fetchJson(path) {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(`No se pudo leer ${path} (${response.status})`);
  }

  return response.json();
}

export async function loadRadarData({ demoState = "" } = {}) {
  if (demoState === "error") {
    throw new Error("Estado de error solicitado para verificación visual.");
  }

  const [ranking, ...snapshots] = await Promise.all([
    fetchJson(DATA_SOURCE.ranking),
    ...DATA_SOURCE.snapshots.map(fetchJson),
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
    source: DATA_SOURCE,
    generatedAt: ranking.generatedAt,
    radarDate: ranking.radarDate,
    rankedSignals: demoState === "empty" ? [] : rankedSignals,
    totalSignals: signalsById.size,
    rankedCount: ranking.audit.rankedSignals,
    sourceCount,
    weights: ranking.weights,
  };
}
