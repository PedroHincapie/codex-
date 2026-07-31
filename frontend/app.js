import { loadRadarData } from "./data.js?v=20260730-resilient";

const PAGE_SIZE = 6;
const dimensionLabels = {
  novelty: "Novedad",
  evidence: "Evidencia",
  impact: "Impacto",
  reliability: "Confiabilidad",
  actionability: "Accionabilidad",
  strategicFit: "Ajuste estratégico",
};
const statusLabels = {
  actionable: "Accionable",
  confirmed: "Confirmada",
  evolving: "En evolución",
  candidate: "Candidata",
  debated: "En debate",
  archived: "Archivada",
};
const impactLabels = {
  high: "Alto",
  "medium-high": "Medio-alto",
  medium: "Medio",
  low: "Bajo",
};
const viewMetadata = {
  radar: {
    title: "Radar",
    eyebrow: "Inteligencia editorial",
    description: "Resumen operativo del corte editorial y sus señales prioritarias.",
  },
  rankings: {
    title: "Rankings",
    eyebrow: "Priorización",
    description: "Orden determinista de señales con impacto, confianza y evidencia.",
  },
  sources: {
    title: "Fuentes",
    eyebrow: "Procedencia",
    description: "Cobertura de fuentes observada en los snapshots cargados.",
  },
  evidence: {
    title: "Evidencia",
    eyebrow: "Trazabilidad",
    description: "Acceso directo a los dossiers y fuentes de cada señal.",
  },
  reviews: {
    title: "Revisiones",
    eyebrow: "Control editorial",
    description: "Cola verificable de señales que requieren decisión humana.",
  },
};

const state = {
  data: null,
  signals: [],
  filteredSignals: [],
  selectedId: null,
  mode: "reader",
  page: 1,
  evidenceOpen: true,
  draft: null,
  lastFocusedElement: null,
  activeView: "radar",
  notificationsDismissed: false,
};

const elements = {
  body: document.body,
  loading: document.querySelector("#loading-state"),
  error: document.querySelector("#error-state"),
  errorMessage: document.querySelector("#error-message"),
  empty: document.querySelector("#empty-state"),
  tableCard: document.querySelector("#table-card"),
  rankingBody: document.querySelector("#ranking-body"),
  resultsLabel: document.querySelector("#results-label"),
  pageLabel: document.querySelector("#page-label"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
  search: document.querySelector("#search-input"),
  statusFilter: document.querySelector("#status-filter"),
  impactFilter: document.querySelector("#impact-filter"),
  evidencePanel: document.querySelector("#evidence-panel"),
  evidenceContent: document.querySelector("#evidence-content"),
  evidenceToggle: document.querySelector("#evidence-toggle"),
  operatorPanel: document.querySelector("#operator-panel"),
  operatorTitle: document.querySelector("#operator-title"),
  operatorStatus: document.querySelector("#operator-status"),
  tagEditor: document.querySelector("#tag-editor"),
  scoringControls: document.querySelector("#scoring-controls"),
  weightedScore: document.querySelector("#weighted-score"),
  previewDialog: document.querySelector("#preview-dialog"),
  previewJson: document.querySelector("#preview-json"),
  toast: document.querySelector("#toast"),
  sidebar: document.querySelector("#sidebar"),
  menuButton: document.querySelector("#menu-button"),
  dataBadge: document.querySelector("#data-badge"),
  sourceNotice: document.querySelector("#source-notice"),
  sourceNoticeTitle: document.querySelector("#source-notice-title"),
  sourceNoticeText: document.querySelector("#source-notice-text"),
  dashboard: document.querySelector("#ranking-view"),
  sectionView: document.querySelector("#section-view"),
  sectionViewContent: document.querySelector("#section-view-content"),
  viewTitle: document.querySelector("#view-title"),
  viewEyebrow: document.querySelector("#view-eyebrow"),
  viewDescription: document.querySelector("#view-description"),
  notificationButton: document.querySelector("#notification-button"),
  notificationPanel: document.querySelector("#notification-panel"),
  notificationContent: document.querySelector("#notification-content"),
  notificationDot: document.querySelector("#notification-dot"),
};

const formatDate = (value) =>
  new Intl.DateTimeFormat("es-CO", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(value));

const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

function getDemoState() {
  return new URLSearchParams(window.location.search).get("demo") || "";
}

function getSelectedSignal() {
  return state.signals.find((signal) => signal.signalId === state.selectedId) || null;
}

function scoreToPercent(score) {
  return Math.round(score * 20);
}

function confidenceFor(signal) {
  const confidence = signal.dimensions.reliability;
  if (confidence >= 5) return { label: "Alta", percent: 92 };
  if (confidence >= 4) return { label: "Alta", percent: 82 };
  if (confidence >= 3) return { label: "Media", percent: 68 };
  return { label: "Baja", percent: 46 };
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.hidden = false;
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => {
    elements.toast.hidden = true;
  }, 3200);
}

