/* =====================================================================
   TTC v2.0 — Vistas de Progresión: Todas las 459 Quests, Dossier Wiki,
   Inventario Traders LL1-LL4 (Grid + Lista), Rutas Óptimas e Historia
   ===================================================================== */

window.TTCViews = window.TTCViews || {};

const QUEST_MAPS = [
  "TODOS", "Ground Zero", "Customs", "Woods", "Factory",
  "Interchange", "Shoreline", "Reserve", "Lighthouse", "Streets of Tarkov", "The Lab",
];

window.TTCViews.renderQuestsView = async function (container) {
  let subtab = "quests"; // quests | assortment | routes | story
  let qTrader = "TODOS", qMap = "TODOS", qMode = "CORRELATIVE", qSearch = "", qHideDone = false;
  let aTrader = "Prapor", aLL = 1, aSearch = "";
  let rMap = "customs", rSelectedTasks = new Set(), rSpawnIdx = 0;

  container.innerHTML = `
    <div class="view-header">
      <h1 class="view-title">PROGRESIÓN <span>&amp; QUESTS</span></h1>
      <div class="subtabs-bar" id="q-subtabs">
        <button class="subtab-btn active" data-st="quests">📜 Misiones &amp; Traders</button>
        <button class="subtab-btn" data-st="assortment">🛒 Inventario LL1–LL4</button>
        <button class="subtab-btn" data-st="routes">🧭 Rutas Óptimas</button>
        <button class="subtab-btn" data-st="story">📕 Historia (10 Capítulos)</button>
      </div>
    </div>
    <div id="quests-body"></div>
  `;

  const body = container.querySelector("#quests-body");
  container.querySelectorAll("#q-subtabs .subtab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      subtab = btn.dataset.st;
      container.querySelectorAll("#q-subtabs .subtab-btn").forEach(b => b.classList.toggle("active", b.dataset.st === subtab));
      renderSubtab();
    });
  });

  async function openQuestGuideModal(questId) {
    const res = await window.pywebview.api.get_quest_guide(questId);
    if (!res || !res.ok) return;
    const q = res.quest, g = res.guide || {};
    const modal = document.getElementById("modal-notes");
    const titleEl = document.getElementById("notes-modal-title");
    const mBody = document.getElementById("notes-body");
    modal.classList.add("modal-dossier");
    if (titleEl) titleEl.textContent = "📖 DOSSIER TÁCTICO DE MISIÓN";
    modal.classList.add("open");

    const steps = g.walkthrough_steps || [];
    const hasSteps = steps.length > 0;

    mBody.innerHTML = `
      <div class="glass-card" style="padding:18px 20px">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">
          <div>
            <h3 style="font-family:var(--font-display);font-size:23px;letter-spacing:0.5px;color:var(--accent-gold);line-height:1.15">${escapeHtml(q.title)}</h3>
            <div style="font-size:13.5px;color:var(--text-muted);margin-top:4px">${escapeHtml(q.trader_name)} · 📍 ${escapeHtml(q.primary_map)} · Nv.${q.level_req} · +${q.exp.toLocaleString("es-AR")} XP</div>
          </div>
          <div style="display:flex;gap:8px;align-items:center">
            ${q.is_kappa ? `<span class="kappa-tag" style="font-size:11.5px;padding:4px 10px">REQUERIDA KAPPA</span>` : ""}
            ${q.is_lightkeeper ? `<span class="kappa-tag" style="font-size:11.5px;padding:4px 10px;color:var(--accent-blue);border-color:rgba(56,189,248,.4)">LIGHTKEEPER</span>` : ""}
          </div>
        </div>
        ${res.map_image_url ? `
          <div class="zoomable-img-wrap" id="dossier-map-wrap" style="margin-top:14px" title="Click para ampliar con zoom">
            <img src="${escapeHtml(res.map_image_url)}" style="width:100%;max-height:390px;object-fit:contain;display:block;border-radius:10px;background:#06080d" />
            <span class="zoomable-hint">🔍 Click para ampliar mapa con zoom</span>
          </div>
        ` : ""}
      </div>
      <div class="${hasSteps ? "dossier-grid" : ""}" style="${hasSteps ? "" : "display:flex;flex-direction:column;gap:12px"}">
        <div style="display:flex;flex-direction:column;gap:12px">
          <div class="info-box dossier-section">
            <h4 style="color:var(--accent-gold)">📋 Objetivos</h4>
            <ul style="margin:0 0 0 18px;color:var(--text-soft)">${(q.objectives_lines || []).map(l => `<li style="margin-bottom:4px">${escapeHtml(l)}</li>`).join("")}</ul>
          </div>
          ${(q.rewards_lines || []).length ? `
            <div class="info-box dossier-section">
              <h4 style="color:var(--accent-blue)">🎁 Recompensas</h4>
              <div style="color:var(--text-soft)">${escapeHtml(q.rewards_lines.join(" · "))}</div>
            </div>
          ` : ""}
          ${(q.prereq_titles || []).length || (q.unlocks_titles || []).length ? `
            <div class="info-box dossier-section" style="color:var(--text-muted)">
              <h4 style="color:var(--text-soft)">🔗 Cadena de Progresión</h4>
              ${(q.prereq_titles || []).length ? `<div><strong>⬅ Prerrequisitos:</strong> ${escapeHtml(q.prereq_titles.join(", "))}</div>` : ""}
              ${(q.unlocks_titles || []).length ? `<div style="margin-top:6px"><strong>➡ Desbloquea:</strong> ${escapeHtml(q.unlocks_titles.join(", "))}</div>` : ""}
            </div>
          ` : ""}
        </div>
        ${hasSteps ? `
          <div class="info-box dossier-section">
            <h4 style="color:var(--accent-emerald)">🧭 Guía Paso a Paso (Offline)</h4>
            <ol style="margin:0 0 0 18px;color:var(--text-soft)">${steps.map(s => `<li style="margin-bottom:6px">${escapeHtml(typeof s === "string" ? s : (s.detail || s.title || ""))}</li>`).join("")}</ol>
          </div>
        ` : ""}
      </div>
    `;

    mBody.querySelector("#dossier-map-wrap")?.addEventListener("click", () => {
      window.openImageLightbox?.(res.map_image_url, q.title, `${q.trader_name} · ${q.primary_map}`);
    });
  }

  async function renderQuestsTab() {
    const data = await window.pywebview.api.get_quests_data(qTrader, qMap, qMode, qSearch, qHideDone);
    body.innerHTML = `
      <div class="trader-strip">
        <button class="trader-card-btn ${qTrader === "TODOS" ? "active" : ""}" data-tr="TODOS"><div style="height:44px;display:grid;place-items:center;font-weight:800;color:var(--accent-gold)">ALL</div><span>Todos</span></button>
        ${data.traders.map(t => `<button class="trader-card-btn ${qTrader === t.name ? "active" : ""}" data-tr="${escapeHtml(t.name)}"><img src="${escapeHtml(t.avatar_url)}" /><span>${escapeHtml(t.name)}</span></button>`).join("")}
      </div>
      <div class="glass-card toolbar-row">
        <input class="t-input" id="q-search" value="${escapeHtml(qSearch)}" placeholder="Buscar misión, objetivo o mapa..." style="flex:1;min-width:180px" />
        <select class="t-select" id="q-map">${QUEST_MAPS.map(m => `<option value="${escapeHtml(m)}" ${m === qMap ? "selected" : ""}>${m === "TODOS" ? "Todos los Mapas" : escapeHtml(m)}</option>`).join("")}</select>
        <select class="t-select" id="q-mode">
          <option value="CORRELATIVE" ${qMode === "CORRELATIVE" ? "selected" : ""}>Progresión Correlativa</option>
          <option value="KAPPA" ${qMode === "KAPPA" ? "selected" : ""}>Solo KAPPA</option>
          <option value="LIGHTKEEPER" ${qMode === "LIGHTKEEPER" ? "selected" : ""}>Ruta Lightkeeper</option>
          <option value="ALL" ${qMode === "ALL" ? "selected" : ""}>Todas (${data.total})</option>
        </select>
        <button class="btn-ghost-sm ${qHideDone ? "active" : ""}" id="q-hide-done">Ocultar completadas</button>
        <span class="hud-chip">Mostrando ${data.items.length} · ✓ ${data.done}/${data.total}</span>
      </div>
      <div class="table-wrap glass-card">
        <table class="tarkov-table">
          <thead><tr><th style="width:46px">✓</th><th>Misión</th><th>Trader / Mapa</th><th>Objetivos</th><th style="width:110px">Guía</th></tr></thead>
          <tbody>
            ${data.items.map(q => `
              <tr>
                <td><button class="btn-check-quest" data-toggle-q="${q.id}" style="${q.is_completed ? "background:var(--accent-emerald);color:#04120c" : ""}">✓</button></td>
                <td>
                  <div style="font-weight:700;color:${q.is_completed ? "var(--accent-emerald)" : "var(--text-main)"}">${escapeHtml(q.title)}</div>
                  <div style="margin-top:3px;display:flex;gap:5px;flex-wrap:wrap">
                    ${q.is_kappa ? `<span class="kappa-tag">Kappa</span>` : ""}
                    ${q.is_lightkeeper ? `<span class="kappa-tag" style="color:var(--accent-blue)">LK</span>` : ""}
                    <span class="xp-tag">Nv.${q.level_req} · +${q.exp.toLocaleString("es-AR")} XP</span>
                  </div>
                </td>
                <td><strong>${escapeHtml(q.trader_name)}</strong><div style="font-size:11px;color:var(--text-muted)">📍 ${escapeHtml(q.primary_map)}</div></td>
                <td style="font-size:11.5px;color:var(--text-muted);max-width:380px">${escapeHtml((q.objectives_lines || []).slice(0, 3).join(" • "))}</td>
                <td><button class="btn-ghost-sm" data-guide-q="${q.id}">📖 Dossier</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;

    body.querySelectorAll("[data-tr]").forEach(btn => btn.addEventListener("click", () => { qTrader = btn.dataset.tr; renderQuestsTab(); }));
    body.querySelector("#q-map").addEventListener("change", (e) => { qMap = e.target.value; renderQuestsTab(); });
    body.querySelector("#q-mode").addEventListener("change", (e) => { qMode = e.target.value; renderQuestsTab(); });
    body.querySelector("#q-hide-done").addEventListener("click", () => { qHideDone = !qHideDone; renderQuestsTab(); });
    let tmr = null;
    body.querySelector("#q-search").addEventListener("input", (e) => { qSearch = e.target.value; clearTimeout(tmr); tmr = setTimeout(renderQuestsTab, 160); });
    body.querySelectorAll("[data-toggle-q]").forEach(btn => {
      btn.addEventListener("click", async () => {
        const res = await window.pywebview.api.toggle_quest_synced(Number(btn.dataset.toggleQ));
        if (res && res.ok) {
          if (res.command_center && window.renderCommandCenter) window.renderCommandCenter(res.command_center);
          renderQuestsTab();
          showToast(res.is_completed ? "✓ Misión completada" : "↩ Misión desmarcada");
        }
      });
    });
    body.querySelectorAll("[data-guide-q]").forEach(btn => btn.addEventListener("click", () => openQuestGuideModal(Number(btn.dataset.guideQ))));
  }

  async function renderAssortmentTab() {
    const data = await window.pywebview.api.get_trader_assortment_data(aTrader, aLL);
    const aq = aSearch.trim().toLowerCase();
    const filteredItems = (data.items || []).filter(it => !aq || `${it.name} ${it.category} ${it.desc}`.toLowerCase().includes(aq));
    const req = data.requirements || {};
    body.innerHTML = `
      <div class="trader-strip">
        ${data.traders.map(t => `<button class="trader-card-btn ${aTrader === t.name ? "active" : ""}" data-atr="${escapeHtml(t.name)}"><img src="${escapeHtml(t.avatar_url)}" /><span>${escapeHtml(t.name)}</span></button>`).join("")}
      </div>
      <div class="glass-card toolbar-row" style="justify-content:space-between">
        <div class="subtabs-bar">
          ${[1, 2, 3, 4].map(lv => `<button class="subtab-btn ${aLL === lv ? "active" : ""}" data-ll="${lv}">LL${lv}${lv === 4 ? " 👑" : ""}</button>`).join("")}
        </div>
        <input class="t-input" id="a-search" value="${escapeHtml(aSearch)}" placeholder="Filtrar ítems de ${escapeHtml(data.trader)}..." style="width:240px" />
        <div style="font-size:12px;color:var(--accent-blue);font-weight:700">Nv.${req.level || 1} · Rep ${req.rep ?? 0} · Gasto ${(req.spend || 0).toLocaleString("es-AR")}</div>
      </div>
      <div class="glass-card panel-card" style="margin-bottom:14px">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
          <div class="panel-title">Cuadrícula Oficial In-Game — ${escapeHtml(data.trader)} LL${data.ll}</div>
          <button class="btn-primary-gold" id="a-zoom-stock" style="padding:6px 12px;font-size:12px">🔍 Ampliar Inventario (Zoom)</button>
        </div>
        <div class="zoomable-img-wrap" id="a-stock-wrap" title="Click para ampliar con zoom">
          <img src="${escapeHtml(data.stock_image_url)}" style="width:100%;max-height:460px;object-fit:contain;display:block" onerror="this.parentElement.style.display='none'" />
          <span class="zoomable-hint">🔍 Click para ampliar y hacer zoom</span>
        </div>
      </div>
      <div class="cards-grid-3">
        ${filteredItems.map(it => `
          <div class="glass-card panel-card">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:6px">
              <strong style="color:var(--accent-gold);font-size:13px">${escapeHtml(it.name)}</strong>
              <span class="kappa-tag">${escapeHtml(it.category || "ITEM")}</span>
            </div>
            <div style="font-size:12px;color:var(--accent-emerald);font-weight:700">${escapeHtml(it.cost || "")} · <span style="color:var(--text-muted);font-weight:400">${escapeHtml(it.limit || "")}</span></div>
            <div style="font-size:11.5px;color:var(--text-soft)">${escapeHtml(it.desc || "")}</div>
          </div>
        `).join("")}
      </div>
    `;
    const openStockZoom = () => window.openImageLightbox?.(
      data.stock_image_url,
      `${data.trader} — Inventario Oficial LL${data.ll}`,
      `Nv.${req.level || 1} · Rep ${req.rep ?? 0} · Gasto ${(req.spend || 0).toLocaleString("es-AR")} · Usa la rueda del mouse para hacer zoom y arrastra para explorar`
    );
    body.querySelector("#a-zoom-stock")?.addEventListener("click", openStockZoom);
    body.querySelector("#a-stock-wrap")?.addEventListener("click", openStockZoom);
    body.querySelectorAll("[data-atr]").forEach(b => b.addEventListener("click", () => { aTrader = b.dataset.atr; renderAssortmentTab(); }));
    body.querySelectorAll("[data-ll]").forEach(b => b.addEventListener("click", () => { aLL = Number(b.dataset.ll); renderAssortmentTab(); }));
    body.querySelector("#a-search").addEventListener("input", (e) => { aSearch = e.target.value; renderAssortmentTab(); });
  }

  let rTaskFilter = "";
  let rLastPlan = null;

  async function renderRoutesTab() {
    const maps = await window.pywebview.api.get_route_maps_list();
    if (!maps.some(m => m.key === rMap) && maps.length) rMap = maps[0].key;
    const mapData = await window.pywebview.api.get_route_map_tasks(rMap);
    const rq = rTaskFilter.trim().toLowerCase();
    const filteredTasks = (mapData.tasks || []).filter(t => !rq || `${t.name} ${t.trader}`.toLowerCase().includes(rq));

    function buildRouteOverlay(plan) {
      if (!plan || !plan.ok) return "";
      const pts = [];
      if (plan.start && typeof plan.start.x_pct === "number") pts.push({ x: plan.start.x_pct, y: plan.start.y_pct });
      (plan.ordered_stops || []).forEach(s => { if (typeof s.x_pct === "number") pts.push({ x: s.x_pct, y: s.y_pct }); });
      if (plan.extract && typeof plan.extract.x_pct === "number") pts.push({ x: plan.extract.x_pct, y: plan.extract.y_pct });

      const svgLine = pts.length >= 2
        ? `<svg viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:3">
             <polyline points="${pts.map(p => `${p.x},${p.y}`).join(" ")}" fill="none" stroke="#f59e0b" stroke-width="0.65" stroke-dasharray="1.6 0.9" stroke-linecap="round" stroke-linejoin="round" />
           </svg>`
        : "";

      const startPin = plan.start && typeof plan.start.x_pct === "number"
        ? `<div class="route-pin start" style="left:${plan.start.x_pct}%;top:${plan.start.y_pct}%">INICIO</div>`
        : "";
      const stopPins = (plan.ordered_stops || []).map((s, idx) =>
        typeof s.x_pct === "number"
          ? `<div class="route-pin stop" style="left:${s.x_pct}%;top:${s.y_pct}%" title="${escapeHtml(s.label)}">#${idx + 1} ${escapeHtml(s.quest || "")}</div>`
          : ""
      ).join("");
      const extPin = plan.extract && typeof plan.extract.x_pct === "number"
        ? `<div class="route-pin extract" style="left:${plan.extract.x_pct}%;top:${plan.extract.y_pct}%">EXIT: ${escapeHtml(plan.extract.name)}</div>`
        : "";
      return svgLine + startPin + stopPins + extPin;
    }

    body.innerHTML = `
      <div class="glass-card toolbar-row">
        <select class="t-select" id="r-map-sel">${maps.map(m => `<option value="${escapeHtml(m.key)}" ${m.key === rMap ? "selected" : ""}>${escapeHtml(m.label)}</option>`).join("")}</select>
        <select class="t-select" id="r-spawn-sel" style="max-width:340px">${(mapData.spawns || []).map((s, idx) => `<option value="${idx}" ${idx === rSpawnIdx ? "selected" : ""}>${escapeHtml(s.label || `Spawn ${idx + 1}`)}</option>`).join("")}</select>
        <input class="t-input" id="r-task-search" value="${escapeHtml(rTaskFilter)}" placeholder="Filtrar misiones del mapa..." style="width:200px" />
        <button class="btn-primary-gold" id="r-calc-btn">🧭 Calcular Ruta (${rSelectedTasks.size})</button>
        ${rSelectedTasks.size ? `<button class="btn-ghost-sm" id="r-clear-btn">Limpiar</button>` : ""}
      </div>
      <div class="split-layout">
        <div class="glass-card split-list">
          <div class="panel-title" style="padding:4px 6px">Misiones en ${escapeHtml(mapData.name)} (${filteredTasks.length}/${(mapData.tasks || []).length})</div>
          ${filteredTasks.map(t => {
            const tid = String(t.id || t.name);
            return `
              <label class="list-item-card ${rSelectedTasks.has(tid) ? "active" : ""}">
                <input type="checkbox" data-rtask="${escapeHtml(tid)}" ${rSelectedTasks.has(tid) ? "checked" : ""} />
                <div style="flex:1;min-width:0">
                  <div style="font-weight:700;font-size:12.5px">${escapeHtml(t.name)}</div>
                  <div style="font-size:11px;color:var(--text-muted)">${escapeHtml(t.trader || "")} · ${t.objectives_count || (t.objectives || []).length} objetivos${t.kappa ? " · ⭐ Kappa" : ""}</div>
                </div>
              </label>
            `;
          }).join("")}
        </div>
        <div class="glass-card split-detail" id="r-result-box">
          <div class="map-overlay-container" id="r-map-stage" style="cursor:zoom-in">
            <img src="${escapeHtml(mapData.image_url)}" alt="${escapeHtml(mapData.name)}" />
            <div id="r-map-pins">${buildRouteOverlay(rLastPlan)}</div>
          </div>
          <div class="info-box" id="r-plan-out" style="color:var(--text-muted)">
            ${rLastPlan && rLastPlan.ok ? `
              <div style="color:var(--accent-emerald);font-weight:800;margin-bottom:8px">
                ✓ Ruta Óptima (${rLastPlan.exact ? "Exacta" : "Heurística"}) — Distancia total: ${rLastPlan.total_distance}m · Extracción: ${escapeHtml(rLastPlan.extract_name || "Más cercana")}
              </div>
              <ol style="margin-left:18px;color:var(--text-soft);line-height:1.65;font-size:12.5px">
                ${(rLastPlan.ordered_stops || []).map(s => `<li><strong>${escapeHtml(s.quest || "")}</strong>: ${escapeHtml(s.label.replace(`${s.quest} — `, ""))} <span style="color:var(--accent-gold);font-family:var(--font-mono)">(+${s.distance}m · Σ ${s.cumulative}m)</span></li>`).join("")}
              </ol>
            ` : `Tilda una o más misiones a la izquierda y presiona <strong>Calcular Ruta</strong> para trazar el recorrido más corto con extracción óptima.`}
          </div>
        </div>
      </div>
    `;

    body.querySelector("#r-map-sel").addEventListener("change", (e) => { rMap = e.target.value; rSelectedTasks.clear(); rSpawnIdx = 0; rLastPlan = null; renderRoutesTab(); });
    body.querySelector("#r-spawn-sel").addEventListener("change", (e) => { rSpawnIdx = Number(e.target.value); });
    body.querySelector("#r-task-search").addEventListener("input", (e) => { rTaskFilter = e.target.value; renderRoutesTab(); });
    body.querySelector("#r-clear-btn")?.addEventListener("click", () => { rSelectedTasks.clear(); rLastPlan = null; renderRoutesTab(); });
    body.querySelector("#r-map-stage")?.addEventListener("click", () => window.openImageLightbox?.(mapData.image_url, `Mapa de Rutas — ${mapData.name}`, "Rueda del mouse para zoom · Arrastra para mover"));
    body.querySelectorAll("[data-rtask]").forEach(cb => cb.addEventListener("change", () => {
      if (cb.checked) rSelectedTasks.add(cb.dataset.rtask);
      else rSelectedTasks.delete(cb.dataset.rtask);
      const calcBtn = body.querySelector("#r-calc-btn");
      if (calcBtn) calcBtn.textContent = `🧭 Calcular Ruta (${rSelectedTasks.size})`;
      cb.closest(".list-item-card")?.classList.toggle("active", cb.checked);
    }));
    body.querySelector("#r-calc-btn").addEventListener("click", async () => {
      const res = await window.pywebview.api.compute_optimal_route(rMap, Array.from(rSelectedTasks), rSpawnIdx);
      const out = body.querySelector("#r-plan-out");
      if (!res || !res.ok) {
        rLastPlan = null;
        body.querySelector("#r-map-pins").innerHTML = "";
        out.innerHTML = `<span style="color:var(--accent-amber)">⚠️ ${escapeHtml(res?.error || "Error calculando la ruta")}</span>`;
        return;
      }
      rLastPlan = res;
      body.querySelector("#r-map-pins").innerHTML = buildRouteOverlay(res);
      out.innerHTML = `
        <div style="color:var(--accent-emerald);font-weight:800;margin-bottom:8px">
          ✓ Ruta Óptima (${res.exact ? "Exacta" : "Heurística"}) — Distancia total: ${res.total_distance}m · Extracción: ${escapeHtml(res.extract_name || "Más cercana")}
        </div>
        <ol style="margin-left:18px;color:var(--text-soft);line-height:1.65;font-size:12.5px">
          ${(res.ordered_stops || []).map(s => `<li><strong>${escapeHtml(s.quest || "")}</strong>: ${escapeHtml(s.label.replace(`${s.quest} — `, ""))} <span style="color:var(--accent-gold);font-family:var(--font-mono)">(+${s.distance}m · Σ ${s.cumulative}m)</span></li>`).join("")}
        </ol>
      `;
      showToast(`🧭 Ruta calculada: ${res.total_distance}m (${res.ordered_stops.length} paradas)`);
    });
  }

  async function renderStoryTab() {
    const data = await window.pywebview.api.get_story_chapters_data();
    let activeIdx = 0;
    const fmtListOrText = (val) => Array.isArray(val) ? val.filter(Boolean).join(" · ") : String(val || "").trim();
    function draw() {
      const ch = data.chapters[activeIdx] || data.chapters[0];
      if (!ch) {
        body.innerHTML = `<div class="glass-card panel-card" style="color:var(--text-muted)">No se encontraron capítulos de historia.</div>`;
        return;
      }
      const reqText = fmtListOrText(ch.requirements_es || ch.requirements_en);
      const rewText = fmtListOrText(ch.rewards_es || ch.rewards);
      body.innerHTML = `
        <div class="split-layout">
          <div class="glass-card split-list">
            ${data.chapters.map((c, idx) => `
              <button class="list-item-card ${idx === activeIdx ? "active" : ""}" data-ch="${idx}">
                ${c.icon_url ? `<img class="item-thumb-sm" src="${escapeHtml(c.icon_url)}" style="width:34px;height:34px" onerror="this.style.display='none'" />` : ""}
                <div style="flex:1">
                  <div style="font-weight:700;font-size:13px">${c.chapter_number || idx + 1}. ${escapeHtml(c.title || "")}</div>
                  <div style="font-size:11px;color:var(--accent-gold)">${c.completed_count || 0}/${c.total_count || 0} objetivos</div>
                </div>
              </button>
            `).join("")}
          </div>
          <div class="glass-card split-detail">
            ${ch.banner_url ? `<img src="${escapeHtml(ch.banner_url)}" style="width:100%;max-height:190px;object-fit:cover;border-radius:10px" onerror="this.style.display='none'" />` : ""}
            <h2 style="font-family:var(--font-display);font-size:23px;color:var(--accent-gold)">Capítulo ${ch.chapter_number || activeIdx + 1}: ${escapeHtml(ch.title || "")}</h2>
            ${reqText ? `<div class="info-box"><strong style="color:var(--accent-amber)">🔒 Requisitos:</strong> ${escapeHtml(reqText)}</div>` : ""}
            <div class="info-box">
              <div class="panel-title" style="margin-bottom:8px;color:var(--accent-emerald)">📋 Objetivos del Capítulo (${ch.completed_count}/${ch.total_count})</div>
              <div style="display:flex;flex-direction:column;gap:6px">
                ${(ch.objectives || []).map(obj => `
                  <div class="quest-row" style="padding:7px 10px">
                    <button class="btn-check-quest" data-sq="${escapeHtml(obj.id)}" style="${obj.is_completed ? "background:var(--accent-emerald);color:#04120c" : ""}">✓</button>
                    <div style="flex:1;color:${obj.is_completed ? "var(--accent-emerald)" : "var(--text-soft)"};font-size:12.5px">
                      ${escapeHtml(obj.text_es || obj.text || "")}
                      ${obj.optional ? `<span class="kappa-tag" style="margin-left:6px">Opcional</span>` : ""}
                      ${obj.fir ? `<span class="kappa-tag" style="margin-left:6px">FiR</span>` : ""}
                    </div>
                  </div>
                `).join("")}
              </div>
            </div>
            ${(ch.guide_steps || []).length ? `
              <div class="info-box">
                <div class="panel-title" style="margin-bottom:10px;color:var(--accent-gold)">📖 Guía Paso a Paso Completa</div>
                <div style="display:flex;flex-direction:column;gap:12px">
                  ${ch.guide_steps.map(gs => `
                    <div style="padding-bottom:10px;border-bottom:1px solid var(--border-soft)">
                      <strong style="color:var(--text-main);font-size:13.5px">${escapeHtml(gs.title_es || gs.title || "")}</strong>
                      <p style="margin-top:4px;font-size:12.5px;color:var(--text-muted);line-height:1.55">${escapeHtml(gs.walkthrough_es || gs.walkthrough_en || "")}</p>
                      ${(gs.gallery || []).length ? `<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">${gs.gallery.map(im => `<img class="story-gal-img" data-gal-src="${escapeHtml(im.url)}" data-gal-cap="${escapeHtml(im.caption_es || im.caption || gs.title_es || "")}" src="${escapeHtml(im.url)}" title="${escapeHtml(im.caption_es || im.caption || "Click para ampliar")}" style="height:110px;border-radius:8px;border:1px solid var(--border);cursor:zoom-in" loading="lazy" onerror="this.style.display='none'" />`).join("")}</div>` : ""}
                    </div>
                  `).join("")}
                </div>
              </div>
            ` : ""}
            ${rewText ? `<div class="info-box"><strong style="color:var(--accent-blue)">🎁 Recompensas:</strong> ${escapeHtml(rewText)}</div>` : ""}
          </div>
        </div>
      `;
      body.querySelectorAll("[data-ch]").forEach(b => b.addEventListener("click", () => { activeIdx = Number(b.dataset.ch); draw(); }));
      body.querySelectorAll(".story-gal-img").forEach(im => im.addEventListener("click", () => {
        window.openImageLightbox?.(im.dataset.galSrc, `Historia · Cap. ${ch.chapter_number || activeIdx + 1}`, im.dataset.galCap || "");
      }));
      body.querySelectorAll("[data-sq]").forEach(b => b.addEventListener("click", async () => {
        const res = await window.pywebview.api.toggle_story_quest(b.dataset.sq);
        const obj = (ch.objectives || []).find(s => String(s.id) === String(b.dataset.sq));
        if (obj && res?.ok) {
          obj.is_completed = res.is_completed;
          ch.completed_count = (ch.objectives || []).filter(s => s.is_completed).length;
          draw();
        }
      }));
    }
    draw();
  }

  function renderSubtab() {
    if (subtab === "quests") renderQuestsTab();
    else if (subtab === "assortment") renderAssortmentTab();
    else if (subtab === "routes") renderRoutesTab();
    else renderStoryTab();
  }

  renderSubtab();
};
