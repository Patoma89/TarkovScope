/* =====================================================================
   TTC v2.0 Next-Gen — Controlador Frontend (pywebview API Bridge)
   ===================================================================== */

const RING_CIRCUMFERENCE = 2 * Math.PI * 29; // r=29 => 182.21

const PHASE_INFO = {
  maps: { phase: "FASE 2 · INCURSIÓN", title: "Mapas 2D Interactivos (GPU Zoom/Pan)", desc: "Planos topográficos HD con capas de extracciones, llaves, spawns de bosses y tus pines personales guardados en SQLite." },
  bosses: { phase: "FASE 2 · INCURSIÓN", title: "Bosses, Spawns PvE/PvP & Facciones IA", desc: "Radar de los 12 Bosses con sincronización en vivo de eftboss.com, zonas de spawn y dossier de las 6 facciones IA." },
  keys: { phase: "FASE 2 · INCURSIÓN", title: "Llaves, Keycards & Marked Rooms", desc: "Catálogo de 230+ llaves con miniaturas oficiales y tu checklist personal de llavero." },
  quests: { phase: "FASE 3 · PROGRESIÓN", title: "Quests, Tracker de Rutas & Planner", desc: "Las 459 misiones de los 11 Traders, Dossier Wiki Offline, rutas óptimas multi-quest y Planner de progresión." },
  weapons: { phase: "FASE 4 · COMBATE", title: "Armería, Gunsmith & Modding Studio Pro", desc: "110 armas reales, Workbench interactivo con cálculo de stats, exportación JSON/Base64 y guía de Averías." },
  ballistics: { phase: "FASE 4 · COMBATE", title: "Balística (203 Balas), Duelo STK & Blindajes", desc: "Matriz completa sincronizada con eft-ammo.com, simulador de disparos para matar y catálogo de placas/cascos." },
  flea: { phase: "FASE 5 · ECONOMÍA", title: "Hideout, Trueques (Barters), Cultist Circle & FiR", desc: "Progresión correlativa del Hideout (68 niveles), Collector Kappa, crafteos FiR y recetas del Círculo Cultista." },
  medical: { phase: "FASE 5 · ECONOMÍA", title: "Medicina, Stims, 45 Provisiones & Salud", desc: "Catálogo médico completo, provisiones con buffs y matriz de los 14 efectos de salud." },
  pmc_systems: { phase: "FASE 5 · ECONOMÍA", title: "PMC, 35 Skills, Prestigio 1-6, Logros & Lore", desc: "Skills con perks Élite, Scav Karma, BTR & Transits, Prestige 1-6, 32 Achievements y Ropa Táctica." },
};

const state = {
  bootstrap: null,
  cc: null,
  kappaFilter: "pending", // "pending" | "all"
  activeTab: "command_center",
  searchDebounce: null,
};

function hexToRgbTuple(hex) {
  const clean = (hex || "#D4B886").replace("#", "");
  const num = parseInt(clean.length === 3 ? clean.split("").map(c => c + c).join("") : clean, 16);
  return `${(num >> 16) & 255}, ${(num >> 8) & 255}, ${num & 255}`;
}

function showToast(msg) {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove("show"), 2400);
}

function applySkinPalette(skinId, palette) {
  if (!palette) return;
  const r = document.documentElement.style;
  r.setProperty("--bg-dark", palette.bg_dark || "#090c12");
  r.setProperty("--bg-darkest", palette.bg_darkest || "#06080d");
  r.setProperty("--bg-deep", palette.bg_deep || "#0c1018");
  r.setProperty("--bg-card", palette.bg_card || "#121722");
  r.setProperty("--bg-card-glass", `rgba(${hexToRgbTuple(palette.bg_card || "#121722")}, 0.80)`);
  r.setProperty("--bg-card-hover", palette.bg_card_hover || "#1a2130");
  r.setProperty("--btn-surface", palette.btn_surface || "#171d2a");
  r.setProperty("--btn-hover", palette.btn_hover || "#212a3d");
  r.setProperty("--border", palette.border || "#252e40");
  r.setProperty("--text-main", palette.text_main || "#f8fafc");
  r.setProperty("--text-soft", palette.text_soft || "#e2e8f0");
  r.setProperty("--text-muted", palette.text_muted || "#94a3b8");
  r.setProperty("--text-dim", palette.text_dim || "#64748b");
  r.setProperty("--accent-gold", palette.accent_gold || "#d4b886");
  r.setProperty("--accent-gold-rgb", hexToRgbTuple(palette.accent_gold || "#d4b886"));
  r.setProperty("--accent-orange", palette.accent_orange || "#e5732f");
  r.setProperty("--accent-blue", palette.accent_blue || "#38bdf8");
  r.setProperty("--accent-emerald", palette.emerald || "#10b981");
  r.setProperty("--accent-amber", palette.accent_yellow || "#f59e0b");

  const hudSel = document.getElementById("hud-skin-select");
  if (hudSel && hudSel.value !== skinId) hudSel.value = skinId;
}

