const state = {
  alpha: null,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

init().catch((error) => {
  $("#statusLine").textContent = `Error: ${error.message}`;
});

async function init() {
  setupTabs();
  state.alpha = await requestJson("/api/state");
  $("#statusLine").textContent = `${state.alpha.build_count} builds loaded`;
  populateSelectors();
  renderCoverage();
  $("#stateDump").textContent = JSON.stringify(state.alpha, null, 2);
  $("#characterInput").value = JSON.stringify(state.alpha.sample_character, null, 2);
  $("#recommendForm").addEventListener("submit", onRecommend);
  $("#diagnoseForm").addEventListener("submit", onDiagnose);
  $("#loadSample").addEventListener("click", () => {
    $("#characterInput").value = JSON.stringify(state.alpha.sample_character, null, 2);
  });
  await onRecommend(new Event("submit"));
}

function setupTabs() {
  $$(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      $$(".tab").forEach((tab) => tab.classList.remove("active"));
      $$(".view").forEach((view) => view.classList.remove("active"));
      button.classList.add("active");
      document.getElementById(button.dataset.view).classList.add("active");
    });
  });
}

function populateSelectors() {
  const classes = state.alpha.ascendancies.classes;
  $("#classSelect").innerHTML = `<option value="">不限</option>${classes
    .map((entry) => `<option value="${escapeHtml(entry.class)}">${escapeHtml(entry.class)}</option>`)
    .join("")}`;
  updateAscendancies();
  $("#classSelect").addEventListener("change", updateAscendancies);
}

function updateAscendancies() {
  const selectedClass = $("#classSelect").value;
  const entries = state.alpha.ascendancies.classes;
  const ascendancies = entries
    .filter((entry) => !selectedClass || entry.class === selectedClass)
    .flatMap((entry) => entry.ascendancies);
  $("#ascendancySelect").innerHTML = `<option value="">不限</option>${ascendancies
    .map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`)
    .join("")}`;
}

async function onRecommend(event) {
  event.preventDefault();
  const form = new FormData($("#recommendForm"));
  const payload = {
    player_class: form.get("player_class"),
    ascendancy: form.get("ascendancy"),
    playstyles: form.get("playstyles"),
    budget: form.get("budget"),
    budget_divines: numberOrNull(form.get("budget_divines")),
    trade_mode: form.get("trade_mode"),
    hardcore: form.get("hardcore") === "on",
    avoid_uniques: form.get("avoid_uniques") === "on",
    controller_friendly: form.get("controller_friendly") === "on",
    top: 5,
  };
  const data = await postJson("/api/recommend", payload);
  $("#recommendMeta").textContent = data.warning;
  renderRecommendResults(data.results);
}

async function onDiagnose(event) {
  event.preventDefault();
  const form = new FormData($("#diagnoseForm"));
  const payload = {
    budget_divines: numberOrNull(form.get("budget_divines")),
    character: JSON.parse(form.get("character")),
  };
  const data = await postJson("/api/diagnose", payload);
  $("#diagnoseMeta").textContent = data.warning;
  renderDiagnosis(data.recommendations);
}

function renderRecommendResults(results) {
  $("#recommendResults").innerHTML = results.map((item, index) => {
    const build = item.build;
    const concerns = item.concerns.map((text) => `<div class="warn">${escapeHtml(text)}</div>`).join("");
    const strengths = item.strengths.map((text) => `<div class="good">${escapeHtml(text)}</div>`).join("");
    return `
      <article class="result">
        <div class="resultTop">
          <div>
            <div class="resultTitle">${index + 1}. ${escapeHtml(build.name)}</div>
            <div class="meta">${escapeHtml(build.player_class)} / ${escapeHtml(build.ascendancy)} / ${escapeHtml(build.main_skill)}</div>
          </div>
          <div class="score">${item.total.toFixed(2)}</div>
        </div>
        <div class="chips">
          <span class="chip">${escapeHtml(build.budget)}</span>
          <span class="chip">${build.estimated_cost_divines ?? "?"}D</span>
          <span class="chip">${escapeHtml(build.damage_type)}</span>
          <span class="chip">risk ${escapeHtml(build.nerf_risk)}</span>
        </div>
        <div class="small">Key: ${(build.key_items || []).map(escapeHtml).join(", ") || "none"}</div>
        <div class="small">Defence: ${(build.defensive_layers || []).map(escapeHtml).join(", ") || "none"}</div>
        ${strengths}
        ${concerns}
      </article>`;
  }).join("");
}

function renderDiagnosis(items) {
  $("#diagnoseResults").innerHTML = items.map((item, index) => `
    <article class="result">
      <div class="resultTop">
        <div>
          <div class="resultTitle">${index + 1}. ${escapeHtml(item.title)}</div>
          <div class="meta">${escapeHtml(item.slot)} / ${item.estimated_cost_divines}D</div>
        </div>
        <div class="score">${Math.round(item.confidence * 100)}%</div>
      </div>
      <div class="chips">
        <span class="chip">damage +${item.estimated_damage_gain_pct}%</span>
        <span class="chip">survival +${item.estimated_survival_gain_pct}%</span>
      </div>
      <div>${escapeHtml(item.reason)}</div>
    </article>`).join("");
}

function renderCoverage() {
  $("#ascendancyCoverage").innerHTML = state.alpha.ascendancies.classes.map((entry) => `
    <div class="coverageRow">
      <strong>${escapeHtml(entry.class)}</strong>
      <div>${entry.ascendancies.length ? entry.ascendancies.map(escapeHtml).join(", ") : "<span class='bad'>pending</span>"}</div>
    </div>`).join("");
}

async function requestJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error((await response.json()).error || response.statusText);
  return response.json();
}

function numberOrNull(value) {
  if (value === null || value === "") return null;
  return Number(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
