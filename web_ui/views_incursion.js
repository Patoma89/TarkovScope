/* =====================================================================
   TTC v2.0 — Vistas de Incursión: Mapas 2D (GPU Zoom/Pan + Listados),
   Bosses (Multi-mapa + Spawns + Facciones IA completas) & Llaves (230+)
   ===================================================================== */

window.TTCViews = window.TTCViews || {};

/* ================= 1. MAPAS 2D INTERACTIVOS ================= */
window.TTCViews.renderMapsView = async function (container) {
  container.innerHTML = `<div class="view-header"><h1 class="view-title">MAPAS <span>2D TÁCTICOS</span></h1><span style="color:var(--text-muted);font-size:12px">Rueda para Zoom · Arrastrar para Pan · Clic Derecho en mapa para agregar Pin</span></div><div id="maps-root" class="split-layout"></div>`;
  const root = container.querySelector("#maps-root");
  const maps = await window.pywebview.api.get_maps_catalog();
  let selectedKey = maps[0]?.key || "customs";
  const layers = { pmc: true, scav: true, boss: true, poi: true, user: true };
  let zoom = 0.78, panX = 0, panY = 0;

  root.innerHTML = `
    <div class="glass-card split-list" id="maps-list"></div>
    <div class="glass-card split-detail" id="maps-detail"></div>
  `;

  const listEl = root.querySelector("#maps-list");
  const detailEl = root.querySelector("#maps-detail");

  function renderList() {
    listEl.innerHTML = maps.map(m => `
      <button class="list-item-card ${m.key === selectedKey ? "active" : ""}" data-map="${escapeHtml(m.key)}">
        <div style="flex:1;min-width:0">
          <div style="font-weight:700;font-size:13px">${escapeHtml(m.name)}</div>
          <div style="font-size:11px;color:var(--text-muted)">⏱ ${escapeHtml(m.raid_duration)} · 👥 ${escapeHtml(m.players)}</div>
        </div>
      </button>
    `).join("");
    listEl.querySelectorAll(".list-item-card").forEach(btn => {
      btn.addEventListener("click", () => {
        selectedKey = btn.dataset.map;
        zoom = 0.78; panX = 0; panY = 0;
        renderList();
        loadDetail();
      });
    });
  }

  async function loadDetail() {
    const d = await window.pywebview.api.get_map_detail(selectedKey);
    const toPct = (v) => {
      if (typeof v !== "number" || Number.isNaN(v)) return null;
      return v <= 1 ? v * 100 : v;
    };
    const buildPins = () => {
      const pins = [];
      if (layers.pmc || layers.scav) {
        (d.extractions || []).forEach(ex => {
          const isScav = typeof ex.is_scav === "boolean"
            ? (ex.is_scav && !ex.is_pmc)
            : ((ex.faction || "").toLowerCase().includes("scav") && !(ex.faction || "").toLowerCase().includes("pmc"));
          if (isScav && !layers.scav) return;
          if (!isScav && !layers.pmc) return;
          const lx = toPct(typeof ex.x === "number" ? ex.x : ex.x_pct);
          const ly = toPct(typeof ex.y === "number" ? ex.y : ex.y_pct);
          if (lx === null || ly === null) return;
          pins.push(`<div class="map-pin ${isScav ? "scav" : "pmc"}" style="left:${lx.toFixed(2)}%;top:${ly.toFixed(2)}%" title="${escapeHtml(ex.req || ex.notes || ex.name)}">🚪 ${escapeHtml(ex.name)}</div>`);
        });
      }
      if (layers.poi) {
        const mapPois = Array.isArray(d.pois_on_map) ? d.pois_on_map : (d.pois || []);
        mapPois.forEach(p => {
          const lx = toPct(typeof p.x === "number" ? p.x : p.x_pct);
          const ly = toPct(typeof p.y === "number" ? p.y : p.y_pct);
          if (lx === null || ly === null) return;
          pins.push(`<div class="map-pin poi" style="left:${lx.toFixed(2)}%;top:${ly.toFixed(2)}%" title="${escapeHtml(p.desc || p.name)}">🔑 ${escapeHtml(p.name)}</div>`);
        });
      }
      if (layers.boss) {
        (d.bosses || []).forEach(b => {
          (b.spawns || []).forEach(sp => {
            const lx = toPct(typeof sp.x === "number" ? sp.x : sp.x_pct);
            const ly = toPct(typeof sp.y === "number" ? sp.y : sp.y_pct);
            if (lx === null || ly === null) return;
            const bShort = b.name.split(" (")[0];
            const zShort = sp.zone ? ` · ${sp.zone}` : "";
            pins.push(`<div class="map-pin boss" style="left:${lx.toFixed(2)}%;top:${ly.toFixed(2)}%" title="${escapeHtml(b.name)}${escapeHtml(zShort)} (PvE ${escapeHtml(b.pve_chance)})">💀 ${escapeHtml(bShort)}${escapeHtml(zShort)}</div>`);
          });
        });
      }
      if (layers.user) {
        (d.markers || []).forEach(mk => {
          const lx = toPct(typeof mk.x_pct === "number" ? mk.x_pct : mk.x);
          const ly = toPct(typeof mk.y_pct === "number" ? mk.y_pct : mk.y);
          if (lx === null || ly === null) return;
          pins.push(`<div class="map-pin user" data-del-pin="${mk.id}" style="left:${lx.toFixed(2)}%;top:${ly.toFixed(2)}%;background:${escapeHtml(mk.color || "#a855f7")}" title="Clic para eliminar: ${escapeHtml(mk.title)}">📌 ${escapeHtml(mk.title)}</div>`);
        });
      }
      return pins.join("");
    };

    detailEl.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
        <div>
          <h2 style="font-family:var(--font-display);font-size:20px;color:var(--accent-gold)">${escapeHtml(d.name)}</h2>
          <div style="font-size:12px;color:var(--text-muted)">${escapeHtml(d.description || "")}</div>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
          <button class="btn-ghost-sm ${layers.pmc ? "active" : ""}" data-layer="pmc">🟢 PMC</button>
          <button class="btn-ghost-sm ${layers.scav ? "active" : ""}" data-layer="scav">🟡 Scav</button>
          <button class="btn-ghost-sm ${layers.boss ? "active" : ""}" data-layer="boss">🔴 Bosses (${(d.bosses || []).length})</button>
          <button class="btn-ghost-sm ${layers.poi ? "active" : ""}" data-layer="poi">🔵 POIs (${(d.pois || []).length})</button>
          <button class="btn-ghost-sm ${layers.user ? "active" : ""}" data-layer="user">📌 Pines (${(d.markers || []).length})</button>
        </div>
      </div>

      <div class="map-stage" id="map-stage">
        <div class="map-controls">
          <button class="btn-ghost-sm" id="map-zoom-in">＋</button>
          <button class="btn-ghost-sm" id="map-zoom-out">－</button>
          <button class="btn-ghost-sm" id="map-zoom-reset">100%</button>
        </div>
        <div class="map-transform" id="map-transform" style="position:relative;display:inline-block">
          <img src="${escapeHtml(d.image_url)}" alt="${escapeHtml(d.name)}" style="display:block;max-width:none;user-select:none" draggable="false" />
          <div id="map-pins-layer" style="position:absolute;inset:0;pointer-events:none">${buildPins()}</div>
        </div>
        <div id="map-pin-dialog" style="display:none;position:absolute;left:50%;top:16px;transform:translateX(-50%);z-index:20;background:var(--bg-deep);border:1px solid var(--accent-gold);border-radius:12px;padding:10px 12px;box-shadow:0 12px 36px rgba(0,0,0,.75);gap:8px;align-items:center">
          <input class="t-input" id="map-pin-title" placeholder="Nombre del pin personal..." style="width:220px" />
          <button class="btn-primary-gold" id="map-pin-save" style="padding:6px 12px;font-size:12px">Guardar Pin</button>
          <button class="btn-ghost-sm" id="map-pin-cancel">✕</button>
        </div>
      </div>

      <div class="cards-grid-2">
        <div class="info-box">
          <div class="panel-title" style="color:var(--accent-emerald);margin-bottom:8px">🚪 Extracciones (${(d.extractions || []).length})</div>
          <div style="display:flex;flex-direction:column;gap:5px;max-height:220px;overflow-y:auto">
            ${(d.extractions || []).map(ex => `<div style="font-size:12px;color:var(--text-soft)"><strong>${escapeHtml(ex.name)}</strong> <span style="color:var(--accent-gold)">[${escapeHtml(ex.faction || "PMC")}]</span> ${(ex.req || ex.notes) ? `<span style="color:var(--text-muted)">— ${escapeHtml(ex.req || ex.notes)}</span>` : ""}</div>`).join("") || "<span style='color:var(--text-muted)'>Sin datos</span>"}
          </div>
        </div>
        <div class="info-box">
          <div class="panel-title" style="color:var(--accent-blue);margin-bottom:8px">🔑 POIs, Llaves &amp; Bosses en ${escapeHtml(d.name)}</div>
          <div style="display:flex;flex-direction:column;gap:5px;max-height:220px;overflow-y:auto">
            ${(d.bosses || []).map(b => `<div style="font-size:12px;color:var(--accent-amber)">💀 <strong>${escapeHtml(b.name)}</strong> — PvE ${escapeHtml(b.pve_chance)} / PvP ${escapeHtml(b.pvp_chance)}</div>`).join("")}
            ${(d.pois || []).map(p => `<div style="font-size:12px;color:var(--text-soft)">🔑 <strong>${escapeHtml(p.name)}</strong> ${p.desc ? `<span style="color:var(--text-muted)">— ${escapeHtml(p.desc)}</span>` : ""}</div>`).join("")}
          </div>
        </div>
      </div>
    `;

    const stage = detailEl.querySelector("#map-stage");
    const tf = detailEl.querySelector("#map-transform");
    const applyTransform = () => { tf.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`; };
    applyTransform();

    stage.addEventListener("wheel", (e) => {
      e.preventDefault();
      zoom = Math.max(0.25, Math.min(3.5, zoom * (e.deltaY < 0 ? 1.14 : 0.88)));
      applyTransform();
    }, { passive: false });

    let dragging = false, sx = 0, sy = 0;
    stage.addEventListener("mousedown", (e) => {
      if (e.button !== 0 || e.target.closest(".map-pin") || e.target.closest("#map-pin-dialog") || e.target.closest(".map-controls")) return;
      dragging = true; sx = e.clientX - panX; sy = e.clientY - panY;
    });
    const onMove = (e) => { if (!dragging) return; panX = e.clientX - sx; panY = e.clientY - sy; applyTransform(); };
    const onUp = () => { dragging = false; };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);

    let pendingPin = null;
    const pinDlg = detailEl.querySelector("#map-pin-dialog");
    const pinIn = detailEl.querySelector("#map-pin-title");
    stage.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      const img = tf.querySelector("img");
      const rect = img.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      const xPct = Math.max(0.02, Math.min(0.98, (e.clientX - rect.left) / rect.width));
      const yPct = Math.max(0.02, Math.min(0.98, (e.clientY - rect.top) / rect.height));
      pendingPin = { xPct, yPct };
      pinDlg.style.display = "flex";
      pinIn.value = "";
      pinIn.focus();
    });

    const savePendingPin = async () => {
      const title = (pinIn.value || "").trim();
      if (!pendingPin || !title) { pinDlg.style.display = "none"; return; }
      await window.pywebview.api.add_map_marker(selectedKey, pendingPin.xPct, pendingPin.yPct, title, "Nota Personal", "#a855f7");
      pendingPin = null;
      pinDlg.style.display = "none";
      showToast(`📌 Pin "${title}" guardado en SQLite`);
      loadDetail();
    };
    detailEl.querySelector("#map-pin-save")?.addEventListener("click", savePendingPin);
    detailEl.querySelector("#map-pin-cancel")?.addEventListener("click", () => { pendingPin = null; pinDlg.style.display = "none"; });
    pinIn?.addEventListener("keydown", (e) => { if (e.key === "Enter") savePendingPin(); if (e.key === "Escape") { pendingPin = null; pinDlg.style.display = "none"; } });

    detailEl.querySelectorAll("[data-del-pin]").forEach(el => {
      el.style.pointerEvents = "auto";
      el.addEventListener("click", async (e) => {
        e.stopPropagation();
        const mid = Number(el.dataset.delPin);
        await window.pywebview.api.delete_map_marker(selectedKey, mid);
        showToast("📌 Pin eliminado");
        loadDetail();
      });
    });

    detailEl.querySelector("#map-zoom-in").addEventListener("click", () => { zoom = Math.min(3.5, zoom * 1.2); applyTransform(); });
    detailEl.querySelector("#map-zoom-out").addEventListener("click", () => { zoom = Math.max(0.25, zoom * 0.82); applyTransform(); });
    detailEl.querySelector("#map-zoom-reset").addEventListener("click", () => { zoom = 0.78; panX = 0; panY = 0; applyTransform(); });
    detailEl.querySelectorAll("[data-layer]").forEach(btn => btn.addEventListener("click", () => { layers[btn.dataset.layer] = !layers[btn.dataset.layer]; loadDetail(); }));
  }

  renderList();
  loadDetail();
};