function statusCounts() {
  return state.signals.reduce((counts, signal) => {
    counts[signal.status] = (counts[signal.status] || 0) + 1;
    return counts;
  }, {});
}

function getInitialView() {
  const candidate = window.location.hash.replace("#", "");
  return viewMetadata[candidate] ? candidate : "radar";
}

function setActiveView(view, { focus = true, updateUrl = true } = {}) {
  if (!viewMetadata[view]) return;
  state.activeView = view;
  document.querySelectorAll("[data-view]").forEach((button) => {
    const active = button.dataset.view === view;
    button.classList.toggle("is-active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  if (updateUrl) {
    const url = new URL(window.location.href);
    url.hash = view;
    window.history.replaceState(null, "", url);
  }
  elements.sidebar.classList.remove("is-open");
  elements.menuButton.setAttribute("aria-expanded", "false");
  elements.menuButton.setAttribute("aria-label", "Abrir navegación");
  renderActiveView();
  renderOperator();
  if (focus) {
    const target = view === "rankings" ? document.querySelector("#ranking-title") : elements.viewTitle;
    target?.focus();
  }
}

function renderActiveView() {
  const rankingsActive = state.activeView === "rankings";
  elements.dashboard.hidden = !rankingsActive;
  elements.sectionView.hidden = rankingsActive;
  if (rankingsActive || !state.data) return;

  const metadata = viewMetadata[state.activeView];
  elements.viewTitle.textContent = metadata.title;
  elements.viewEyebrow.textContent = metadata.eyebrow;
  elements.viewDescription.textContent = metadata.description;

  const renderers = {
    radar: renderRadarOverview,
    sources: renderSourcesView,
    evidence: renderEvidenceView,
    reviews: renderReviewsView,
  };
  elements.sectionViewContent.innerHTML = renderers[state.activeView]();
  bindSectionActions();
}

function renderRadarOverview() {
  const counts = statusCounts();
  const actionable = (counts.actionable || 0) + (counts.confirmed || 0);
  const review = (counts.candidate || 0) + (counts.debated || 0) + (counts.evolving || 0);
  const topSignals = state.signals.slice(0, 5).map((signal) => `
    <li>
      <span class="rank-number">${signal.rank}</span>
      <button type="button" data-open-signal="${escapeHtml(signal.signalId)}">
        <strong>${escapeHtml(signal.title)}</strong>
        <small>${escapeHtml(signal.source.name)} · ${escapeHtml(statusLabels[signal.status] || signal.status)}</small>
      </button>
      <strong class="impact-score">${scoreToPercent(signal.score)}</strong>
    </li>
  `).join("");
  return `
    <div class="overview-grid">
      <article class="metric-card"><span>Señales</span><strong>${state.data.totalSignals}</strong><small>Ranking acumulado</small></article>
      <article class="metric-card"><span>Fuentes</span><strong>${state.data.sourceCount}</strong><small>Observadas en snapshots</small></article>
      <article class="metric-card"><span>Listas para actuar</span><strong>${actionable}</strong><small>Accionables o confirmadas</small></article>
      <article class="metric-card"><span>Revisión pendiente</span><strong>${review}</strong><small>Candidatas, debatidas o en evolución</small></article>
    </div>
    <section class="view-block" aria-labelledby="priority-title">
      <h2 id="priority-title">Señales prioritarias</h2>
      <ol class="view-list">${topSignals}</ol>
    </section>
  `;
}

function renderSourcesView() {
  const sources = new Map();
  state.signals.forEach((signal) => {
    const key = signal.source.name;
    const current = sources.get(key) || {
      name: signal.source.name,
      url: signal.source.url,
      type: signal.sourceType || "sin-clasificar",
      count: 0,
      latest: signal.source.publishedAt,
    };
    current.count += 1;
    if (signal.source.publishedAt >= current.latest) {
      current.latest = signal.source.publishedAt;
      current.url = signal.source.url;
    }
    sources.set(key, current);
  });
  const cards = [...sources.values()]
    .sort((left, right) => right.count - left.count || left.name.localeCompare(right.name))
    .map((source) => `
      <article class="source-card-view">
        <header><strong>${escapeHtml(source.name)}</strong><span class="source-type">${escapeHtml(source.type)}</span></header>
        <small>${source.count} señales · última publicación ${escapeHtml(source.latest)}</small>
        <a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">Abrir fuente <span aria-hidden="true">↗</span></a>
      </article>
    `).join("");
  return `<div class="source-grid">${cards}</div>`;
}

function renderEvidenceView() {
  const cards = state.signals.slice(0, 18).map((signal) => `
    <article class="evidence-card">
      <header><span class="status status-${escapeHtml(signal.status)}">${escapeHtml(statusLabels[signal.status] || signal.status)}</span><strong>#${signal.rank}</strong></header>
      <button type="button" data-open-signal="${escapeHtml(signal.signalId)}"><strong>${escapeHtml(signal.title)}</strong></button>
      <small>${signal.evidence.length} evidencias · ${escapeHtml(signal.source.name)}</small>
    </article>
  `).join("");
  return `<div class="evidence-grid">${cards}</div>`;
}

function renderReviewsView() {
  const counts = statusCounts();
  const reviewSignals = state.signals.filter((signal) =>
    ["candidate", "debated", "evolving"].includes(signal.status)
  );
  const queue = reviewSignals.slice(0, 8).map((signal) => `
    <li>
      <span class="rank-number">${signal.rank}</span>
      <button type="button" data-open-signal="${escapeHtml(signal.signalId)}">
        <strong>${escapeHtml(signal.title)}</strong>
        <small>${escapeHtml(statusLabels[signal.status] || signal.status)} · ${escapeHtml(signal.source.name)}</small>
      </button>
      <span class="status status-${escapeHtml(signal.status)}">${escapeHtml(statusLabels[signal.status] || signal.status)}</span>
    </li>
  `).join("");
  return `
    <div class="review-grid">
      <article class="content-card"><strong>${counts.candidate || 0}</strong><p>Candidatas pendientes de evidencia o decisión.</p></article>
      <article class="content-card"><strong>${counts.evolving || 0}</strong><p>En evolución y sujetas a seguimiento.</p></article>
      <article class="content-card"><strong>${counts.debated || 0}</strong><p>En debate y con revisión humana necesaria.</p></article>
    </div>
    <section class="view-block" aria-labelledby="review-queue-title">
      <h2 id="review-queue-title">Cola de revisión</h2>
      ${queue ? `<ol class="view-list">${queue}</ol>` : '<div class="notification-empty">No hay revisiones pendientes.</div>'}
    </section>
  `;
}

function bindSectionActions() {
  elements.sectionViewContent.querySelectorAll("[data-open-signal]").forEach((button) => {
    button.addEventListener("click", () => {
      setActiveView("rankings", { focus: false });
      selectSignal(button.dataset.openSignal);
      document.querySelector("#ranking-title")?.focus();
    });
  });
}

function buildNotifications() {
  if (!state.data || state.notificationsDismissed) return [];
  const notifications = [];
  const pendingReview = state.signals.filter((signal) =>
    ["candidate", "debated", "evolving"].includes(signal.status)
  ).length;
  if (pendingReview) {
    notifications.push({
      icon: "◇",
      title: `${pendingReview} señales requieren revisión`,
      detail: "La cola incluye candidatas, señales en debate y señales en evolución.",
    });
  }
  if (state.data.degraded) {
    notifications.push({
      icon: "△",
      title: "Fuente de datos degradada",
      detail: state.data.fallbackReason || "El dashboard está usando el fallback local.",
    });
  }
  return notifications;
}

function renderNotifications() {
  const notifications = buildNotifications();
  elements.notificationDot.hidden = notifications.length === 0;
  elements.notificationButton.setAttribute(
    "aria-label",
    notifications.length ? `Notificaciones, ${notifications.length} pendientes` : "Notificaciones, sin pendientes",
  );
  elements.notificationContent.innerHTML = notifications.length
    ? `
      <ul class="notification-list">
        ${notifications.map((item) => `
          <li><span aria-hidden="true">${item.icon}</span><div><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.detail)}</small></div></li>
        `).join("")}
      </ul>
      <div class="notification-actions"><button class="text-button" id="notification-clear" type="button">Marcar como revisadas</button></div>
    `
    : '<div class="notification-empty"><span>No hay notificaciones pendientes para este corte.</span></div>';
  document.querySelector("#notification-clear")?.addEventListener("click", () => {
    state.notificationsDismissed = true;
    renderNotifications();
    showToast("Notificaciones marcadas como revisadas en esta sesión.");
  });
}

