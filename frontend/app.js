// Configuration de base de l'URL de l'API
const API_BASE = "http://localhost:8000"; // à adapter si nécessaire

// Helpers DOM
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

function showScreen(id) {
  $$(".screen").forEach((el) => el.classList.remove("active"));
  $("#" + id).classList.add("active");
}

function showTab(id) {
  $$(".tab").forEach((el) => el.classList.remove("active"));
  $("#" + id).classList.add("active");

  $$(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === id.replace("tab-", ""));
  });
}

// Événements de base
window.addEventListener("DOMContentLoaded", () => {
  const btnStart = $("#btn-start");
  const navItems = $$(".nav-item");

  if (btnStart) {
    btnStart.addEventListener("click", () => {
      showScreen("dashboard");
      showTab("tab-home");
      loadHistory();
    });
  }

  navItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.tab;
      showTab("tab-" + tab);
      if (tab === "history") {
        loadHistory();
      }
    });
  });

  // Historique → Export
  const btnGoExport = $("#btn-go-export");
  if (btnGoExport) {
    btnGoExport.addEventListener("click", () => {
      const id = btnGoExport.dataset.recordId;
      if (id) {
        $("#export-record-id").value = id;
      }
      showTab("tab-export");
    });
  }

  // Bouton export
  const btnExport = $("#btn-export");
  if (btnExport) {
    btnExport.addEventListener("click", onExportClick);
  }

  // Bouton traduction avec le modèle perso
  const btnCustomTranslate = $("#btn-custom-translate");
  if (btnCustomTranslate) {
    btnCustomTranslate.addEventListener("click", onCustomTranslateClick);
  }
});

// Chargement de l'historique
async function loadHistory() {
  const listEl = $("#history-list");
  const detailEl = $("#history-detail");
  if (!listEl) return;

  listEl.innerHTML = "Chargement...";

  try {
    const res = await fetch(`${API_BASE}/history`);
    if (!res.ok) throw new Error(await res.text());
    const items = await res.json();

    if (!items.length) {
      listEl.innerHTML = "Aucun historique disponible.";
      if (detailEl) detailEl.classList.add("hidden");
      return;
    }

    listEl.innerHTML = "";
    items.forEach((item) => {
      const div = document.createElement("div");
      div.className = "history-item";
      div.innerHTML = `
        <div class="history-item-title">[#${item.id}] ${item.audio_path}</div>
        <div class="history-item-meta">${item.timestamp} — Langue: ${item.detected_lang || "?"}</div>
      `;
      div.addEventListener("click", () => onHistoryItemClick(item.id));
      listEl.appendChild(div);
    });
  } catch (err) {
    console.error(err);
    listEl.innerHTML = "Erreur lors du chargement de l'historique.";
  }
}

async function onHistoryItemClick(id) {
  const detailEl = $("#history-detail");
  const statusEl = $("#history-list");
  if (!detailEl) return;

  statusEl && (statusEl.innerHTML += "\nChargement du détail...");

  try {
    const res = await fetch(`${API_BASE}/history/${id}`);
    if (!res.ok) throw new Error(await res.text());
    const rec = await res.json();

    $("#detail-audio-path").textContent = rec.audio_path;
    $("#detail-timestamp").textContent = rec.timestamp;
    $("#detail-lang").textContent = rec.detected_lang || "?";
    $("#detail-original").textContent = rec.original_text || "";
    $("#detail-translated").textContent = rec.translated_text || "";

    const btnGoExport = $("#btn-go-export");
    if (btnGoExport) {
      btnGoExport.dataset.recordId = rec.id;
    }

    detailEl.classList.remove("hidden");
  } catch (err) {
    console.error(err);
  }
}

// Export
async function onExportClick() {
  const idEl = $("#export-record-id");
  const formatEl = $("#export-format");
  const statusEl = $("#export-status");
  if (!idEl || !formatEl || !statusEl) return;

  const id = parseInt(idEl.value, 10);
  const format = formatEl.value;

  if (!id) {
    statusEl.textContent = "Veuillez saisir un ID d'enregistrement valide.";
    return;
  }

  statusEl.textContent = "Préparation du téléchargement...";

  const url = `${API_BASE}/export/${id}?format=${encodeURIComponent(format)}`;

  // Ouvre le téléchargement dans un nouvel onglet
  window.open(url, "_blank");
  statusEl.textContent = "Si tout va bien, le téléchargement doit commencer.";
}

// Traduction via le modèle personnalisé
async function onCustomTranslateClick() {
  const textEl = $("#custom-text");
  const resultEl = $("#custom-result");
  if (!textEl || !resultEl) return;

  const text = textEl.value.trim();
  if (!text) {
    resultEl.textContent = "Veuillez saisir un texte.";
    return;
  }

  resultEl.textContent = "Traduction en cours...";

  try {
    const res = await fetch(`${API_BASE}/translate/custom`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }), // model_dir lu côté serveur via CUSTOM_TRANSLATION_MODEL_DIR
    });
    if (!res.ok) {
      const msg = await res.text();
      throw new Error(msg || "Erreur HTTP");
    }
    const data = await res.json();
    resultEl.textContent = data.translated_text || "(aucune sortie)";
  } catch (err) {
    console.error(err);
    resultEl.textContent = "Erreur lors de la traduction avec le modèle personnalisé.";
  }
}