/* ================= 2. BOSSES & FACCIONES IA ================= */
window.TTCViews.renderBossesView = async function (container) {
  let data = await window.pywebview.api.get_bosses_data();
  let mode = "pve", subtab = "bosses";
  let selectedId = data.bosses[0]?.id || "reshala";
  let selectedMapIdx = 0;

  function render() {
    container.innerHTML = `
      <div class="view-header">
        <h1 class="view-title">BOSSES <span>&amp; FACCIONES IA</span></h1>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <div class="subtabs-bar">
            <button class="subtab-btn ${subtab === "bosses" ? "active" : ""}" id="bs-tab-bosses">💀 Bosses (${data.bosses.length})</button>
            <button class="subtab-btn ${subtab === "factions" ? "active" : ""}" id="bs-tab-factions">☠️ Facciones IA (${data.factions.length})</button>
          </div>
          <div class="subtabs-bar">
            <button class="subtab-btn ${mode === "pve" ? "active" : ""}" id="bs-mode-pve">PvE</button>
            <button class="subtab-btn ${mode === "pvp" ? "active" : ""}" id="bs-mode-pvp">PvP</button>
          </div>
          <button class="btn-ghost-sm" id="bs-sync-live">⟳ Sync eftboss.com</button>
        </div>
      </div>
      <div id="bosses-body"></div>
    `;

    container.querySelector("#bs-tab-bosses").addEventListener("click", () => { subtab = "bosses"; render(); });
    container.querySelector("#bs-tab-factions").addEventListener("click", () => { subtab = "factions"; render(); });
    container.querySelector("#bs-mode-pve").addEventListener("click", () => { mode = "pve"; render(); });
    container.querySelector("#bs-mode-pvp").addEventListener("click", () => { mode = "pvp"; render(); });
    container.querySelector("#bs-sync-live").addEventListener("click", async (e) => {
      e.currentTarget.textContent = "⏳ Sincronizando...";
      const res = await window.pywebview.api.sync_boss_spawns_live();
      if (res && res.data) data = res.data;
      showToast(res?.ok ? "✓ Probabilidades actualizadas desde eftboss.com" : "Usando datos offline oficiales");
      render();
    });

    const body = container.querySelector("#bosses-body");
    if (subtab === "factions") {
      body.innerHTML = `<div class="cards-grid-2">${data.factions.map(f => `
        <div class="glass-card panel-card">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
            <div>
              <strong style="font-size:16px;color:var(--accent-gold)">${escapeHtml(f.name)}</strong>
              <div style="font-size:11.5px;color:var(--text-muted)">${escapeHtml(f.subtitle_es || "")}</div>
            </div>
            <span class="kappa-tag">${escapeHtml(f.danger_level || "ALTA")}</span>
          </div>
          <div style="font-size:12px;color:var(--accent-blue)">📍 Mapas: ${escapeHtml((f.maps || []).join(" · "))}</div>
          <div class="info-box" style="font-size:12px;color:var(--text-soft)"><strong>⚠️ Reglas de Aggro:</strong> ${escapeHtml(f.aggro_rules_es || "")}</div>
          <div class="info-box" style="font-size:12px;color:var(--text-soft)"><strong>⚡ Activación / Spawns:</strong> ${escapeHtml(f.spawn_triggers_es || "")}</div>
          <div class="info-box" style="font-size:12px;color:var(--accent-emerald)">
            <strong>🎯 Guía de Farmeo:</strong>
            <ul style="margin:4px 0 0 16px;line-height:1.45">${(f.farming_guide_steps_es || []).map(s => `<li>${escapeHtml(s)}</li>`).join("")}</ul>
          </div>
          <div style="font-size:11.5px;color:var(--accent-gold)">💎 Top Loot: ${escapeHtml((f.top_loot || []).join(" · "))}</div>
        </div>
      `).join("")}</div>`;
      return;
    }

    const boss = data.bosses.find(b => b.id === selectedId) || data.bosses[0];
    const bossMaps = boss.maps || [];
    if (selectedMapIdx >= bossMaps.length) selectedMapIdx = 0;
    const activeMapName = bossMaps[selectedMapIdx] || "";
    const activeMapKey = boss.map_keys?.[selectedMapIdx] || "customs";
    const rawMapSpawns = boss.map_spawns || {};
    const spawnsHere =
      rawMapSpawns[activeMapName] ||
      rawMapSpawns[activeMapKey] ||
      Object.entries(rawMapSpawns).find(([k]) => k.toLowerCase() === activeMapName.toLowerCase())?.[1] ||
      [];
    const rate = mode === "pve" ? boss.pve_chance : boss.pvp_chance;
    const hpParts = Object.entries(boss.hp_breakdown || {}).map(([k, v]) => `<div class="stat-tile"><div class="stat-tile-lbl">${escapeHtml(k)}</div><div class="stat-tile-val">${v}</div></div>`).join("");

    body.innerHTML = `
      <div class="split-layout">
        <div class="glass-card split-list">
          ${data.bosses.map(b => `
            <button class="list-item-card ${b.id === selectedId ? "active" : ""}" data-boss="${escapeHtml(b.id)}">
              <img class="trader-avatar" src="${escapeHtml(b.avatar_url)}" alt="${escapeHtml(b.name)}" />
              <div style="flex:1;min-width:0">
                <div style="font-weight:700;font-size:13px">${escapeHtml(b.name.split(" (")[0])}</div>
                <div style="font-size:11px;color:var(--accent-gold)">${escapeHtml(mode === "pve" ? b.pve_chance : b.pvp_chance)} · ${escapeHtml((b.maps || []).slice(0, 2).join(", "))}</div>
              </div>
            </button>
          `).join("")}
        </div>
        <div class="glass-card split-detail">
          <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
            <img src="${escapeHtml(boss.avatar_url)}" style="width:86px;height:86px;border-radius:14px;object-fit:cover;border:2px solid var(--accent-gold)" />
            <div style="flex:1">
              <h2 style="font-family:var(--font-display);font-size:24px;color:var(--accent-gold)">${escapeHtml(boss.name)}</h2>
              <div style="color:var(--text-muted);font-size:12.5px;margin-top:3px">Mapas: ${escapeHtml(bossMaps.join(" · "))} · Spawn (${mode.toUpperCase()}): <strong style="color:var(--accent-emerald)">${escapeHtml(rate)}</strong></div>
              <div style="color:var(--text-soft);font-size:12px;margin-top:4px">Escoltas: ${escapeHtml(boss.followers || "Ninguna")}</div>
            </div>
            <div class="stat-tile" style="text-align:center;min-width:110px">
              <div class="stat-tile-lbl">Salud Total</div>
              <div class="stat-tile-val" style="color:var(--accent-red)">${boss.total_hp} HP</div>
            </div>
          </div>

          <div class="stat-grid-4">${hpParts}</div>

          <div class="cards-grid-2">
            <div class="info-box">
              <div class="panel-title" style="margin-bottom:8px;color:var(--accent-gold)">🔫 Armamento &amp; Botín Notable</div>
              <div style="font-size:12.5px;color:var(--text-soft);line-height:1.55">
                <strong>Armas:</strong> ${escapeHtml((boss.weapons || []).join(", "))}<br><br>
                <strong>Loot:</strong> ${escapeHtml((boss.notable_loot || []).join(" · "))}
              </div>
            </div>
            <div class="info-box">
              <div class="panel-title" style="margin-bottom:8px;color:var(--accent-emerald)">🧠 Tácticas de Combate</div>
              <div style="font-size:12.5px;color:var(--text-soft);line-height:1.55">${escapeHtml(boss.tactics || "")}</div>
            </div>
          </div>

          <div class="info-box">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:8px">
              <div class="panel-title">📍 Zonas de Spawn en ${escapeHtml(activeMapName)} (${spawnsHere.length} zonas)</div>
              <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                <div class="subtabs-bar">
                  ${bossMaps.map((mn, i) => `<button class="subtab-btn ${i === selectedMapIdx ? "active" : ""}" data-bmap="${i}">${escapeHtml(mn)}</button>`).join("")}
                </div>
                <button class="btn-ghost-sm" id="bs-zoom-map">🔍 Ampliar Mapa</button>
              </div>
            </div>
            <div class="zoomable-img-wrap" id="bs-map-box" title="Click para ampliar Radar HD">
              <img id="bs-radar-img" src="${escapeHtml((boss.map_spawn_urls || {})[activeMapName] || `/cache/maps/${activeMapKey}.png`)}" alt="${escapeHtml(activeMapName)}" style="width:100%;display:block;max-height:520px;object-fit:contain" />
              <span class="zoomable-hint">🔍 Click para ampliar Radar HD con zoom</span>
            </div>
            ${spawnsHere.length ? `
              <div style="margin-top:10px;display:flex;flex-direction:column;gap:6px">
                ${spawnsHere.map((sp, i) => `
                  <div style="font-size:12px;color:var(--text-soft);padding:6px 10px;border-radius:8px;background:rgba(255,255,255,0.03);border:1px solid var(--border-soft)">
                    <strong style="color:var(--accent-red)">#${i + 1} ${escapeHtml(sp.zone || sp.name || "")}</strong>
                    ${sp.details ? `<div style="font-size:11.5px;color:var(--text-muted);margin-top:2px">${escapeHtml(sp.details)}</div>` : ""}
                  </div>
                `).join("")}
              </div>
            ` : `<div style="margin-top:8px;font-size:12px;color:var(--text-muted)">Este boss patrulla de forma dinámica en ${escapeHtml(activeMapName)}.</div>`}
          </div>
        </div>
      </div>
    `;

    let currentRadarUrl = (boss.map_spawn_urls || {})[activeMapName] || `/cache/maps/${activeMapKey}.png`;
    if (!(boss.map_spawn_urls || {})[activeMapName] && activeMapName) {
      window.pywebview.api.get_boss_spawn_map_url(boss.id, activeMapName).then(res => {
        if (res && res.url) {
          boss.map_spawn_urls = boss.map_spawn_urls || {};
          boss.map_spawn_urls[activeMapName] = res.url;
          currentRadarUrl = res.url;
          const imgEl = body.querySelector("#bs-radar-img");
          if (imgEl) imgEl.src = res.url;
        }
      });
    }

    body.querySelectorAll("[data-boss]").forEach(btn => btn.addEventListener("click", () => { selectedId = btn.dataset.boss; selectedMapIdx = 0; render(); }));
    body.querySelectorAll("[data-bmap]").forEach(btn => btn.addEventListener("click", () => { selectedMapIdx = Number(btn.dataset.bmap); render(); }));
    const openBossMapZoom = () => window.openImageLightbox?.(currentRadarUrl, `${boss.name} — Radar de Spawns (${activeMapName})`, `${spawnsHere.length} zonas calibradas · Rueda para zoom · Arrastra para mover`);
    body.querySelector("#bs-zoom-map")?.addEventListener("click", openBossMapZoom);
    body.querySelector("#bs-map-box")?.addEventListener("click", openBossMapZoom);
  }

  render();
};