function toggleNotifications(forceOpen) {
  const open = forceOpen ?? elements.notificationPanel.hidden;
  elements.notificationPanel.hidden = !open;
  elements.notificationButton.setAttribute("aria-expanded", String(open));
  if (open) elements.notificationPanel.focus();
  else elements.notificationButton.focus();
}

async function initialize() {
  elements.loading.hidden = false;
  elements.error.hidden = true;
  elements.empty.hidden = true;
  elements.tableCard.hidden = true;

  try {
    const data = await loadRadarData({ demoState: getDemoState() });
    state.data = data;
    state.signals = data.rankedSignals;
    state.filteredSignals = [...state.signals];
    state.selectedId = state.signals[0]?.signalId || null;
    state.page = 1;
    state.activeView = getInitialView();

    document.querySelector("#last-updated").textContent =
      `Corte editorial: ${formatDate(data.generatedAt)}`;
    document.querySelector("#sidebar-signal-count").textContent =
      data.totalSignals.toLocaleString("es-CO");
    document.querySelector("#sidebar-source-count").textContent =
      `${data.sourceCount} fuentes en snapshots`;
    elements.dataBadge.textContent = data.source.badge;
    elements.sourceNotice.classList.toggle("is-degraded", data.degraded);
    elements.sourceNoticeTitle.textContent = `${data.source.label}.`;
    elements.sourceNoticeText.textContent = data.degraded
      ? `Modo degradado: ${data.source.note} Motivo: ${data.fallbackReason}`
      : "Ranking y señales consultados desde la Data API protegida por RLS.";

    render();
    window.dispatchEvent(new Event("airadar:ready"));
  } catch (error) {
    elements.loading.hidden = true;
    elements.error.hidden = false;
    elements.errorMessage.textContent = error.message;
    window.dispatchEvent(new Event("airadar:ready"));
  }
}