function setRing(ringId, pctId, pct) {
  const ring = document.getElementById(ringId);
  const pctEl = document.getElementById(pctId);
  const clamped = Math.max(0, Math.min(100, Number(pct) || 0));
  if (ring) {
    ring.style.strokeDasharray = `${RING_CIRCUMFERENCE}`;
    ring.style.strokeDashoffset = `${RING_CIRCUMFERENCE * (1 - clamped / 100)}`;
  }
  if (pctEl) pctEl.textContent = `${clamped}%`;
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCommandCenter(cc) {
  if (!cc) return;
  state.cc = cc;
  const k = cc.kpis;

  // KPIs + Anillos SVG
  document.getElementById("kpi-quests-num").textContent = `${k.quests.done}/${k.quests.total}`;
  document.getElementById("kpi-q-unlocked").textContent = `${k.quests.unlocked} disponibles`;
  setRing("ring-quests", "ring-quests-pct", k.quests.pct);

  document.getElementById("kpi-kappa-num").textContent = `${k.kappa.done}/${k.kappa.total}`;
  document.getElementById("kpi-k-missing").textContent = `${k.kappa.missing} pendientes`;
  setRing("ring-kappa", "ring-kappa-pct", k.kappa.pct);

  document.getElementById("kpi-hideout-num").textContent = `${k.hideout.done}/${k.hideout.total}`;
  document.getElementById("kpi-h-ready").textContent = `${k.hideout.ready} listas`;
  setRing("ring-hideout", "ring-hideout-pct", k.hideout.pct);

  document.getElementById("kpi-ach-num").textContent = `${k.achievements.done}/${k.achievements.total}`;
  document.getElementById("kpi-p-lvl").textContent = `P${k.achievements.prestige}`;
  const pChip = document.getElementById("hud-prestige-chip");
  if (pChip) pChip.textContent = `P${k.achievements.prestige}`;
  setRing("ring-ach", "ring-ach-pct", k.achievements.pct);

  // Próximas Misiones Disponibles
  const qList = document.getElementById("next-quests-list");
  if (!cc.next_quests.length) {
    qList.innerHTML = `<div style="padding:24px;text-align:center;color:var(--accent-emerald);font-weight:700">¡Todas las misiones desbloqueadas están completas!</div>`;
  } else {
    qList.innerHTML = cc.next_quests.map(q => `
      <div class="quest-row">
        <img class="trader-avatar" src="${escapeHtml(q.trader_avatar)}" alt="${escapeHtml(q.trader_name)}" loading="lazy" />
        <div class="quest-info">
          <div class="quest-title">${escapeHtml(q.title)}</div>
          <div class="quest-meta">
            <span>${escapeHtml(q.trader_name)}</span>
            <span>•</span>
            <span>📍 ${escapeHtml(q.primary_map)}</span>
            <span>•</span>
            <span>Nv.${q.level_req}</span>
          </div>
        </div>
        <div class="quest-badges">
          ${q.exp ? `<span class="xp-tag">+${q.exp.toLocaleString("es-AR")} XP</span>` : ""}
          ${q.is_kappa ? `<span class="kappa-tag">Kappa</span>` : ""}
          ${q.is_lightkeeper ? `<span class="kappa-tag" style="color:var(--accent-blue);border-color:rgba(56,189,248,.4);background:rgba(56,189,248,.12)">LK</span>` : ""}
          <button class="btn-check-quest" data-quest-id="${q.id}" title="Marcar completada">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><polyline points="20 6 9 17 4 12"/></svg>
          </button>
        </div>
      </div>
    `).join("");

    qList.querySelectorAll(".btn-check-quest").forEach(btn => {
      btn.addEventListener("click", async () => {
        const qid = Number(btn.dataset.questId);
        const res = await window.pywebview.api.toggle_quest(qid);
        if (res && res.ok) {
          renderCommandCenter(res.command_center);
          showToast("✓ Misión marcada como completada");
        }
      });
    });
  }

  renderKappaGrid();

  // Paneles Operativos Adicionales del Centro de Mando
  const bossesEl = document.getElementById("cc-bosses-list");
  if (bossesEl) {
    bossesEl.innerHTML = (cc.bosses_radar || []).map(b => `
      <div class="cc-mini-row">
        <img src="${escapeHtml(b.avatar_url)}" alt="${escapeHtml(b.name)}" loading="lazy" />
        <div style="flex:1;min-width:0">
          <div style="font-weight:700;color:var(--text-main);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${escapeHtml(b.name)}</div>
          <div style="font-size:10.5px;color:var(--text-muted)">${escapeHtml(b.maps)}</div>
        </div>
        <span style="font-family:var(--font-mono);font-size:11px;font-weight:800;color:var(--accent-emerald)">${escapeHtml(b.pve_chance || b.pvp_chance)}</span>
      </div>
    `).join("");
  }

  const hideoutEl = document.getElementById("cc-hideout-list");
  if (hideoutEl) {
    const hList = cc.hideout_ready_list || [];
    hideoutEl.innerHTML = hList.length
      ? hList.map(m => `
          <div class="cc-mini-row">
            <div style="flex:1;min-width:0">
              <div style="font-weight:700;color:var(--text-main);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${escapeHtml(m.station)}</div>
              <div style="font-size:10.5px;color:var(--text-muted)">${m.reqs_count} requisitos</div>
            </div>
            <span class="kappa-tag" style="color:var(--accent-blue);border-color:rgba(56,189,248,.4);background:rgba(56,189,248,.12)">Nv.${m.level}</span>
          </div>
        `).join("")
      : `<div style="padding:18px;text-align:center;color:var(--accent-emerald);font-weight:700;font-size:12px">✓ ¡Refugio al máximo!</div>`;
  }

  const keysEl = document.getElementById("cc-keys-list");
  const keysBadge = document.getElementById("cc-keys-badge");
  if (keysEl && cc.missing_quest_keys) {
    const mk = cc.missing_quest_keys;
    if (keysBadge) keysBadge.textContent = `${mk.owned}/${mk.total} →`;
    const kItems = mk.items || [];
    keysEl.innerHTML = kItems.length
      ? kItems.map(it => `
          <div class="cc-mini-row">
            <div style="flex:1;min-width:0">
              <div style="font-weight:700;color:var(--accent-gold);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${escapeHtml(it.name)}</div>
              <div style="font-size:10.5px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${escapeHtml(it.map)} · ${escapeHtml(it.quest)}</div>
            </div>
          </div>
        `).join("")
      : `<div style="padding:18px;text-align:center;color:var(--accent-emerald);font-weight:700;font-size:12px">🔑 ¡Todas las llaves de quest completas!</div>`;
  }

  const campEl = document.getElementById("cc-campaign-box");
  if (campEl && cc.campaign_progress) {
    const st = cc.campaign_progress.story || {};
    const gs = cc.campaign_progress.gunsmith || {};
    campEl.innerHTML = `
      <div class="cc-mini-row clickable-card" data-goto="quests" style="flex-direction:column;align-items:stretch;gap:3px;padding:10px">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <strong style="color:var(--accent-gold)">📖 Historia (10 Capítulos)</strong>
          <span style="font-family:var(--font-mono);font-size:11px;color:var(--accent-emerald);font-weight:800">${st.done || 0}/${st.total || 0} (${st.pct || 0}%)</span>
        </div>
        <div class="cc-progress-bar"><div class="cc-progress-fill" style="width:${st.pct || 0}%"></div></div>
        <div style="font-size:11px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">Siguiente: ${escapeHtml(st.next || "")}</div>
      </div>
      <div class="cc-mini-row clickable-card" data-goto="weapons" style="flex-direction:column;align-items:stretch;gap:3px;padding:10px">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <strong style="color:var(--accent-blue)">🔧 Gunsmith (Mechanic)</strong>
          <span style="font-family:var(--font-mono);font-size:11px;color:var(--accent-gold);font-weight:800">${gs.done || 0}/${gs.total || 25} (${gs.pct || 0}%)</span>
        </div>
        <div class="cc-progress-bar"><div class="cc-progress-fill" style="width:${gs.pct || 0}%;background:linear-gradient(90deg, var(--accent-blue), var(--accent-gold))"></div></div>
        <div style="font-size:11px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">Siguiente: ${escapeHtml(gs.next || "")}</div>
      </div>
    `;
    campEl.querySelectorAll("[data-goto]").forEach(el => {
      el.addEventListener("click", (e) => {
        e.stopPropagation();
        switchTab(el.dataset.goto);
      });
    });
  }

  renderPreRaidChecklist(cc.preraid_checklist || []);
}

function renderPreRaidChecklist(items) {
  const listEl = document.getElementById("cc-preraid-list");
  const countEl = document.getElementById("cc-preraid-count");
  if (!listEl) return;

  const list = Array.isArray(items) ? items : [];
  if (state.cc) state.cc.preraid_checklist = list;
  const done = list.filter(it => it.checked).length;
  const total = list.length;

  if (countEl) {
    countEl.textContent = total > 0 && done === total ? `✓ ${done}/${total}` : `${done}/${total}`;
    countEl.classList.toggle("ready", total > 0 && done === total);
  }

  const isEn = window.TTC_LANG === "en";
  listEl.innerHTML = list.map(it => {
    const label = isEn ? (it.label_en || it.label_es) : (it.label_es || it.label_en);
    return `
      <div class="preraid-item ${it.checked ? "checked" : ""}" data-preraid-id="${escapeHtml(it.id)}">
        <span class="preraid-box">✓</span>
        <span class="preraid-label" title="${escapeHtml(label)}">${escapeHtml(label)}</span>
        ${it.custom ? `<button class="preraid-del" data-preraid-del="${escapeHtml(it.id)}" title="${isEn ? "Remove item" : "Eliminar ítem"}">×</button>` : ""}
      </div>
    `;
  }).join("");

  listEl.querySelectorAll(".preraid-item").forEach(row => {
    row.addEventListener("click", async () => {
      const id = row.dataset.preraidId;
      const res = await window.pywebview.api.toggle_preraid_item(id);
      if (res && res.ok) renderPreRaidChecklist(res.preraid_checklist);
    });
  });

  listEl.querySelectorAll("[data-preraid-del]").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const res = await window.pywebview.api.remove_preraid_item(btn.dataset.preraidDel);
      if (res && res.ok) renderPreRaidChecklist(res.preraid_checklist);
    });
  });
}

