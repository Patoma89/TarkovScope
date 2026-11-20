/* =====================================================================
   TTC v2.0 — Vistas de Economía & PMC (100% Datos Completos):
   Hideout/FiR/Kappa/Crafteos/Barters/Cultist, Contenedores + SICC vs Docs,
   Medicina/45 Provisiones/14 Efectos Salud, PMC (Skills, Prestige+Reset+Arena,
   Logros, Ropa, Scav Karma+Acciones+BTR+Transits) & Lore Completo
   ===================================================================== */

window.TTCViews = window.TTCViews || {};

/* ================= 1. HIDEOUT, FIR, KAPPA, CRAFTEOS, BARTERS & CULTIST ================= */
window.TTCViews.renderFleaView = async function (container) {
  const data = await window.pywebview.api.get_hideout_and_flea_data();
  let subtab = "hideout"; // hideout | fir | crafts | barters | cultist
  let search = "", hideoutMode = "CORRELATIVE";

  container.innerHTML = `
    <div class="view-header">
      <h1 class="view-title">HIDEOUT, <span>TRUEQUES &amp; ÍTEMS FiR</span></h1>
      <div class="subtabs-bar" id="f-subtabs">
        <button class="subtab-btn active" data-st="hideout">🏭 Hideout (${data.hideout.length})</button>
        <button class="subtab-btn" data-st="fir">📦 Ítems FiR (${data.fir_items.length})</button>
        <button class="subtab-btn" data-st="crafts">⚗️ Crafteos (${data.crafts.length})</button>
        <button class="subtab-btn" data-st="barters">🤝 Trueques (${data.barters.length})</button>
        <button class="subtab-btn" data-st="cultist">🔮 Cultist Circle</button>
      </div>
    </div>
    <div id="flea-body"></div>
  `;

  const body = container.querySelector("#flea-body");
  container.querySelectorAll("#f-subtabs .subtab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      subtab = btn.dataset.st;
      container.querySelectorAll("#f-subtabs .subtab-btn").forEach(b => b.classList.toggle("active", b.dataset.st === subtab));
      render();
    });
  });

  function render() {
    const q = search.trim().toLowerCase();
    if (subtab === "hideout") {
      const mods = data.hideout.filter(m => {
        if (hideoutMode === "CORRELATIVE" && !q && !(m.is_unlocked || m.is_completed)) return false;
        if (q && !`${m.station} ${(m.requirements_lines || []).join(" ")} ${(m.function_lines || []).join(" ")}`.toLowerCase().includes(q)) return false;
        return true;
      });
      body.innerHTML = `
        <div class="glass-card toolbar-row">
          <input class="t-input" id="f-q" value="${escapeHtml(search)}" placeholder="Buscar estación o material del Hideout..." style="flex:1" />
          <select class="t-select" id="f-hmode">
            <option value="CORRELATIVE" ${hideoutMode === "CORRELATIVE" ? "selected" : ""}>Progresión Correlativa</option>
            <option value="ALL" ${hideoutMode === "ALL" ? "selected" : ""}>Todos los 68 niveles</option>
          </select>
        </div>
        <div class="cards-grid-2">
          ${mods.map(m => `
            <div class="glass-card panel-card" style="${m.is_completed ? "border-color:rgba(16,185,129,.5)" : ""}">
              <div style="display:flex;align-items:center;gap:10px">
                <img class="item-thumb-sm" src="${escapeHtml(m.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
                <div style="flex:1">
                  <strong style="color:${m.is_completed ? "var(--accent-emerald)" : "var(--accent-gold)"}">${escapeHtml(m.station)} · Nv.${m.level}/${m.max_level}</strong>
                  <div style="font-size:11px;color:var(--text-muted)">⏱ ${escapeHtml(m.construction_time || "Instant")}</div>
                </div>
                <button class="btn-check-quest" data-hmod="${escapeHtml(m.key)}" style="${m.is_completed ? "background:var(--accent-emerald);color:#04120c" : ""}">✓</button>
              </div>
              <div style="font-size:11.5px;color:var(--text-soft);line-height:1.5"><strong>Requisitos:</strong> ${escapeHtml((m.requirements_lines || []).join(" · "))}</div>
              ${(m.function_lines || []).length ? `<div style="font-size:11px;color:var(--accent-blue)">⚡ ${escapeHtml(m.function_lines.slice(0, 3).join(" · "))}</div>` : ""}
            </div>
          `).join("")}
        </div>
      `;
      body.querySelector("#f-q").addEventListener("input", (e) => { search = e.target.value; render(); });
      body.querySelector("#f-hmode").addEventListener("change", (e) => { hideoutMode = e.target.value; render(); });
      body.querySelectorAll("[data-hmod]").forEach(btn => btn.addEventListener("click", async () => {
        const res = await window.pywebview.api.toggle_hideout_module(btn.dataset.hmod);
        if (res?.ok) {
          const fresh = await window.pywebview.api.get_hideout_and_flea_data();
          data.hideout = fresh.hideout;
          if (res.command_center && window.renderCommandCenter) window.renderCommandCenter(res.command_center);
          render();
        }
      }));
    } else if (subtab === "fir") {
      if (!window._firFilterMode) window._firFilterMode = "all";
      const fMode = window._firFilterMode;
      const doneCount = data.fir_items.filter(x => x.collected >= x.total_required).length;
      const totalItems = data.fir_items.length;
      const pctDone = totalItems ? Math.round((doneCount / totalItems) * 100) : 0;
      const list = data.fir_items.filter(x => {
        const isDone = x.collected >= x.total_required;
        if (fMode === "pending" && isDone) return false;
        if (fMode === "done" && !isDone) return false;
        if (q && !`${x.item_name} ${(x.quests || []).join(" ")}`.toLowerCase().includes(q)) return false;
        return true;
      });
      body.innerHTML = `
        <div class="glass-card panel-card" style="margin-bottom:14px">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">
            <div>
              <div class="panel-title" style="color:var(--accent-gold)">📦 CHECKLIST FOUND IN RAID (FiR)</div>
              <div style="font-size:12px;color:var(--text-muted);margin-top:2px">Controlá en tiempo real qué ítems FiR te faltan para entregar en misiones.</div>
            </div>
            <div style="text-align:right">
              <div style="font-family:var(--font-mono);font-size:18px;font-weight:900;color:var(--accent-emerald)">${doneCount} / ${totalItems} <span style="font-size:12px;color:var(--text-muted)">(${pctDone}%)</span></div>
            </div>
          </div>
          <div class="cc-progress-bar" style="height:9px"><div class="cc-progress-fill" style="width:${pctDone}%"></div></div>
        </div>
        <div class="glass-card toolbar-row">
          <input class="t-input" id="f-q" value="${escapeHtml(search)}" placeholder="Buscar por ítem FiR o nombre de misión..." style="flex:1" />
          <div class="subtabs-bar">
            <button class="subtab-btn ${fMode === "all" ? "active" : ""}" data-fmode="all">Todos (${totalItems})</button>
            <button class="subtab-btn ${fMode === "pending" ? "active" : ""}" data-fmode="pending">Pendientes (${totalItems - doneCount})</button>
            <button class="subtab-btn ${fMode === "done" ? "active" : ""}" data-fmode="done">Completos (${doneCount})</button>
          </div>
        </div>
        <div class="cards-grid-3">
          ${list.map(x => {
            const isDone = x.collected >= x.total_required;
            const pct = Math.min(100, Math.round((x.collected / Math.max(1, x.total_required)) * 100));
            return `
              <div class="glass-card panel-card" style="${isDone ? "border-color:rgba(16,185,129,.55);background:linear-gradient(180deg, rgba(16,185,129,.08), rgba(10,16,14,.8))" : ""}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px">
                  <strong style="color:${isDone ? "var(--accent-emerald)" : "var(--text-main)"};font-size:13.5px;line-height:1.25">${escapeHtml(x.item_name)}</strong>
                  <span class="kappa-tag" style="${isDone ? "color:var(--accent-emerald);border-color:rgba(16,185,129,.5);background:rgba(16,185,129,.15)" : ""}">${isDone ? "✓ LISTO" : `Faltan ${x.total_required - x.collected}`}</span>
                </div>
                <div class="cc-progress-bar" style="height:6px;margin:4px 0"><div class="cc-progress-fill" style="width:${pct}%"></div></div>
                <div style="display:flex;align-items:center;justify-content:space-between;gap:6px">
                  <div style="display:flex;align-items:center;gap:5px">
                    <button class="btn-ghost-sm" data-fir-dec="${escapeHtml(x.item_name)}" style="height:26px;width:28px;padding:0">−</button>
                    <span style="font-family:var(--font-mono);font-size:13px;font-weight:900;min-width:44px;text-align:center;color:${isDone ? "var(--accent-emerald)" : "var(--accent-gold)"}">${x.collected}/${x.total_required}</span>
                    <button class="btn-ghost-sm" data-fir-inc="${escapeHtml(x.item_name)}" style="height:26px;width:28px;padding:0">＋</button>
                  </div>
                  <button class="btn-ghost-sm" data-fir-max="${escapeHtml(x.item_name)}" style="height:26px;font-size:11px;padding:0 9px;color:${isDone ? "var(--text-muted)" : "var(--accent-emerald)"}">${isDone ? "↺ 0" : "✓ Max"}</button>
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px">
                  ${(x.quests || []).slice(0, 4).map(qn => `<span style="font-size:10.5px;padding:2px 6px;border-radius:5px;background:rgba(255,255,255,0.05);color:var(--text-muted);border:1px solid var(--border-soft)">${escapeHtml(qn)}</span>`).join("")}
                  ${(x.quests || []).length > 4 ? `<span style="font-size:10.5px;color:var(--text-dim)">+${x.quests.length - 4} más</span>` : ""}
                </div>
              </div>
            `;
          }).join("")}
        </div>
      `;
      body.querySelector("#f-q").addEventListener("input", (e) => { search = e.target.value; render(); });
      body.querySelectorAll("[data-fmode]").forEach(b => b.addEventListener("click", () => { window._firFilterMode = b.dataset.fmode; render(); }));
      const setFir = async (name, targetVal) => {
        const it = data.fir_items.find(i => i.item_name === name);
        if (!it) return;
        const r = await window.pywebview.api.set_fir_stash_count(name, Math.max(0, targetVal));
        if (r?.ok) { it.collected = r.count; render(); }
      };
      body.querySelectorAll("[data-fir-inc]").forEach(b => b.addEventListener("click", () => {
        const it = data.fir_items.find(i => i.item_name === b.dataset.firInc);
        if (it) setFir(it.item_name, it.collected + 1);
      }));
      body.querySelectorAll("[data-fir-dec]").forEach(b => b.addEventListener("click", () => {
        const it = data.fir_items.find(i => i.item_name === b.dataset.firDec);
        if (it) setFir(it.item_name, it.collected - 1);
      }));
      body.querySelectorAll("[data-fir-max]").forEach(b => b.addEventListener("click", () => {
        const it = data.fir_items.find(i => i.item_name === b.dataset.firMax);
        if (it) setFir(it.item_name, it.collected >= it.total_required ? 0 : it.total_required);
      }));
    } else if (subtab === "crafts") {
      const list = data.crafts.filter(c => !q || `${c.output} ${c.station} ${c.inputs} ${c.usage}`.toLowerCase().includes(q));
      body.innerHTML = `
        <div class="glass-card toolbar-row"><input class="t-input" id="f-q" value="${escapeHtml(search)}" placeholder="Buscar crafteo FiR..." style="flex:1" /></div>
        <div class="cards-grid-2">${list.map(c => `
          <div class="glass-card panel-card" style="flex-direction:row;align-items:center">
            <img class="item-thumb-sm" src="${escapeHtml(c.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
            <div style="flex:1">
              <strong style="color:var(--accent-gold)">${escapeHtml(c.output)}</strong>
              <div style="font-size:11px;color:var(--accent-emerald)">🏭 ${escapeHtml(c.station)} Nv.${c.level} · ${escapeHtml(c.category)}</div>
              <div style="font-size:11.5px;color:var(--text-soft);margin-top:3px">Pide: ${escapeHtml(c.inputs)}</div>
              ${c.usage ? `<div style="font-size:11px;color:var(--text-muted)">Uso: ${escapeHtml(c.usage)}</div>` : ""}
            </div>
          </div>
        `).join("")}</div>
      `;
      body.querySelector("#f-q").addEventListener("input", (e) => { search = e.target.value; render(); });
    } else if (subtab === "barters") {
      const list = data.barters.filter(b => !q || `${b.reward} ${b.inputs_text} ${b.trader}`.toLowerCase().includes(q));
      body.innerHTML = `
        <div class="glass-card toolbar-row"><input class="t-input" id="f-q" value="${escapeHtml(search)}" placeholder="Buscar entre los ${data.barters.length} trueques..." style="flex:1" /><span class="hud-chip">${list.length} trueques</span></div>
        <div class="cards-grid-2">${list.map(b => `
          <div class="glass-card panel-card" style="flex-direction:row;align-items:center">
            <img class="item-thumb-sm" src="${escapeHtml(b.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
            <div style="flex:1;min-width:0">
              <strong style="color:var(--text-main)">${escapeHtml(b.reward)}</strong>
              <div style="font-size:11px;color:var(--accent-gold)">${escapeHtml(b.trader)} LL${b.ll} ${b.quest_unlock ? `· 🔒 ${escapeHtml(b.quest_unlock)}` : ""}</div>
              <div style="font-size:11.5px;color:var(--text-muted)">Pide: ${escapeHtml(b.inputs_text)}</div>
            </div>
          </div>
        `).join("")}</div>
      `;
      body.querySelector("#f-q").addEventListener("input", (e) => { search = e.target.value; render(); });
    } else {
      const cinfo = data.cultist.info || {};
      body.innerHTML = `
        <div class="glass-card panel-card" style="margin-bottom:14px">
          <div class="panel-title" style="color:var(--accent-gold)">🔮 Umbrales Oficiales del Círculo Cultista (Máx. ${cinfo.max_slots || 5} ítems)</div>
          <div class="cards-grid-3">
            ${(cinfo.thresholds || []).map(t => `<div class="info-box"><strong style="color:var(--accent-emerald)">${escapeHtml(typeof t === "string" ? t : `${t.value || t.threshold || ""}`)}</strong><div style="font-size:11.5px;color:var(--text-soft);margin-top:3px">${escapeHtml(typeof t === "string" ? "" : (t.effect || t.result || t.notes || ""))}</div></div>`).join("")}
          </div>
          ${(cinfo.tips || []).length ? `<div style="font-size:12px;color:var(--text-muted)">💡 ${escapeHtml(cinfo.tips.join(" · "))}</div>` : ""}
        </div>
        <div class="cards-grid-2">
          <div class="glass-card panel-card">
            <div class="panel-title" style="color:var(--accent-purple)">🔮 Sacrificios Únicos (1 vez por Wipe)</div>
            ${(data.cultist.unique || []).map(s => `<div class="info-box"><strong style="color:var(--accent-gold)">${escapeHtml(s.input)}</strong> → ${escapeHtml(s.outcome)} <span style="color:var(--text-muted)">(${escapeHtml(s.duration)})</span></div>`).join("")}
          </div>
          <div class="glass-card panel-card">
            <div class="panel-title" style="color:var(--accent-emerald)">♻️ Sacrificios Repetibles</div>
            ${(data.cultist.repeatable || []).map(s => `<div class="info-box"><strong style="color:var(--accent-gold)">${escapeHtml(s.input)}</strong> → ${escapeHtml(s.outcome)} <span style="color:var(--text-muted)">(${escapeHtml(s.duration)})</span></div>`).join("")}
          </div>
        </div>
      `;
    }
  }
  render();
};