function render() {
  renderRanking();
  renderEvidence();
  renderActiveView();
  renderOperator();
  renderNotifications();
}

function renderRanking() {
  elements.loading.hidden = true;
  elements.error.hidden = true;

  const hasSignals = state.filteredSignals.length > 0;
  elements.empty.hidden = hasSignals;
  elements.tableCard.hidden = !hasSignals;

  if (!hasSignals) return;

  const pageCount = Math.max(1, Math.ceil(state.filteredSignals.length / PAGE_SIZE));
  state.page = Math.min(state.page, pageCount);
  const start = (state.page - 1) * PAGE_SIZE;
  const pageSignals = state.filteredSignals.slice(start, start + PAGE_SIZE);

  elements.rankingBody.innerHTML = pageSignals
    .map((signal) => {
      const confidence = confidenceFor(signal);
      const selected = signal.signalId === state.selectedId;
      const tags = signal.tags
        .slice(0, 2)
        .map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`)
        .join("");

      return `
        <tr class="${selected ? "is-selected" : ""}" data-signal-id="${escapeHtml(signal.signalId)}">
          <td class="rank-cell">
            <button
              class="row-select"
              type="button"
              data-select-signal="${escapeHtml(signal.signalId)}"
              aria-label="Abrir evidencia de ${escapeHtml(signal.title)}"
              aria-pressed="${selected}"
            >
              ${signal.rank}
            </button>
          </td>
          <td class="signal-cell">
            <button
              class="signal-title"
              type="button"
              data-select-signal="${escapeHtml(signal.signalId)}"
            >
              ${escapeHtml(signal.title)}
            </button>
            <span>${escapeHtml(signal.impact.summary)}</span>
          </td>
          <td>
            <strong class="impact-score">${scoreToPercent(signal.score)}</strong>
            <span class="cell-note">/100</span>
          </td>
          <td>
            <strong class="confidence ${confidence.label.toLowerCase()}">${confidence.label}</strong>
            <span class="cell-note">${confidence.percent}%</span>
          </td>
          <td>
            <span class="status status-${escapeHtml(signal.status)}">
              ${escapeHtml(statusLabels[signal.status] || signal.status)}
            </span>
          </td>
          <td><div class="tags">${tags}</div></td>
          <td>
            <span class="source-avatar" title="${escapeHtml(signal.source.name)}">
              ${escapeHtml(signal.source.name.slice(0, 2).toUpperCase())}
            </span>
          </td>
        </tr>
      `;
    })
    .join("");

  elements.rankingBody.querySelectorAll("[data-select-signal]").forEach((button) => {
    button.addEventListener("click", () => selectSignal(button.dataset.selectSignal));
  });

  const end = Math.min(start + PAGE_SIZE, state.filteredSignals.length);
  elements.resultsLabel.textContent =
    `Mostrando ${start + 1}–${end} de ${state.filteredSignals.length} señales`;
  elements.pageLabel.textContent = `Página ${state.page} de ${pageCount}`;
  elements.previousPage.disabled = state.page === 1;
  elements.nextPage.disabled = state.page === pageCount;
}

function renderEvidence() {
  const signal = getSelectedSignal();

  if (!signal) {
    elements.evidenceContent.innerHTML =
      '<div class="panel-placeholder">No hay una señal seleccionada.</div>';
    return;
  }

  const evidenceItems = signal.evidence
    .map(
      (item) => `
        <li>
          <span class="evidence-check" aria-hidden="true">✓</span>
          <span>${escapeHtml(item)}</span>
        </li>
      `,
    )
    .join("");

  elements.evidenceContent.innerHTML = `
    <article>
      <div class="evidence-kicker">
        <span class="status status-${escapeHtml(signal.status)}">
          ${escapeHtml(statusLabels[signal.status] || signal.status)}
        </span>
        <span>${escapeHtml(impactLabels[signal.impact.level] || signal.impact.level)} impacto</span>
      </div>
      <h3>${escapeHtml(signal.title)}</h3>
      <p class="evidence-summary">${escapeHtml(signal.impact.summary)}</p>
      <div class="tags evidence-tags">
        ${signal.tags.slice(0, 5).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}
      </div>

      <section class="evidence-section" aria-labelledby="source-title">
        <div class="subheading-row">
          <h4 id="source-title">Fuente principal</h4>
          <span class="source-type">${escapeHtml(signal.sourceType || "sin clasificar")}</span>
        </div>
        <a class="source-card" href="${escapeHtml(signal.source.url)}" target="_blank" rel="noreferrer">
          <span class="source-logo">${escapeHtml(signal.source.name.slice(0, 2).toUpperCase())}</span>
          <span>
            <strong>${escapeHtml(signal.source.name)}</strong>
            <small>Publicada ${escapeHtml(signal.source.publishedAt)} · recuperada ${escapeHtml(signal.source.retrievedAt)}</small>
          </span>
          <span aria-hidden="true">↗</span>
        </a>
      </section>

      <section class="evidence-section" aria-labelledby="facts-title">
        <h4 id="facts-title">Evidencia</h4>
        <ul class="evidence-list">${evidenceItems}</ul>
      </section>

      <section class="evidence-section rationale" aria-labelledby="rationale-title">
        <h4 id="rationale-title">Rationale del ranking</h4>
        <p>${escapeHtml(signal.reason)}</p>
      </section>

      <section class="recommended-action" aria-labelledby="action-title">
        <span aria-hidden="true">◎</span>
        <div>
          <h4 id="action-title">Acción recomendada</h4>
          <p>${escapeHtml(signal.action)}</p>
        </div>
      </section>
    </article>
  `;
}

function createDraft(signal) {
  if (!signal) return null;
  return {
    id: signal.id,
    title: signal.title,
    status: signal.status,
    tags: [...signal.tags],
    dimensions: { ...signal.dimensions },
    source: { ...signal.source },
    sourceType: signal.sourceType,
    evidence: [...signal.evidence],
    impact: { ...signal.impact },
    action: signal.action,
    provenance: {
      kind: state.data.source.kind,
      endpoint: state.data.source.url,
      ranking: state.data.source.ranking,
      contract: state.data.source.contract,
      persisted: false,
    },
  };
}

function renderOperator() {
  const operatorActive = state.mode === "operator";
  const signal = getSelectedSignal();
  const operatorVisible = operatorActive && state.activeView === "rankings" && Boolean(signal);
  elements.operatorPanel.hidden = !operatorVisible;
  elements.body.classList.toggle("operator-mode", operatorVisible);
  if (!operatorVisible) return;

  if (!state.draft || state.draft.id !== signal.id) {
    state.draft = createDraft(signal);
  }

  elements.operatorTitle.textContent = `Operator mode · Signal #${signal.rank}`;
  elements.operatorStatus.value = state.draft.status;
  renderTags();
  renderScoringControls();
}

function renderTags() {
  elements.tagEditor.innerHTML = state.draft.tags
    .map(
      (tag) => `
        <span class="tag editable-tag">
          ${escapeHtml(tag)}
          <button type="button" data-remove-tag="${escapeHtml(tag)}" aria-label="Eliminar tag ${escapeHtml(tag)}">×</button>
        </span>
      `,
    )
    .join("");

  elements.tagEditor.querySelectorAll("[data-remove-tag]").forEach((button) => {
    button.addEventListener("click", () => {
      state.draft.tags = state.draft.tags.filter((tag) => tag !== button.dataset.removeTag);
      renderTags();
    });
  });
}

function renderScoringControls() {
  const editableDimensions = Object.keys(dimensionLabels);
  elements.scoringControls.innerHTML = editableDimensions
    .map((dimension) => {
      const value = state.draft.dimensions[dimension] * 20;
      return `
        <label class="score-control">
          <span>${dimensionLabels[dimension]}</span>
          <input
            type="range"
            min="0"
            max="100"
            step="20"
            value="${value}"
            data-score-dimension="${dimension}"
          >
          <output>${value}</output>
        </label>
      `;
    })
    .join("");

  elements.scoringControls.querySelectorAll("[data-score-dimension]").forEach((input) => {
    input.addEventListener("input", () => {
      state.draft.dimensions[input.dataset.scoreDimension] = Number(input.value) / 20;
      input.nextElementSibling.value = input.value;
      updateWeightedScore();
    });
  });
  updateWeightedScore();
}

function updateWeightedScore() {
  const weights = state.data.weights;
  const total = Object.entries(weights).reduce(
    (sum, [dimension, weight]) =>
      sum + (state.draft.dimensions[dimension] || 0) * weight,
    0,
  );
  elements.weightedScore.textContent = Math.round(total * 20);
}

function selectSignal(signalId) {
  state.selectedId = signalId;
  state.draft = null;
  state.evidenceOpen = true;
  elements.evidencePanel.classList.remove("is-closed");
  elements.evidenceToggle.setAttribute("aria-expanded", "true");
  render();
}

function applyFilters() {
  const query = elements.search.value.trim().toLowerCase();
  const status = elements.statusFilter.value;
  const impact = elements.impactFilter.value;

  state.filteredSignals = state.signals.filter((signal) => {
    const haystack = [
      signal.title,
      signal.impact.summary,
      signal.source.name,
      ...signal.tags,
    ]
      .join(" ")
      .toLowerCase();
    return (
      (!query || haystack.includes(query)) &&
      (!status || signal.status === status) &&
      (!impact || signal.impact.level === impact)
    );
  });
  state.page = 1;
  if (!state.filteredSignals.some((signal) => signal.signalId === state.selectedId)) {
    state.selectedId = state.filteredSignals[0]?.signalId || null;
    state.draft = null;
  }
  render();
}

function clearFilters() {
  elements.search.value = "";
  elements.statusFilter.value = "";
  elements.impactFilter.value = "";
  applyFilters();
  elements.search.focus();
}

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll("[data-mode]").forEach((button) => {
    const active = button.dataset.mode === mode;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  if (mode === "operator" && state.activeView !== "rankings") {
    setActiveView("rankings", { focus: false });
  }
  renderOperator();
  if (mode === "operator") {
    elements.operatorPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function toggleEvidence(forceOpen) {
  state.evidenceOpen = forceOpen ?? !state.evidenceOpen;
  elements.evidencePanel.classList.toggle("is-closed", !state.evidenceOpen);
  elements.evidenceToggle.setAttribute("aria-expanded", String(state.evidenceOpen));
  if (!state.evidenceOpen) elements.evidenceToggle.focus();
}

function buildDraftExport() {
  return {
    generatedAt: new Date().toISOString(),
    mode: "local-draft",
    persisted: false,
    contractVersion: getSelectedSignal()?.contractVersion,
    signal: state.draft,
  };
}

function exportDraft() {
  const payload = JSON.stringify(buildDraftExport(), null, 2);
  const blob = new Blob([payload], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${state.draft.id}-draft.json`;
  anchor.click();
  URL.revokeObjectURL(url);
  showToast("Borrador exportado. Los snapshots del repositorio no fueron modificados.");
}

function openPreview() {
  state.lastFocusedElement = document.activeElement;
  elements.previewJson.textContent = JSON.stringify(buildDraftExport(), null, 2);
  elements.previewDialog.showModal();
  document.querySelector("#dialog-close").focus();
}

function closePreview() {
  elements.previewDialog.close();
  state.lastFocusedElement?.focus();
}

document.querySelectorAll("[data-mode]").forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => setActiveView(button.dataset.view));
});

elements.notificationButton.addEventListener("click", () => toggleNotifications());
document.querySelector("#notification-close").addEventListener("click", () => toggleNotifications(false));

elements.search.addEventListener("input", applyFilters);
elements.statusFilter.addEventListener("change", applyFilters);
elements.impactFilter.addEventListener("change", applyFilters);
document.querySelector("#clear-filters").addEventListener("click", clearFilters);
document.querySelector("#empty-clear-button").addEventListener("click", clearFilters);
document.querySelector("#retry-button").addEventListener("click", initialize);

elements.previousPage.addEventListener("click", () => {
  state.page -= 1;
  renderRanking();
});
elements.nextPage.addEventListener("click", () => {
  state.page += 1;
  renderRanking();
});

document.querySelector("#filter-button").addEventListener("click", (event) => {
  const popover = document.querySelector("#filter-popover");
  popover.hidden = !popover.hidden;
  event.currentTarget.setAttribute("aria-expanded", String(!popover.hidden));
  if (!popover.hidden) elements.statusFilter.focus();
});

document.querySelector("#evidence-close").addEventListener("click", () => toggleEvidence(false));
elements.evidenceToggle.addEventListener("click", () => toggleEvidence());

elements.operatorStatus.addEventListener("change", () => {
  state.draft.status = elements.operatorStatus.value;
  showToast("Estado actualizado en el borrador local.");
});

document.querySelector("#tag-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const input = document.querySelector("#tag-input");
  const tag = input.value.trim().toLowerCase();
  if (!/^[a-z0-9-]+$/.test(tag)) {
    input.setCustomValidity("Usa minúsculas, números y guiones.");
    input.reportValidity();
    return;
  }
  input.setCustomValidity("");
  if (!state.draft.tags.includes(tag)) state.draft.tags.push(tag);
  input.value = "";
  renderTags();
  input.focus();
});

document.querySelector("#preview-button").addEventListener("click", openPreview);
document.querySelector("#publish-button").addEventListener("click", exportDraft);
document.querySelector("#dialog-close").addEventListener("click", closePreview);
document.querySelector("#dialog-cancel").addEventListener("click", closePreview);
document.querySelector("#dialog-export").addEventListener("click", exportDraft);

elements.previewDialog.addEventListener("click", (event) => {
  if (event.target === elements.previewDialog) closePreview();
});

document.querySelector("#source-details-button").addEventListener("click", () => {
  const source = state.data?.source;
  showToast(
    source
      ? `${source.label}: ${source.note}`
      : "La fuente de datos todavía se está validando.",
  );
});

elements.menuButton.addEventListener("click", () => {
  const open = elements.sidebar.classList.toggle("is-open");
  elements.menuButton.setAttribute("aria-expanded", String(open));
  elements.menuButton.setAttribute("aria-label", open ? "Cerrar navegación" : "Abrir navegación");
});

document.querySelector("#theme-button").addEventListener("click", (event) => {
  const enabled = elements.body.classList.toggle("high-contrast");
  event.currentTarget.setAttribute(
    "aria-label",
    enabled ? "Restaurar contraste" : "Aumentar contraste",
  );
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !elements.notificationPanel.hidden) {
    toggleNotifications(false);
    return;
  }
  if (event.key === "Escape" && elements.sidebar.classList.contains("is-open")) {
    elements.sidebar.classList.remove("is-open");
    elements.menuButton.setAttribute("aria-expanded", "false");
    elements.menuButton.focus();
  }
});

window.addEventListener("hashchange", () => {
  setActiveView(getInitialView(), { updateUrl: false });
});

initialize();