function renderKappaGrid() {
  const grid = document.getElementById("kappa-items-grid");
  const all = state.cc?.kappa_items || [];
  const items = state.kappaFilter === "pending" ? all.filter(i => !i.collected) : all;

  if (!items.length) {
    grid.innerHTML = `<div style="grid-column:1/-1;padding:28px;text-align:center;color:var(--accent-emerald);font-weight:700">🏆 ¡Tienes todos los 44 ítems Collector (Kappa) en tu alijo!</div>`;
    return;
  }

  grid.innerHTML = items.map(it => `
    <div class="kappa-tile ${it.collected ? "collected" : ""}" title="${escapeHtml(it.boss_or_spot)}">
      <img class="kappa-img" src="${escapeHtml(it.icon_url)}" alt="${escapeHtml(it.name)}" loading="lazy" />
      <div class="kappa-name">${escapeHtml(it.name)}</div>
      <div class="kappa-footer">
        <span class="kappa-count">${it.collected ? "1/1" : "0/1"}</span>
        <button class="btn-stash" data-kappa-name="${escapeHtml(it.name)}">${it.collected ? "✓ Alijo" : "+1 Alijo"}</button>
      </div>
    </div>
  `).join("");

  grid.querySelectorAll(".btn-stash").forEach(btn => {
    btn.addEventListener("click", async () => {
      const name = btn.dataset.kappaName;
      const res = await window.pywebview.api.toggle_kappa_item(name);
      if (res && res.ok) {
        renderCommandCenter(res.command_center);
        showToast(res.collected ? `✓ ${name} agregado al alijo` : `↩ ${name} quitado del alijo`);
      }
    });
  });
}