/* ================= 3. LLAVES & INTEL (TODAS LAS 230+ LLAVES) ================= */
window.TTCViews.renderKeysView = async function (container) {
  const data = await window.pywebview.api.get_keys_data();
  let activeMap = "Todos", activeCat = "Todas", query = "", onlyMissingQuest = false;
  let selectedId = data.items[0]?.id || "";

  container.innerHTML = `
    <div class="view-header">
      <h1 class="view-title">LLAVES, <span>KEYCARDS &amp; MARKED ROOMS</span></h1>
      <div id="keys-kpi-lbl" class="hud-chip"></div>
    </div>
    <div class="glass-card toolbar-row">
      <input class="t-input" id="keys-search" placeholder="Buscar llave, habitación, misión o loot..." style="flex:1;min-width:220px" />
      <select class="t-select" id="keys-map-sel">${data.maps.map(m => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`).join("")}</select>
      <select class="t-select" id="keys-cat-sel">${data.categories.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("")}</select>
      <button class="btn-ghost-sm" id="keys-missing-btn">Solo Quest faltantes</button>
    </div>
    <div class="split-layout">
      <div class="glass-card split-list" id="keys-list"></div>
      <div class="glass-card split-detail" id="keys-detail"></div>
    </div>
  `;

  const listEl = container.querySelector("#keys-list");
  const detailEl = container.querySelector("#keys-detail");
  const kpiEl = container.querySelector("#keys-kpi-lbl");

  function updateKpi() {
    const owned = data.items.filter(k => k.owned).length;
    kpiEl.textContent = `🔑 ${owned} / ${data.items.length} en tu llavero`;
  }

  function filtered() {
    const q = query.trim().toLowerCase();
    return data.items.filter(k => {
      if (activeMap !== "Todos" && k.map !== activeMap) return false;
      if (activeCat !== "Todas" && k.category !== activeCat) return false;
      if (onlyMissingQuest && (!(k.quests && k.quests.length) || k.owned)) return false;
      if (q && !`${k.name} ${k.short_name} ${k.map} ${k.opens} ${k.loot} ${(k.quests || []).join(" ")}`.toLowerCase().includes(q)) return false;
      return true;
    });
  }

  function renderDetail(item) {
    if (!item) { detailEl.innerHTML = `<div style="color:var(--text-muted)">Selecciona una llave.</div>`; return; }
    detailEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:14px">
        <img src="${escapeHtml(item.icon_url)}" style="width:68px;height:68px;object-fit:contain;background:#06080d;border-radius:10px;padding:6px;border:1px solid var(--border)" onerror="this.style.display='none'" />
        <div style="flex:1">
          <h2 style="font-family:var(--font-display);font-size:21px;color:var(--accent-gold)">${escapeHtml(item.name)}</h2>
          <div style="font-size:12px;color:var(--text-muted);margin-top:3px">📍 ${escapeHtml(item.map)} · ${escapeHtml(item.category)} · Usos: ${item.uses || "∞"} · Valor: ${escapeHtml(item.approx_value || "—")}</div>
        </div>
        <button class="btn-primary-gold" id="btn-toggle-key">${item.owned ? "✓ En mi Llavero" : "+ Marcar en Llavero"}</button>
      </div>
      <div class="info-box"><strong style="color:var(--accent-gold)">🚪 Qué abre:</strong><div style="margin-top:4px;color:var(--text-soft)">${escapeHtml(item.opens || "—")}</div></div>
      <div class="info-box"><strong style="color:var(--accent-emerald)">💎 Botín principal:</strong><div style="margin-top:4px;color:var(--text-soft)">${escapeHtml(item.loot || "—")}</div></div>
      <div class="info-box"><strong style="color:var(--accent-blue)">📍 Dónde encontrarla:</strong><div style="margin-top:4px;color:var(--text-soft)">${escapeHtml(item.spawns || "—")}</div></div>
      ${(item.quests && item.quests.length) ? `<div class="info-box"><strong style="color:var(--accent-amber)">📜 Misiones requeridas:</strong><div style="margin-top:4px;color:var(--text-soft)">${escapeHtml(item.quests.join(" · "))}</div></div>` : ""}
    `;
    detailEl.querySelector("#btn-toggle-key").addEventListener("click", async () => {
      const res = await window.pywebview.api.toggle_key_owned(item.id);
      if (res && res.ok) {
        item.owned = res.owned;
        updateKpi();
        renderList();
        renderDetail(item);
        showToast(item.owned ? `🔑 ${item.short_name} agregada al llavero` : `↩ Quitada del llavero`);
      }
    });
  }

  function renderList() {
    const items = filtered();
    if (items.length && !items.some(i => i.id === selectedId)) selectedId = items[0].id;
    listEl.innerHTML = items.map(k => `
      <button class="list-item-card ${k.id === selectedId ? "active" : ""} ${k.owned ? "owned" : ""}" data-kid="${escapeHtml(k.id)}">
        <img class="item-thumb-sm" src="${escapeHtml(k.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
        <div style="flex:1;min-width:0">
          <div style="font-weight:700;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${k.owned ? "✓ " : ""}${escapeHtml(k.name)}</div>
          <div style="font-size:11px;color:var(--text-muted)">${escapeHtml(k.map)} · ${escapeHtml(k.category)}</div>
        </div>
      </button>
    `).join("") || `<div style="padding:20px;color:var(--text-muted);text-align:center">Sin llaves para ese filtro.</div>`;

    listEl.querySelectorAll("[data-kid]").forEach(btn => {
      btn.addEventListener("click", () => {
        selectedId = btn.dataset.kid;
        renderList();
        renderDetail(data.items.find(x => x.id === selectedId));
      });
    });
    renderDetail(data.items.find(x => x.id === selectedId));
  }

  container.querySelector("#keys-search").addEventListener("input", (e) => { query = e.target.value; renderList(); });
  container.querySelector("#keys-map-sel").addEventListener("change", (e) => { activeMap = e.target.value; renderList(); });
  container.querySelector("#keys-cat-sel").addEventListener("change", (e) => { activeCat = e.target.value; renderList(); });
  container.querySelector("#keys-missing-btn").addEventListener("click", (e) => {
    onlyMissingQuest = !onlyMissingQuest;
    e.currentTarget.classList.toggle("active", onlyMissingQuest);
    renderList();
  });

  updateKpi();
  renderList();
};