/* ================= 2. CONTENEDORES, RIGS & MOCHILAS (+ SICC vs DOCS) ================= */
window.TTCViews.renderContainersView = async function (container) {
  const data = await window.pywebview.api.get_containers_data();
  let q = "", cat = "Todos", only2x2 = false, selId = data.items[0]?.id || "";
  const cats = ["Todos", ...new Set(data.items.map(i => i.category))];

  function render() {
    const ql = q.trim().toLowerCase();
    const list = data.items.filter(i => (cat === "Todos" || i.category === cat) && (!only2x2 || i.has_2x2) && (!ql || `${i.name} ${i.holds || ""}`.toLowerCase().includes(ql)));
    if (list.length && !list.some(i => i.id === selId)) selId = list[0].id;
    const cur = list.find(i => i.id === selId) || list[0];

    container.innerHTML = `
      <div class="view-header"><h1 class="view-title">CONTENEDORES, <span>RIGS &amp; MOCHILAS</span></h1></div>
      <div class="glass-card toolbar-row">
        <input class="t-input" id="c-q" value="${escapeHtml(q)}" placeholder="Buscar Kappa, SICC, Docs, mochila o rig..." style="flex:1" />
        <select class="t-select" id="c-cat">${cats.map(c => `<option value="${escapeHtml(c)}" ${c === cat ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}</select>
        <button class="btn-ghost-sm ${only2x2 ? "active" : ""}" id="c-2x2">Solo con espacio 2×2</button>
        <span class="hud-chip">${list.length} ítems</span>
      </div>
      <div class="split-layout">
        <div class="glass-card split-list">
          ${list.map(it => `
            <button class="list-item-card ${it.id === selId ? "active" : ""}" data-cid="${escapeHtml(it.id)}">
              <img class="item-thumb-sm" src="${escapeHtml(it.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
              <div style="flex:1;min-width:0">
                <div style="font-weight:700;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${escapeHtml(it.name)}</div>
                <div style="font-size:11px;color:var(--accent-gold)">${it.slots} slots · Efic ${it.efficiency}x · ${escapeHtml(it.category)}</div>
              </div>
            </button>
          `).join("")}
        </div>
        <div class="glass-card split-detail">
          ${cur ? `
            <div style="display:flex;align-items:center;gap:14px">
              <img src="${escapeHtml(cur.icon_url)}" style="width:82px;height:82px;object-fit:contain;background:var(--bg-darkest);border-radius:10px;padding:6px;border:1px solid var(--border)" onerror="this.style.display='none'" />
              <div>
                <h2 style="font-family:var(--font-display);font-size:22px;color:var(--accent-gold)">${escapeHtml(cur.name)}</h2>
                <div style="font-size:12.5px;color:var(--text-muted)">${escapeHtml(cur.category)} · ${cur.has_2x2 ? "Tiene espacio 2×2" : ""}</div>
              </div>
            </div>
            <div class="stat-grid-4">
              <div class="stat-tile"><div class="stat-tile-lbl">Capacidad</div><div class="stat-tile-val">${cur.slots} slots</div></div>
              <div class="stat-tile"><div class="stat-tile-lbl">Tamaño Externo</div><div class="stat-tile-val" style="color:var(--accent-blue)">${escapeHtml(cur.external_grid || "—")}</div></div>
              <div class="stat-tile"><div class="stat-tile-lbl">Eficiencia</div><div class="stat-tile-val" style="color:var(--accent-emerald)">${cur.efficiency}x</div></div>
              <div class="stat-tile"><div class="stat-tile-lbl">Peso</div><div class="stat-tile-val" style="color:var(--accent-amber)">${cur.weight_kg ?? "—"} kg</div></div>
            </div>
            <div class="info-box"><strong style="color:var(--accent-gold)">📦 Qué puede guardar / Cómo obtenerlo:</strong><div style="margin-top:4px;color:var(--text-soft)">${escapeHtml(cur.holds || cur.layout || "—")}</div></div>
            <div class="info-box"><strong style="color:var(--accent-blue)">⚖️ Comparativa SICC vs Documents Case:</strong>
              <div style="margin-top:6px;display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--text-soft)">
                ${(data.sicc_vs_docs || []).map(row => `<div><strong>${escapeHtml(row.aspect || row.feature || "")}:</strong> SICC: ${escapeHtml(row.sicc || "")} · Docs: ${escapeHtml(row.docs || "")}</div>`).join("")}
              </div>
            </div>
          ` : ""}
        </div>
      </div>
    `;
    container.querySelector("#c-q").addEventListener("input", (e) => { q = e.target.value; render(); });
    container.querySelector("#c-cat").addEventListener("change", (e) => { cat = e.target.value; render(); });
    container.querySelector("#c-2x2").addEventListener("click", () => { only2x2 = !only2x2; render(); });
    container.querySelectorAll("[data-cid]").forEach(b => b.addEventListener("click", () => { selId = b.dataset.cid; render(); }));
  }
  render();
};

/* ================= 3. MEDICINA, 45 PROVISIONES & 14 EFECTOS SALUD ================= */
window.TTCViews.renderMedicalView = async function (container) {
  const data = await window.pywebview.api.get_medical_and_provisions_data();
  let subtab = "medical", q = "", mcat = "Todas";

  container.innerHTML = `
    <div class="view-header">
      <h1 class="view-title">MEDICINA, <span>PROVISIONES &amp; SALUD</span></h1>
      <div class="subtabs-bar" id="m-subtabs">
        <button class="subtab-btn active" data-st="medical">💉 Medicina &amp; Stims (${data.medical.length})</button>
        <button class="subtab-btn" data-st="provisions">🥫 Provisiones (${data.provisions.length})</button>
        <button class="subtab-btn" data-st="health">❤️ Efectos de Salud (${data.health_effects.length})</button>
      </div>
    </div>
    <div id="med-body"></div>
  `;

  const body = container.querySelector("#med-body");
  container.querySelectorAll("#m-subtabs .subtab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      subtab = btn.dataset.st;
      container.querySelectorAll("#m-subtabs .subtab-btn").forEach(b => b.classList.toggle("active", b.dataset.st === subtab));
      render();
    });
  });

  function render() {
    const ql = q.trim().toLowerCase();
    if (subtab === "medical") {
      const list = data.medical.filter(m => (mcat === "Todas" || m.category === mcat) && (!ql || `${m.name} ${m.cures_label} ${m.category} ${m.positive_effects}`.toLowerCase().includes(ql)));
      body.innerHTML = `
        <div class="glass-card toolbar-row">
          <input class="t-input" id="m-q" value="${escapeHtml(q)}" placeholder="Buscar medkit, stim (SJ6, Propital, MULE) o síntoma..." style="flex:1" />
          <select class="t-select" id="m-cat">${(data.categories || ["Todas"]).map(c => `<option value="${escapeHtml(c)}" ${c === mcat ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}</select>
        </div>
        <div class="cards-grid-2">${list.map(m => `
          <div class="glass-card panel-card">
            <div style="display:flex;align-items:center;gap:12px">
              <img class="item-thumb-sm" src="${escapeHtml(m.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
              <div>
                <strong style="color:var(--accent-gold);font-size:14.5px">${escapeHtml(m.name)}</strong>
                <div style="font-size:11px;color:var(--accent-emerald)">${escapeHtml(m.category)} · ${escapeHtml(m.uses)} · ⏱ ${escapeHtml(m.use_time)}</div>
              </div>
            </div>
            <div style="font-size:12px;color:var(--text-soft)"><strong>Cura / Efecto:</strong> ${escapeHtml(m.cures_label || "")}</div>
            <div style="font-size:11.5px;color:var(--accent-emerald)">✓ ${escapeHtml(m.positive_effects || "")}</div>
            ${m.negative_effects ? `<div style="font-size:11.5px;color:var(--accent-red)">⚠ ${escapeHtml(m.negative_effects)}</div>` : ""}
            ${m.tactical_tip ? `<div style="font-size:11.5px;color:var(--text-muted)">💡 ${escapeHtml(m.tactical_tip)}</div>` : ""}
          </div>
        `).join("")}</div>
      `;
      body.querySelector("#m-q").addEventListener("input", (e) => { q = e.target.value; render(); });
      body.querySelector("#m-cat").addEventListener("change", (e) => { mcat = e.target.value; render(); });
    } else if (subtab === "provisions") {
      const list = data.provisions.filter(p => !ql || `${p.name} ${p.category} ${p.buffs_es} ${p.fir_usage_es || ""}`.toLowerCase().includes(ql));
      body.innerHTML = `
        <div class="glass-card toolbar-row"><input class="t-input" id="m-q" value="${escapeHtml(q)}" placeholder="Buscar comida, bebida, Moonshine o uso FiR..." style="flex:1" /></div>
        <div class="cards-grid-3">${list.map(p => `
          <div class="glass-card panel-card">
            <div style="display:flex;align-items:center;gap:10px">
              <img class="item-thumb-sm" src="${escapeHtml(p.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
              <div>
                <strong style="color:var(--accent-gold);font-size:13px">${escapeHtml(p.name)}</strong>
                <div style="font-size:11px;color:var(--text-muted)">⚡ ${p.energy >= 0 ? "+" : ""}${p.energy} En · 💧 ${p.hydration >= 0 ? "+" : ""}${p.hydration} Hid · ⏱ ${p.use_time}s</div>
              </div>
            </div>
            <div style="font-size:11.5px;color:var(--text-soft)">${escapeHtml(p.buffs_es || "")}</div>
            ${p.fir_usage_es ? `<div style="font-size:11px;color:var(--accent-amber)">📦 ${escapeHtml(p.fir_usage_es)}</div>` : ""}
          </div>
        `).join("")}</div>
      `;
      body.querySelector("#m-q").addEventListener("input", (e) => { q = e.target.value; render(); });
    } else {
      body.innerHTML = `<div class="cards-grid-2">${data.health_effects.map(h => `
        <div class="glass-card panel-card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <strong style="color:var(--accent-gold);font-size:15px">${escapeHtml(h.name_es || h.name)}</strong>
            <span class="kappa-tag">${escapeHtml(h.severity || "")}</span>
          </div>
          <div style="font-size:12px;color:var(--text-muted)"><strong>Causas:</strong> ${escapeHtml(h.causes_es || "")}</div>
          <div style="font-size:12px;color:var(--text-soft)"><strong>Impacto:</strong> ${escapeHtml(h.impact_es || "")}</div>
          <div class="info-box" style="font-size:12px;color:var(--accent-emerald)">💊 <strong>Mejores Curas:</strong> ${escapeHtml(Array.isArray(h.best_cures) ? h.best_cures.join(" · ") : (h.best_cures || ""))}</div>
        </div>
      `).join("")}</div>`;
    }
  }
  render();
};

/* ================= 4. PMC SYSTEMS (SKILLS, PRESTIGE, LOGROS, ROPA, KARMA/BTR) ================= */
window.TTCViews.renderPMCView = async function (container) {
  const data = await window.pywebview.api.get_pmc_systems_data();
  let subtab = "skills", skillCat = "Todas", clothFac = "Todos";
  let achQuery = "", achCat = "Todos";

  container.innerHTML = `
    <div class="view-header">
      <h1 class="view-title">PMC, <span>SKILLS, PRESTIGE &amp; LOGROS</span></h1>
      <div class="subtabs-bar" id="p-subtabs">
        <button class="subtab-btn active" data-st="skills">📈 Skills (${data.skills.length})</button>
        <button class="subtab-btn" data-st="prestige">🏆 Prestige 1–6</button>
        <button class="subtab-btn" data-st="achievements">🎖️ Logros (${data.achievements.length})</button>
        <button class="subtab-btn" data-st="clothing">👕 Ropa (${data.clothing.length})</button>
        <button class="subtab-btn" data-st="karma">⚖️ Karma, BTR &amp; Transits</button>
      </div>
    </div>
    <div id="pmc-body"></div>
  `;

  const body = container.querySelector("#pmc-body");
  container.querySelectorAll("#p-subtabs .subtab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      subtab = btn.dataset.st;
      container.querySelectorAll("#p-subtabs .subtab-btn").forEach(b => b.classList.toggle("active", b.dataset.st === subtab));
      render();
    });
  });

  function render() {
    if (subtab === "skills") {
      const cats = ["Todas", ...new Set(data.skills.map(s => s.category))];
      const list = data.skills.filter(s => skillCat === "Todas" || s.category === skillCat);
      body.innerHTML = `
        <div class="glass-card toolbar-row">
          <div class="subtabs-bar">${cats.map(c => `<button class="subtab-btn ${skillCat === c ? "active" : ""}" data-scat="${escapeHtml(c)}">${escapeHtml(c)}</button>`).join("")}</div>
        </div>
        <div class="cards-grid-2">${list.map(s => `
          <div class="glass-card panel-card">
            <div style="display:flex;align-items:center;gap:10px">
              <img class="item-thumb-sm" src="${escapeHtml(s.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
              <div>
                <strong style="color:var(--accent-gold);font-size:14.5px">${escapeHtml(s.name)}</strong>
                <div style="font-size:11px;color:var(--accent-blue)">${escapeHtml(s.category)} · ${escapeHtml(s.requirements || "")}</div>
              </div>
            </div>
            <div style="font-size:11.5px;color:var(--text-soft);white-space:pre-line">${escapeHtml(s.effects || "")}</div>
            <div class="info-box" style="font-size:11.5px;color:var(--accent-emerald);white-space:pre-line"><strong>⭐ Perk Élite Nv.51:</strong>\n${escapeHtml(s.elite_perk || "")}</div>
            <div style="font-size:11.5px;color:var(--text-muted);white-space:pre-line"><strong>📈 Cómo subirla:</strong>\n${escapeHtml(s.how_to_level || "")}</div>
          </div>
        `).join("")}</div>
      `;
      body.querySelectorAll("[data-scat]").forEach(b => b.addEventListener("click", () => { skillCat = b.dataset.scat; render(); }));
    } else if (subtab === "prestige") {
      const rm = data.prestige_reset_matrix || {};
      body.innerHTML = `
        <div class="glass-card toolbar-row" style="justify-content:space-between">
          <strong style="color:var(--accent-gold)">Tu Nivel de Prestige Actual: P${data.prestige_level}</strong>
          <div class="subtabs-bar">${[0, 1, 2, 3, 4, 5, 6].map(lv => `<button class="subtab-btn ${data.prestige_level === lv ? "active" : ""}" data-plv="${lv}">P${lv}</button>`).join("")}</div>
        </div>
        <div class="cards-grid-2" style="margin-bottom:14px">${data.prestige_levels.map(p => `
          <div class="glass-card panel-card">
            <div style="display:flex;align-items:center;gap:12px">
              <img class="item-thumb-sm" src="${escapeHtml(p.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
              <div><strong style="color:var(--accent-gold);font-size:15px">${escapeHtml(p.title_es)}</strong><div style="font-size:11.5px;color:var(--text-muted)">${escapeHtml(p.summary_es)}</div></div>
            </div>
            <ul style="margin-left:16px;font-size:12px;color:var(--text-soft);line-height:1.45">${(p.requirements_es || []).map(r => `<li>${escapeHtml(r)}</li>`).join("")}</ul>
            <div class="info-box" style="font-size:11.5px;color:var(--accent-emerald)"><strong>🎁 Recompensas:</strong><ul style="margin:4px 0 0 16px">${(p.rewards_es || []).map(r => `<li>${escapeHtml(r)}</li>`).join("")}</ul></div>
          </div>
        `).join("")}</div>
        <div class="cards-grid-2">
          <div class="glass-card panel-card">
            <div class="panel-title" style="color:var(--accent-emerald)">✓ Qué se CONSERVA al hacer Prestige</div>
            <ul style="margin-left:16px;font-size:12px;color:var(--text-soft);line-height:1.5">${(rm.kept || []).map(x => `<li>${escapeHtml(typeof x === "string" ? x : (x.es || x.title_es || ""))}</li>`).join("")}</ul>
          </div>
          <div class="glass-card panel-card">
            <div class="panel-title" style="color:var(--accent-red)">✕ Qué se REINICIA al hacer Prestige</div>
            <ul style="margin-left:16px;font-size:12px;color:var(--text-soft);line-height:1.5">${(rm.reset || []).map(x => `<li>${escapeHtml(typeof x === "string" ? x : (x.es || x.title_es || ""))}</li>`).join("")}</ul>
          </div>
        </div>
      `;
      body.querySelectorAll("[data-plv]").forEach(btn => btn.addEventListener("click", async () => {
        const res = await window.pywebview.api.set_prestige_lvl(Number(btn.dataset.plv));
        if (res?.ok) {
          data.prestige_level = res.prestige_level;
          if (res.command_center && window.renderCommandCenter) window.renderCommandCenter(res.command_center);
          render();
          showToast(`👑 Prestige actualizado a P${res.prestige_level}`);
        }
      }));
    } else if (subtab === "achievements") {
      const aCats = ["Todos", ...new Set(data.achievements.map(a => a.category))];
      const aq = achQuery.trim().toLowerCase();
      const filteredAchs = data.achievements.filter(a => {
        if (achCat !== "Todos" && a.category !== achCat) return false;
        if (aq && !`${a.name} ${a.condition_es} ${a.condition_en} ${a.category} ${a.rarity} ${a.reward}`.toLowerCase().includes(aq)) return false;
        return true;
      });
      const unlockedCnt = data.achievements.filter(a => a.unlocked).length;
      body.innerHTML = `
        <div class="glass-card toolbar-row">
          <input class="t-input" id="ach-q" value="${escapeHtml(achQuery)}" placeholder="Buscar entre los ${data.achievements.length} logros oficiales (Wiki / Steam)..." style="flex:1" />
          <select class="t-select" id="ach-cat">${aCats.map(c => `<option value="${escapeHtml(c)}" ${achCat === c ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}</select>
          <span class="hud-chip" style="color:var(--accent-emerald)">${unlockedCnt}/${data.achievements.length}</span>
        </div>
        <div class="cards-grid-2">${filteredAchs.map(a => `
          <div class="glass-card panel-card" style="${a.unlocked ? "border-color:rgba(16,185,129,.5)" : ""}">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:10px">
              <div>
                <strong style="color:${a.unlocked ? "var(--accent-emerald)" : "var(--accent-gold)"}">${escapeHtml(a.name)}</strong>
                <div style="font-size:11px;color:var(--text-muted)">${escapeHtml(a.category)} · ${escapeHtml(a.rarity)} (${a.pct_players}%) · 🎁 ${escapeHtml(a.reward || "")}</div>
              </div>
              <button class="btn-check-quest" data-ach="${escapeHtml(a.id)}" style="${a.unlocked ? "background:var(--accent-emerald);color:#04120c" : ""}">✓</button>
            </div>
            <div style="font-size:12px;color:var(--text-soft)">${escapeHtml(window.TTC_LANG === "en" ? (a.condition_en || a.condition_es) : a.condition_es)}</div>
            <div style="font-size:11.5px;color:var(--text-muted)">💡 ${escapeHtml(window.TTC_LANG === "en" ? (a.tip_en || a.tip_es || "") : (a.tip_es || ""))}</div>
          </div>
        `).join("")}</div>`;
      body.querySelector("#ach-q")?.addEventListener("input", (e) => { achQuery = e.target.value; render(); });
      body.querySelector("#ach-cat")?.addEventListener("change", (e) => { achCat = e.target.value; render(); });
      body.querySelectorAll("[data-ach]").forEach(btn => btn.addEventListener("click", async () => {
        const res = await window.pywebview.api.toggle_achievement(btn.dataset.ach);
        const item = data.achievements.find(x => x.id === btn.dataset.ach);
        if (item && res?.ok) {
          item.unlocked = res.unlocked;
          if (res.command_center && window.renderCommandCenter) window.renderCommandCenter(res.command_center);
          render();
        }
      }));
    } else if (subtab === "clothing") {
      const list = data.clothing.filter(c => clothFac === "Todos" || c.faction === clothFac);
      body.innerHTML = `
        <div class="glass-card toolbar-row">
          <div class="subtabs-bar">${["Todos", "USEC", "BEAR"].map(f => `<button class="subtab-btn ${clothFac === f ? "active" : ""}" data-cfac="${f}">${f}</button>`).join("")}</div>
        </div>
        <div class="cards-grid-2">${list.map(c => `
          <div class="glass-card panel-card" style="flex-direction:row;align-items:center">
            <img class="item-thumb-sm" src="${escapeHtml(c.icon_url)}" style="width:60px;height:60px" loading="lazy" onerror="this.style.visibility='hidden'" />
            <div style="flex:1">
              <strong style="color:var(--accent-gold);font-size:14px">${escapeHtml(c.name)}</strong>
              <div style="font-size:11.5px;color:var(--accent-blue)">${escapeHtml(c.faction)} · ${escapeHtml(c.slot)} · Nv.${c.pmc_level} · ${escapeHtml(c.trader_req)} · ${escapeHtml(c.price_text)}</div>
              <div style="font-size:11.5px;color:var(--text-soft);margin-top:3px">${escapeHtml(c.camo_notes_es || "")}</div>
            </div>
          </div>
        `).join("")}</div>
      `;
      body.querySelectorAll("[data-cfac]").forEach(b => b.addEventListener("click", () => { clothFac = b.dataset.cfac; render(); }));
    } else if (subtab === "karma") {
      const btr = data.btr_service || {};
      body.innerHTML = `
        <div class="cards-grid-2" style="margin-bottom:14px">
          <div class="glass-card panel-card">
            <div class="panel-title" style="color:var(--accent-gold)">⚖️ Rangos de Scav Karma (Fence)</div>
            ${(data.scav_karma_brackets || []).map(b => `<div class="info-box"><strong style="color:var(--accent-gold)">${escapeHtml(b.karma)}</strong> · BTR: <span style="color:var(--accent-blue)">${escapeHtml(b.btr)}</span> · Grilla: ${escapeHtml(b.transit_grid)}<div style="font-size:11.5px;color:var(--text-soft);margin-top:3px">${escapeHtml(b.effects)}</div></div>`).join("")}
          </div>
          <div class="glass-card panel-card">
            <div class="panel-title" style="color:var(--accent-emerald)">📊 Acciones de Scav Karma</div>
            ${(data.scav_karma_actions || []).map(a => `<div class="info-box"><strong style="color:var(--text-main)">${escapeHtml(a.action)}</strong> <span style="color:var(--accent-gold);font-weight:800">(${escapeHtml(a.change)})</span><div style="font-size:11.5px;color:var(--text-muted)">${escapeHtml(a.notes || "")}</div></div>`).join("")}
          </div>
        </div>
        <div class="cards-grid-2">
          <div class="glass-card panel-card">
            <div class="panel-title" style="color:var(--accent-amber)">🚐 Servicio BTR Driver (${escapeHtml((btr.maps || []).join(" · "))})</div>
            <div style="font-size:12px;color:var(--text-soft)">${escapeHtml(btr.unlock_note || "")}</div>
            ${(btr.services || []).map(sv => `<div class="info-box"><strong style="color:var(--accent-gold)">${escapeHtml(sv.name || sv.service || "")}</strong> — ${escapeHtml(sv.cost || sv.price || "")}<div style="font-size:11.5px;color:var(--text-muted)">${escapeHtml(sv.notes || sv.desc || "")}</div></div>`).join("")}
            <div style="font-size:11.5px;color:var(--accent-red)">⚠️ ${escapeHtml(btr.hostile_rule || "")}</div>
          </div>
          <div class="glass-card panel-card">
            <div class="panel-title" style="color:var(--accent-blue)">🔀 Red Completa de Transits (${(data.transits || []).length})</div>
            <div style="max-height:420px;overflow-y:auto;display:flex;flex-direction:column;gap:6px">
              ${(data.transits || []).map(t => `<div class="info-box"><strong style="color:var(--accent-gold)">${escapeHtml(t.from_map)} → ${escapeHtml(t.to_map)}</strong> (${escapeHtml(t.name || "")})<div style="font-size:11.5px;color:var(--text-muted)">${escapeHtml(t.faction || "")} · ${escapeHtml(t.notes || "")}</div></div>`).join("")}
            </div>
          </div>
        </div>
      `;
    }
  }
  render();
};

/* ================= 5. EXTRAS: LORE & UNIVERSO DE TARKOV ================= */
window.TTCViews.renderLoreView = async function (container) {
  const data = await window.pywebview.api.get_pmc_systems_data();
  const isEn = window.TTC_LANG === "en";
  container.innerHTML = `
    <div class="view-header">
      <h1 class="view-title">LORE <span>&amp; UNIVERSO DE TARKOV</span></h1>
      <span class="hud-chip">${(data.lore || []).length} dossiers</span>
    </div>
    <div class="cards-grid-2">
      ${(data.lore || []).map(l => `
        <div class="glass-card panel-card">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
            <strong style="color:var(--accent-gold);font-size:16px">${escapeHtml(l.title || "")}</strong>
            ${l.date_str ? `<span class="kappa-tag">${escapeHtml(l.date_str)}</span>` : ""}
          </div>
          <div style="font-size:12px;color:var(--accent-blue);font-weight:700">${escapeHtml(isEn ? (l.subtitle_en || l.subtitle_es || "") : (l.subtitle_es || ""))}</div>
          ${(l.highlights || []).length ? `<ul style="margin-left:16px;font-size:12px;color:var(--accent-emerald);line-height:1.45">${l.highlights.map(h => `<li>${escapeHtml(h)}</li>`).join("")}</ul>` : ""}
          <div style="font-size:12.5px;color:var(--text-soft);line-height:1.6;white-space:pre-line">${escapeHtml(isEn ? (l.narrative_en || l.narrative_es || "") : (l.narrative_es || ""))}</div>
        </div>
      `).join("")}
    </div>
  `;
};

/* ================= 6. DOCS DEL PASE DE TEMPORADA (MAPAS INTERACTIVOS KORDMAP.WIKI) ================= */
window.TTCViews.renderSeasonDocsView = async function (container) {
  const data = await window.pywebview.api.get_season_pass_docs_data();
  let viewMode = "interactive"; // interactive (kordmap.wiki embebido) | offline
  let mapFilter = "Todos";

  function render() {
    const meta = data.meta || {};
    const allMaps = ["Todos", ...(data.map_guides || []).map(g => g.map)];
    const visibleDocs = (data.docs || []).filter(d => mapFilter === "Todos" || (d.maps || []).includes(mapFilter) || d.id === "classified_docs");
    const visibleMapGuides = (data.map_guides || []).filter(g => mapFilter === "Todos" || g.map === mapFilter);

    container.innerHTML = `
      <div class="view-header" style="margin-bottom:10px">
        <div>
          <h1 class="view-title">KORD <span>BREACH</span></h1>
          <div style="font-size:12px;color:var(--text-muted)">Mapas interactivos con ubicaciones exactas · Caché persistente activado · Límite diario: Seasonal 40 · PvP 25 · PvE 15</div>
        </div>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <div class="subtabs-bar">
            <button class="subtab-btn ${viewMode === "interactive" ? "active" : ""}" id="bp-mode-live">🗺️ Mapa Interactivo (kordmap.wiki)</button>
            <button class="subtab-btn ${viewMode === "offline" ? "active" : ""}" id="bp-mode-off">📋 Guía Offline por Mapa</button>
          </div>
          ${viewMode === "interactive" ? `<button class="btn-ghost-sm" id="bp-reload-iframe">⟳ Recargar</button>` : ""}
          <button class="btn-ghost-sm" data-bp-ext="https://kordmap.wiki/">kordmap.wiki ↗</button>
          <button class="btn-ghost-sm" data-bp-ext="https://tarkovdocsmap.com/">tarkovdocsmap.com ↗</button>
        </div>
      </div>

      ${viewMode === "interactive" ? `
        <div class="glass-card" style="padding:0;overflow:hidden;height:calc(100vh - 165px);min-height:560px;border:1px solid rgba(var(--accent-gold-rgb),0.35)">
          <iframe id="kordmap-iframe" src="https://kordmap.wiki/" style="width:100%;height:100%;border:0;background:#090c12" allow="fullscreen" referrerpolicy="no-referrer"></iframe>
        </div>
      ` : `
        <div class="glass-card toolbar-row">
          <select class="t-select" id="bp-map-sel">
            ${allMaps.map(m => `<option value="${escapeHtml(m)}" ${m === mapFilter ? "selected" : ""}>🗺️ ${escapeHtml(m)}</option>`).join("")}
          </select>
          <span style="font-size:12px;color:var(--text-muted)">💡 ${escapeHtml(meta.personal_loot_note_es || "")}</span>
        </div>

        <div class="cards-grid-2" style="margin-bottom:14px">
          ${visibleMapGuides.map(g => {
            const docBadges = (g.doc_ids || []).map(did => {
              const obj = (data.docs || []).find(x => x.id === did);
              return obj ? `<span class="kappa-tag" style="border-color:${escapeHtml(obj.color)};color:${escapeHtml(obj.color)};background:rgba(255,255,255,0.04)">${escapeHtml(obj.name_es)}</span>` : "";
            }).join(" ");
            return `
              <div class="glass-card panel-card">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
                  <strong style="color:var(--accent-gold);font-size:15px">📍 ${escapeHtml(g.map)}</strong>
                  <div style="display:flex;gap:4px;flex-wrap:wrap">${docBadges}</div>
                </div>
                <div style="font-size:12.5px;color:var(--text-soft);line-height:1.5">${escapeHtml(g.route_tip_es)}</div>
              </div>
            `;
          }).join("")}
        </div>

        <div class="cards-grid-3">
          ${visibleDocs.map(d => `
            <div class="glass-card panel-card" style="border-top:3px solid ${escapeHtml(d.color || "#d4b886")}">
              <strong style="color:${escapeHtml(d.color || "var(--accent-gold)")};font-size:13.5px">${escapeHtml(d.name_es)}</strong>
              <div style="font-size:11px;color:var(--text-muted)">${escapeHtml(d.name)}</div>
              <div style="display:flex;flex-wrap:wrap;gap:4px">
                ${(d.maps || []).map(mn => `<span class="kappa-tag" style="font-size:10px">${escapeHtml(mn)}</span>`).join("")}
              </div>
              <div style="font-size:11.5px;color:var(--text-soft);line-height:1.45">${escapeHtml(d.hotspots_es)}</div>
              <div style="font-size:11px;color:var(--accent-amber)">🔑 ${escapeHtml(d.keys_hint || "")}</div>
            </div>
          `).join("")}
        </div>
      `}
    `;

    container.querySelector("#bp-mode-live")?.addEventListener("click", () => { viewMode = "interactive"; render(); });
    container.querySelector("#bp-mode-off")?.addEventListener("click", () => { viewMode = "offline"; render(); });
    container.querySelector("#bp-reload-iframe")?.addEventListener("click", () => {
      const fr = container.querySelector("#kordmap-iframe");
      if (fr) fr.src = fr.src;
    });
    container.querySelector("#bp-map-sel")?.addEventListener("change", (e) => { mapFilter = e.target.value; render(); });
    container.querySelectorAll("[data-bp-ext]").forEach(b => b.addEventListener("click", () => window.pywebview.api.open_external_url(b.dataset.bpExt)));
  }

  render();
};