/* ================= RELOJ IN-RAID DE TARKOV (7x EN VIVO) ================= */
function updateRaidClock() {
  const DAY_MS = 86400000;
  const tarkovMs = Date.now() * 7;
  const leftMs = (tarkovMs + 3 * 3600000) % DAY_MS;
  const rightMs = (leftMs + 12 * 3600000) % DAY_MS;

  const fmt = (ms) => {
    const s = Math.floor(ms / 1000) % 86400;
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    return {
      h,
      str: `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`,
      isNight: h >= 22 || h < 7,
      pct: (s / 86400) * 100,
    };
  };

  const L = fmt(leftMs);
  const R = fmt(rightMs);
  const cultists = L.isNight || R.isNight;

  document.getElementById("hud-clock-left").textContent = L.str;
  document.getElementById("hud-clock-right").textContent = R.str;
  document.getElementById("card-clock-left").textContent = L.str;
  document.getElementById("card-clock-right").textContent = R.str;

  const thumb = document.getElementById("daynight-thumb");
  if (thumb) thumb.style.left = `${L.pct.toFixed(1)}%`;

  const hudTag = document.getElementById("hud-cultist-tag");
  const cardBanner = document.getElementById("card-cultist-banner");
  if (cultists) {
    const side = L.isNight ? `IZQ (${L.str.slice(0, 5)})` : `DER (${R.str.slice(0, 5)})`;
    hudTag.textContent = "CULTISTS ACTIVOS";
    hudTag.style.color = "var(--accent-amber)";
    cardBanner.textContent = `🌙 CULTISTS ACTIVOS EN ${side} (22:00–07:00)`;
    cardBanner.classList.remove("day");
  } else {
    hudTag.textContent = "DÍA DESPEJADO";
    hudTag.style.color = "var(--accent-blue)";
    cardBanner.textContent = "☀️ HORARIO DIURNO — SIN VENTANA CULTISTS";
    cardBanner.classList.add("day");
  }
}

/* ================= NAVEGACIÓN ================= */
window.renderCommandCenter = renderCommandCenter;

async function switchTab(tabKey) {
  const aliasMap = {
    quest_tracker: "quests",
    progression_planner: "quests",
    story_quests: "quests",
  };
  const resolved = aliasMap[tabKey] || tabKey;
  state.activeTab = resolved;

  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.tab === resolved);
  });

  const ccSec = document.getElementById("view-command_center");
  const kbSec = document.getElementById("view-kord_breach");
  const dynSec = document.getElementById("view-dynamic");
  const scroll = document.getElementById("content-scroll");
  if (scroll) scroll.scrollTop = 0;

  if (resolved === "command_center") {
    ccSec.style.display = "block";
    if (kbSec) kbSec.style.display = "none";
    dynSec.style.display = "none";
    return;
  }

  if (resolved === "season_docs" && kbSec) {
    ccSec.style.display = "none";
    dynSec.style.display = "none";
    kbSec.style.display = "block";
    if (!kbSec.dataset.mounted && window.TTCViews?.renderSeasonDocsView) {
      kbSec.dataset.mounted = "1";
      await window.TTCViews.renderSeasonDocsView(kbSec);
    }
    return;
  }

  ccSec.style.display = "none";
  if (kbSec) kbSec.style.display = "none";
  dynSec.style.display = "block";
  dynSec.innerHTML = `<div style="padding:36px;text-align:center;color:var(--text-muted)">Cargando módulo…</div>`;

  const V = window.TTCViews || {};
  try {
    if (resolved === "maps" && V.renderMapsView) await V.renderMapsView(dynSec);
    else if (resolved === "bosses" && V.renderBossesView) await V.renderBossesView(dynSec);
    else if (resolved === "keys" && V.renderKeysView) await V.renderKeysView(dynSec);
    else if (resolved === "quests" && V.renderQuestsView) await V.renderQuestsView(dynSec);
    else if (resolved === "season_docs" && V.renderSeasonDocsView) await V.renderSeasonDocsView(dynSec);
    else if (resolved === "weapons" && V.renderWeaponsView) await V.renderWeaponsView(dynSec);
    else if (resolved === "ballistics" && V.renderBallisticsView) await V.renderBallisticsView(dynSec);
    else if (resolved === "flea" && V.renderFleaView) await V.renderFleaView(dynSec);
    else if (resolved === "containers" && V.renderContainersView) await V.renderContainersView(dynSec);
    else if (resolved === "medical" && V.renderMedicalView) await V.renderMedicalView(dynSec);
    else if (resolved === "pmc_systems" && V.renderPMCView) await V.renderPMCView(dynSec);
    else if (resolved === "lore" && V.renderLoreView) await V.renderLoreView(dynSec);
  } catch (err) {
    console.error("View render error:", err);
    dynSec.innerHTML = `<div class="glass-card panel-card" style="color:var(--accent-red)">Error cargando vista: ${escapeHtml(err?.message || err)}</div>`;
  }
}

/* ================= SPOTLIGHT CTRL+K ================= */
function openSpotlight() {
  const modal = document.getElementById("modal-spotlight");
  const input = document.getElementById("spotlight-input");
  modal.classList.add("open");
  input.value = "";
  input.focus();
  document.getElementById("spotlight-results").innerHTML =
    `<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:12.5px">Escribe al menos 2 caracteres para buscar en todo el catálogo offline…</div>`;
}

function closeModals() {
  document.querySelectorAll(".modal-backdrop").forEach(m => m.classList.remove("open"));
}

async function runSpotlightSearch(q) {
  const container = document.getElementById("spotlight-results");
  if (!q || q.trim().length < 2) {
    container.innerHTML = `<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:12.5px">Escribe al menos 2 caracteres…</div>`;
    return;
  }
  const results = await window.pywebview.api.global_search(q.trim());
  if (!results || !results.length) {
    container.innerHTML = `<div style="padding:24px;text-align:center;color:var(--text-muted)">Sin resultados para "${escapeHtml(q)}"</div>`;
    return;
  }
  container.innerHTML = results.map(r => `
    <div class="search-row" data-tab="${escapeHtml(r.tab || "command_center")}">
      <span class="search-cat" style="background:${escapeHtml(r.badge_color || "#334155")}">${escapeHtml(r.category || "TTC")}</span>
      <div class="search-main">
        <div class="search-title">${escapeHtml(r.title)}</div>
        <div class="search-sub">${escapeHtml(r.subtitle || "")}</div>
      </div>
    </div>
  `).join("");

  container.querySelectorAll(".search-row").forEach(row => {
    row.addEventListener("click", () => {
      closeModals();
      switchTab(row.dataset.tab);
    });
  });
}

/* ================= PATCH NOTES, SKINS & LIGHTBOX ================= */
function initSkinSelector() {
  const hudSel = document.getElementById("hud-skin-select");
  const list = state.bootstrap?.skins_meta || [];
  const active = state.bootstrap?.skin_id || "tarkov_classic";
  if (!hudSel) return;

  hudSel.innerHTML = list.map(s => `<option value="${escapeHtml(s.id)}" ${s.id === active ? "selected" : ""}>🎨 ${escapeHtml(s.label)}</option>`).join("");
  hudSel.onchange = async () => {
    const sid = hudSel.value;
    const res = await window.pywebview.api.set_skin(sid);
    if (res && res.ok) {
      state.bootstrap.skin_id = sid;
      applySkinPalette(sid, res.palette);
      showToast(`🎨 Skin: ${list.find(x => x.id === sid)?.label || sid}`);
    }
  };
}

const _lbState = { scale: 1, tx: 0, ty: 0, dragging: false, sx: 0, sy: 0 };

function _applyLightboxTransform() {
  const img = document.getElementById("lightbox-img");
  const lbl = document.getElementById("lb-zoom-lbl");
  if (img) img.style.transform = `translate(${_lbState.tx}px, ${_lbState.ty}px) scale(${_lbState.scale})`;
  if (lbl) lbl.textContent = `${Math.round(_lbState.scale * 100)}%`;
}

window.openImageLightbox = function (src, title, subtitle) {
  if (!src) return;
  const modal = document.getElementById("modal-lightbox");
  const img = document.getElementById("lightbox-img");
  const tEl = document.getElementById("lightbox-title");
  const sEl = document.getElementById("lightbox-sub");
  if (!modal || !img) return;
  img.src = src;
  if (tEl) tEl.textContent = title || "VISOR TÁCTICO";
  if (sEl) sEl.textContent = subtitle || "Rueda del mouse para hacer zoom · Arrastra para mover · ESC para cerrar";
  _lbState.scale = 1;
  _lbState.tx = 0;
  _lbState.ty = 0;
  _applyLightboxTransform();
  modal.classList.add("open");
};

function setupLightboxControls() {
  const stage = document.getElementById("lightbox-stage");
  const btnIn = document.getElementById("lb-zoom-in");
  const btnOut = document.getElementById("lb-zoom-out");
  const btnReset = document.getElementById("lb-zoom-reset");
  const btnClose = document.getElementById("btn-close-lightbox");
  if (!stage) return;

  btnIn?.addEventListener("click", () => { _lbState.scale = Math.min(4.5, _lbState.scale * 1.25); _applyLightboxTransform(); });
  btnOut?.addEventListener("click", () => { _lbState.scale = Math.max(0.5, _lbState.scale / 1.25); _applyLightboxTransform(); });
  btnReset?.addEventListener("click", () => { _lbState.scale = 1; _lbState.tx = 0; _lbState.ty = 0; _applyLightboxTransform(); });
  btnClose?.addEventListener("click", closeModals);

  stage.addEventListener("wheel", (e) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    _lbState.scale = Math.max(0.5, Math.min(4.5, _lbState.scale * factor));
    _applyLightboxTransform();
  }, { passive: false });

  stage.addEventListener("mousedown", (e) => {
    _lbState.dragging = true;
    _lbState.sx = e.clientX - _lbState.tx;
    _lbState.sy = e.clientY - _lbState.ty;
  });
  window.addEventListener("mousemove", (e) => {
    if (!_lbState.dragging) return;
    _lbState.tx = e.clientX - _lbState.sx;
    _lbState.ty = e.clientY - _lbState.sy;
    _applyLightboxTransform();
  });
  window.addEventListener("mouseup", () => { _lbState.dragging = false; });
}

async function openPatchNotes() {
  const modal = document.getElementById("modal-notes");
  const titleEl = document.getElementById("notes-modal-title");
  const body = document.getElementById("notes-body");
  modal.classList.remove("modal-dossier");
  if (titleEl) {
    titleEl.textContent = (window.TTC_LANG === "en") ? "PATCH NOTES — TTC" : "NOTAS DE VERSIÓN — TTC";
  }
  modal.classList.add("open");
  const notes = await window.pywebview.api.get_patch_notes(state.bootstrap?.lang || "es");
  body.innerHTML = (notes || []).map(rel => `
    <div class="glass-card" style="padding:12px 14px">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
        <strong style="color:var(--accent-gold);font-size:14px">v${escapeHtml(rel.version)}</strong>
        <span style="color:var(--text-soft);font-size:12.5px;font-weight:600">${escapeHtml(rel.title)}</span>
      </div>
      <div style="display:flex;flex-direction:column;gap:5px">
        ${(rel.items || []).map(it => `
          <div style="font-size:12px;color:var(--text-muted);line-height:1.4">
            <span style="color:var(--accent-emerald);font-weight:800;margin-right:6px">[${escapeHtml(it.kind)}]</span>${escapeHtml(it.text)}
          </div>
        `).join("")}
      </div>
    </div>
  `).join("");
}

/* ================= I18N (ES / EN EN VIVO) ================= */
const I18N_UI = {
  es: {
    nav_overview: "Vista General",
    tab_cc: "Centro de Mando",
    nav_raid: "Incursión & Mapas",
    tab_maps: "Mapas 2D",
    tab_bosses: "Bosses & IA",
    tab_keys: "Llaves & Intel",
    nav_prog: "Progresión",
    tab_quests: "Quests & Rutas",
    tab_season_docs: "Kord Breach",
    nav_combat: "Combate",
    tab_weapons: "Armería & Gunsmith",
    tab_ballistics: "Balística & Blindaje",
    nav_econ: "Economía & PMC",
    tab_flea: "Hideout & Flea",
    tab_containers: "Contenedores & Rigs",
    tab_medical: "Médico & Comida",
    tab_pmc: "PMC, Skills & Logros",
    nav_extras: "Extras",
    tab_lore: "Lore & Universo",
    btn_socials: "Redes",
    hud_search: "Buscar quests, munición, llaves, bosses...",
    hud_pmc_lvl: "PMC Nv.",
    cc_hero_html: `CENTRO DE MANDO <span>TÁCTICO</span>`,
    cc_hero_sub: "Estado operativo de incursión, progreso Kappa y logística de refugio en tiempo real.",
    btn_plan_raid: "Planear Raid Óptima",
    cc_preraid_title: "✅ Checklist Pre-Raid",
  },
  en: {
    nav_overview: "Overview",
    tab_cc: "Command Center",
    nav_raid: "Raid & Maps",
    tab_maps: "2D Maps",
    tab_bosses: "Bosses & AI",
    tab_keys: "Keys & Intel",
    nav_prog: "Progression",
    tab_quests: "Quests & Routes",
    tab_season_docs: "Kord Breach",
    nav_combat: "Combat",
    tab_weapons: "Armory & Gunsmith",
    tab_ballistics: "Ballistics & Armor",
    nav_econ: "Economy & PMC",
    tab_flea: "Hideout & Flea",
    tab_containers: "Containers & Rigs",
    tab_medical: "Medical & Food",
    tab_pmc: "PMC, Skills & Achievements",
    nav_extras: "Extras",
    tab_lore: "Lore & Universe",
    btn_socials: "Socials",
    hud_search: "Search quests, ammo, keys, bosses...",
    hud_pmc_lvl: "PMC Lv.",
    cc_hero_html: `TACTICAL <span>COMMAND CENTER</span>`,
    cc_hero_sub: "Live raid status, Kappa Collector progress and Hideout logistics in real time.",
    btn_plan_raid: "Plan Optimal Raid",
    cc_preraid_title: "✅ Pre-Raid Checklist",
  },
};

function applyLanguage(lang) {
  const clean = lang === "en" ? "en" : "es";
  window.TTC_LANG = clean;
  document.documentElement.lang = clean;
  const dict = I18N_UI[clean];
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    if (dict[key]) el.textContent = dict[key];
  });
  const hero = document.getElementById("cc-hero-title");
  if (hero && dict.cc_hero_html) hero.innerHTML = dict.cc_hero_html;
  const langBtn = document.getElementById("btn-lang-toggle");
  if (langBtn) langBtn.textContent = clean.toUpperCase();
  const spotIn = document.getElementById("spotlight-input");
  if (spotIn) {
    spotIn.placeholder = clean === "en"
      ? "Search quests, ammo (M80A1, BP), keys, bosses, barters..."
      : "Buscar quests, balas (M80A1, BP), llaves, bosses, barters...";
  }
  const preIn = document.getElementById("preraid-add-input");
  if (preIn) {
    preIn.placeholder = clean === "en" ? "Add quick item…" : "Añadir ítem rápido…";
  }
  const pinBtn = document.getElementById("btn-pin-top");
  if (pinBtn) {
    pinBtn.title = clean === "en"
      ? "Always on top · Global hotkey: Ctrl+Alt+T"
      : "Siempre encima · Atajo global: Ctrl+Alt+T";
  }
  if (state.cc?.preraid_checklist) {
    renderPreRaidChecklist(state.cc.preraid_checklist);
  }
}

/* ================= ACTUALIZADOR GITHUB ================= */
async function openGitHubUpdater() {
  const modal = document.getElementById("modal-update");
  const body = document.getElementById("update-body");
  if (!modal || !body) return;
  modal.classList.add("open");
  body.innerHTML = `<div style="padding:18px;text-align:center;color:var(--text-muted)">⏳ Consultando última Release en GitHub (Patoma89/TarkovScope)…</div>`;

  const res = await window.pywebview.api.check_github_update();
  if (!res || !res.ok) {
    body.innerHTML = `
      <div class="info-box" style="color:var(--accent-red)">⚠️ No se pudo conectar con GitHub: ${escapeHtml(res?.error || "Sin conexión")}</div>
      <button class="btn-ghost-sm" id="upd-open-gh">Abrir GitHub Releases ↗</button>
    `;
    body.querySelector("#upd-open-gh")?.addEventListener("click", () => window.pywebview.api.open_external_url(res?.release_url || "https://github.com/Patoma89/TarkovScope/releases"));
    return;
  }

  const statusHtml = res.has_update
    ? `<div class="info-box" style="border-color:var(--accent-emerald);color:var(--accent-emerald);font-weight:800">🚀 ¡Nueva versión disponible: ${escapeHtml(res.latest_version)}! (Actual: v${escapeHtml(res.current_version)})</div>`
    : `<div class="info-box" style="border-color:var(--accent-blue);color:var(--accent-blue);font-weight:700">✓ Estás al día — Versión instalada: v${escapeHtml(res.current_version)} (Última en GitHub: ${escapeHtml(res.latest_version)})</div>`;

  body.innerHTML = `
    ${statusHtml}
    ${res.notes ? `<div class="info-box" style="max-height:240px;overflow-y:auto;white-space:pre-wrap;font-size:12px;color:var(--text-muted);line-height:1.5">${escapeHtml(res.notes)}</div>` : ""}
    <div style="display:flex;gap:10px;justify-content:flex-end;flex-wrap:wrap">
      <button class="btn-ghost-sm" id="upd-open-gh">Ver en GitHub ↗</button>
      ${res.installer_url ? `<button class="btn-primary-gold" id="upd-download-run">⬇️ Descargar e Instalar (${escapeHtml(res.installer_name || "Setup.exe")})</button>` : ""}
    </div>
  `;

  body.querySelector("#upd-open-gh")?.addEventListener("click", () => window.pywebview.api.open_external_url(res.release_url));
  const dlBtn = body.querySelector("#upd-download-run");
  if (dlBtn) {
    dlBtn.addEventListener("click", async () => {
      dlBtn.disabled = true;
      dlBtn.textContent = "⏳ Descargando instalador…";
      const dl = await window.pywebview.api.download_and_launch_update(res.installer_url, res.installer_name || "TTC_Setup.exe");
      if (dl && dl.ok) {
        dlBtn.textContent = "✓ Instalador iniciado";
        showToast("✓ Instalador descargado y lanzado");
      } else {
        dlBtn.disabled = false;
        dlBtn.textContent = "⚠️ Reintentar descarga";
        showToast(`Error: ${dl?.error || "falló la descarga"}`);
      }
    });
  }
}

/* ================= BOOTSTRAP ================= */
async function initApp() {
  try {
    const boot = await window.pywebview.api.get_bootstrap();
    state.bootstrap = boot;
    document.getElementById("app-ver-lbl").textContent = `v${boot.version} · GPU`;
    const pmcIn = document.getElementById("hud-pmc-level");
    if (pmcIn) pmcIn.value = boot.pmc_level || 1;
    if (boot.sidebar_collapsed) {
      document.getElementById("app-shell").classList.add("collapsed");
    }
    applyLanguage(boot.lang || "es");
    applySkinPalette(boot.skin_id, boot.skins[boot.skin_id]);
    initSkinSelector();
    renderCommandCenter(boot.command_center);
  } catch (err) {
    console.error("Bootstrap error:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  updateRaidClock();
  setInterval(updateRaidClock, 1000);

  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });
  document.querySelectorAll("[data-goto]").forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.dataset.goto));
  });
  document.getElementById("btn-plan-raid").addEventListener("click", () => switchTab("quests"));

  const expBtn = document.getElementById("btn-export-profile");
  if (expBtn) {
    expBtn.addEventListener("click", async () => {
      const res = await window.pywebview.api.export_profile_json();
      if (res && res.ok) {
        const blob = new Blob([JSON.stringify(res.profile, null, 2)], { type: "application/json" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "perfil_ttc.json";
        a.click();
        URL.revokeObjectURL(a.href);
        showToast("✓ Respaldo perfil_ttc.json exportado");
      }
    });
  }

  document.getElementById("btn-collapse").addEventListener("click", async () => {
    const shell = document.getElementById("app-shell");
    const isCol = shell.classList.toggle("collapsed");
    if (window.pywebview?.api) {
      await window.pywebview.api.set_sidebar_collapsed(isCol);
    }
  });

  document.getElementById("kappa-filter-pending").addEventListener("click", () => {
    state.kappaFilter = "pending";
    document.getElementById("kappa-filter-pending").classList.add("active");
    document.getElementById("kappa-filter-all").classList.remove("active");
    renderKappaGrid();
  });
  document.getElementById("kappa-filter-all").addEventListener("click", () => {
    state.kappaFilter = "all";
    document.getElementById("kappa-filter-all").classList.add("active");
    document.getElementById("kappa-filter-pending").classList.remove("active");
    renderKappaGrid();
  });

  document.getElementById("btn-open-search").addEventListener("click", openSpotlight);
  document.getElementById("btn-patch-notes").addEventListener("click", openPatchNotes);
  document.getElementById("btn-close-notes").addEventListener("click", closeModals);
  document.getElementById("btn-socials")?.addEventListener("click", () => {
    document.getElementById("modal-socials")?.classList.add("open");
  });
  document.getElementById("btn-close-socials")?.addEventListener("click", closeModals);
  document.querySelectorAll("[data-ext-url]").forEach(btn => {
    btn.addEventListener("click", () => {
      window.pywebview.api.open_external_url(btn.dataset.extUrl);
      closeModals();
    });
  });
  document.getElementById("btn-github-update")?.addEventListener("click", openGitHubUpdater);
  document.getElementById("btn-close-update")?.addEventListener("click", closeModals);
  setupLightboxControls();

  const pmcInput = document.getElementById("hud-pmc-level");
  if (pmcInput) {
    pmcInput.addEventListener("change", async () => {
      const val = Math.max(1, Math.min(79, parseInt(pmcInput.value, 10) || 1));
      pmcInput.value = val;
      const res = await window.pywebview.api.set_pmc_level(val);
      if (res && res.ok) {
        if (state.bootstrap) state.bootstrap.pmc_level = res.pmc_level;
        showToast(window.TTC_LANG === "en" ? `✓ PMC Level set to ${res.pmc_level}` : `✓ Nivel de PMC actualizado a Nv.${res.pmc_level}`);
      }
    });
  }

  document.getElementById("btn-lang-toggle").addEventListener("click", async () => {
    const next = (state.bootstrap?.lang || "es") === "es" ? "en" : "es";
    const res = await window.pywebview.api.set_lang(next);
    if (res && res.ok) {
      state.bootstrap.lang = next;
      applyLanguage(next);
      if (state.activeTab && state.activeTab !== "command_center") {
        await switchTab(state.activeTab);
      }
      showToast(next === "en" ? "🌐 Language switched to English (EN)" : "🌐 Idioma cambiado a Español (ES)");
    }
  });

  document.getElementById("btn-sync").addEventListener("click", async () => {
    const lbl = document.getElementById("sync-lbl");
    lbl.textContent = "SYNC…";
    const res = await window.pywebview.api.sync_data();
    lbl.textContent = res?.ok ? "SYNC OK" : "ERROR";
    if (res?.ok && res.command_center) {
      renderCommandCenter(res.command_center);
      showToast("✓ Datos sincronizados en caché RAM");
    }
  });

  document.getElementById("btn-pin-top")?.addEventListener("click", async () => {
    const res = await window.pywebview.api.toggle_always_on_top();
    if (res && res.ok) {
      document.getElementById("btn-pin-top")?.classList.toggle("active", Boolean(res.always_on_top));
      const isEn = window.TTC_LANG === "en";
      showToast(res.always_on_top
        ? (isEn ? "📌 Always on top ON (Hotkey: Ctrl+Alt+T)" : "📌 Siempre encima activado (Atajo: Ctrl+Alt+T)")
        : (isEn ? "📌 Always on top OFF" : "📌 Siempre encima desactivado"));
    }
  });

  document.getElementById("btn-preraid-reset")?.addEventListener("click", async () => {
    const res = await window.pywebview.api.reset_preraid_checklist();
    if (res && res.ok) {
      renderPreRaidChecklist(res.preraid_checklist);
      showToast(window.TTC_LANG === "en" ? "↺ Pre-Raid checklist reset" : "↺ Checklist Pre-Raid reiniciado");
    }
  });

  const addPreRaid = async () => {
    const inp = document.getElementById("preraid-add-input");
    const val = (inp?.value || "").trim();
    if (!val) return;
    const res = await window.pywebview.api.add_preraid_item(val);
    if (res && res.ok) {
      inp.value = "";
      renderPreRaidChecklist(res.preraid_checklist);
    }
  };
  document.getElementById("btn-preraid-add")?.addEventListener("click", addPreRaid);
  document.getElementById("preraid-add-input")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addPreRaid();
    }
  });

  document.getElementById("spotlight-input").addEventListener("input", (e) => {
    clearTimeout(state.searchDebounce);
    state.searchDebounce = setTimeout(() => runSpotlightSearch(e.target.value), 120);
  });

  document.querySelectorAll(".modal-backdrop").forEach(m => {
    m.addEventListener("click", (e) => {
      if (e.target === m) closeModals();
    });
  });

  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && (e.key.toLowerCase() === "k" || e.key.toLowerCase() === "f")) {
      e.preventDefault();
      openSpotlight();
    } else if (e.key === "Escape") {
      closeModals();
    }
  });

  if (window.pywebview && window.pywebview.api) {
    initApp();
  } else {
    window.addEventListener("pywebviewready", initApp);
  }
});
