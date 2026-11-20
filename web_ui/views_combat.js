/* =====================================================================
   TTC v2.0 — Vistas de Combate: Arsenal, Gunsmith (1-25 con piezas),
   Modding Studio Pro (con vista arma + importador Base64), Averías 93%,
   Balística (203 Balas + Duelo STK exacto) & Blindajes/Cascos (Completo)
   ===================================================================== */

window.TTCViews = window.TTCViews || {};

/* ================= 1. ARMERÍA, GUNSMITH & MODDING STUDIO ================= */
window.TTCViews.renderWeaponsView = async function (container) {
  const data = await window.pywebview.api.get_weapons_arsenal();
  const modCatalog = await window.pywebview.api.get_modding_catalog();
  let subtab = "arsenal"; // arsenal | gunsmith | builder | malfunctions
  let selWeaponId = data.arsenal[0]?.id || "";
  let wbWeaponId = modCatalog.weapons[0]?.id || "";
  let wbSlots = {};

  container.innerHTML = `
    <div class="view-header">
      <h1 class="view-title">ARMERÍA <span>&amp; MODDING STUDIO</span></h1>
      <div class="subtabs-bar" id="w-subtabs">
        <button class="subtab-btn active" data-st="arsenal">🔫 Arsenal Meta</button>
        <button class="subtab-btn" data-st="gunsmith">🔧 Gunsmith (1–25)</button>
        <button class="subtab-btn" data-st="builder">🛠️ Modding Studio Pro</button>
        <button class="subtab-btn" data-st="malfunctions">⚠️ Averías &amp; 93%</button>
      </div>
    </div>
    <div id="weapons-body"></div>
  `;

  const body = container.querySelector("#weapons-body");
  container.querySelectorAll("#w-subtabs .subtab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      subtab = btn.dataset.st;
      container.querySelectorAll("#w-subtabs .subtab-btn").forEach(b => b.classList.toggle("active", b.dataset.st === subtab));
      render();
    });
  });

  function renderArsenal() {
    const wp = data.arsenal.find(w => w.id === selWeaponId) || data.arsenal[0];
    body.innerHTML = `
      <div class="split-layout">
        <div class="glass-card split-list">
          ${data.arsenal.map(w => `
            <button class="list-item-card ${w.id === selWeaponId ? "active" : ""}" data-wid="${escapeHtml(w.id)}">
              <img class="item-thumb-sm" src="${escapeHtml(w.image_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
              <div style="flex:1;min-width:0">
                <div style="font-weight:700;font-size:12.5px">${escapeHtml(w.name)}</div>
                <div style="font-size:11px;color:var(--accent-gold)">${escapeHtml(w.tier)} · ${w.rpm} RPM · ${escapeHtml(w.caliber)}</div>
              </div>
            </button>
          `).join("")}
        </div>
        <div class="glass-card split-detail">
          <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">
            <img src="${escapeHtml(wp.image_url)}" style="width:220px;height:96px;object-fit:contain;background:var(--bg-darkest);border-radius:10px;padding:8px;border:1px solid var(--border)" onerror="this.style.display='none'" />
            <div>
              <h2 style="font-family:var(--font-display);font-size:24px;color:var(--accent-gold)">${escapeHtml(wp.name)}</h2>
              <div style="color:var(--text-muted);font-size:12.5px">${escapeHtml(wp.category)} · Calibre ${escapeHtml(wp.caliber)} · ${wp.rpm} RPM · Tier ${escapeHtml(wp.tier)}</div>
            </div>
          </div>
          <div class="cards-grid-2">
            <div class="info-box">
              <div class="panel-title" style="color:var(--accent-gold);margin-bottom:8px">🏆 Build Meta Competitiva</div>
              <ul style="margin-left:16px;color:var(--text-soft);line-height:1.55">${(wp.meta_build || []).map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul>
            </div>
            <div class="info-box">
              <div class="panel-title" style="color:var(--accent-emerald);margin-bottom:8px">💰 Build Económica (LL2/LL3)</div>
              <ul style="margin-left:16px;color:var(--text-soft);line-height:1.55">${(wp.budget_build || []).map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul>
            </div>
          </div>
          <div class="info-box"><strong style="color:var(--accent-blue)">🧠 Análisis Táctico:</strong><div style="margin-top:4px;color:var(--text-soft)">${escapeHtml(wp.notes || "")}</div></div>
        </div>
      </div>
    `;
    body.querySelectorAll("[data-wid]").forEach(b => b.addEventListener("click", () => { selWeaponId = b.dataset.wid; renderArsenal(); }));
  }

  function renderGunsmith() {
    const doneCnt = data.gunsmith.filter(g => g.is_done).length;
    body.innerHTML = `
      <div class="glass-card toolbar-row" style="justify-content:space-between">
        <strong style="color:var(--accent-gold)">🔧 Progreso Gunsmith (Mechanic): ${doneCnt} / ${data.gunsmith.length}</strong>
        <span style="font-size:12px;color:var(--text-muted)">Incluye todas las piezas requeridas por parte · Clic en ✓ para marcar</span>
      </div>
      <div class="cards-grid-2">
        ${data.gunsmith.map(g => `
          <div class="glass-card panel-card" style="${g.is_done ? "border-color:rgba(16,185,129,.5)" : ""}">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:10px">
              <div style="display:flex;align-items:center;gap:10px">
                <img class="item-thumb-sm" src="${escapeHtml(g.image_url)}" style="width:68px;height:40px" loading="lazy" onerror="this.style.display='none'" />
                <div>
                  <strong style="font-size:14.5px;color:${g.is_done ? "var(--accent-emerald)" : "var(--accent-gold)"}">${escapeHtml(g.title || `Gunsmith - Part ${g.part}`)}</strong>
                  <div style="font-size:11.5px;color:var(--text-muted)">${escapeHtml(g.weapon)} · Nv.${g.level || 1} · ${escapeHtml(g.reqs || "")}</div>
                </div>
              </div>
              <button class="btn-check-quest" data-gs-part="${g.part}" style="${g.is_done ? "background:var(--accent-emerald);color:#04120c" : ""}">✓</button>
            </div>
            <ul style="margin-left:16px;font-size:12px;color:var(--text-soft);line-height:1.5">
              ${(g.parts_detailed || []).map(p => `<li>${escapeHtml(Array.isArray(p) ? p[1] : p)}</li>`).join("")}
            </ul>
          </div>
        `).join("")}
      </div>
    `;
    body.querySelectorAll("[data-gs-part]").forEach(btn => {
      btn.addEventListener("click", async () => {
        const part = Number(btn.dataset.gsPart);
        const res = await window.pywebview.api.toggle_gunsmith_done(part);
        const item = data.gunsmith.find(x => x.part === part);
        if (item && res?.ok) { item.is_done = res.is_done; renderGunsmith(); }
      });
    });
  }

  let wbSearch = "";

  async function renderBuilder() {
    const curWpn = modCatalog.weapons.find(w => w.id === wbWeaponId) || modCatalog.weapons[0];
    if (curWpn && !Object.keys(wbSlots).length && curWpn.default_slots) {
      wbSlots = { ...curWpn.default_slots };
    }
    const calc = await window.pywebview.api.calculate_weapon_build(wbWeaponId, wbSlots);
    const st = calc.stats || {};
    const supported = new Set(curWpn?.supported_slots || []);
    const allSlots = Array.isArray(modCatalog.slots)
      ? modCatalog.slots
      : Object.entries(modCatalog.slots || {}).map(([key, label]) => ({ key, label }));
    const visibleSlots = supported.size ? allSlots.filter(s => supported.has(s.key)) : allSlots;
    const presetNames = Object.keys(curWpn?.presets || {});

    body.innerHTML = `
      <div class="glass-card toolbar-row">
        <select class="t-select" id="wb-weapon-sel" style="min-width:240px">
          ${modCatalog.weapons.map(w => `<option value="${escapeHtml(w.id)}" ${w.id === wbWeaponId ? "selected" : ""}>${escapeHtml(w.name)} (${escapeHtml(w.caliber || "")})</option>`).join("")}
        </select>
        <input class="t-input" id="wb-part-search" value="${escapeHtml(wbSearch)}" placeholder="Filtrar piezas (Razor, Zenit, SureFire, Magpul...)" style="width:240px" />
        <button class="btn-primary-gold" id="wb-opt-recoil">⚡ Meta Recoil</button>
        <button class="btn-ghost-sm" id="wb-opt-ergo">🎯 CQC Ergo</button>
        <button class="btn-ghost-sm" id="wb-opt-budget">💰 Budget LL2</button>
        <button class="btn-ghost-sm" id="wb-reset-stock">↺ Stock</button>
        <button class="btn-ghost-sm" id="wb-copy-b64">🔗 Copiar Base64</button>
        <button class="btn-ghost-sm" id="wb-import-b64">📥 Importar</button>
        <button class="btn-ghost-sm" id="wb-copy-shop">📋 Lista Compras</button>
      </div>
      ${presetNames.length ? `
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center">
          <span style="font-size:11.5px;color:var(--text-muted);font-weight:700">Presets Oficiales:</span>
          ${presetNames.map(pn => `<button class="btn-ghost-sm" data-preset="${escapeHtml(pn)}">★ ${escapeHtml(pn)}</button>`).join("")}
        </div>
      ` : ""}
      <div class="glass-card panel-card" style="margin-bottom:14px;flex-direction:row;align-items:center;gap:18px;flex-wrap:wrap">
        <img src="${escapeHtml(curWpn?.image_url || "")}" style="width:240px;height:96px;object-fit:contain;background:var(--bg-darkest);border-radius:10px;padding:8px;border:1px solid var(--border)" onerror="this.style.display='none'" />
        <div class="stat-grid-4" style="flex:1;min-width:340px">
          <div class="stat-tile">
            <div class="stat-tile-lbl">Recoil Vertical</div>
            <div class="stat-tile-val">${st.final_recoil_v ?? "—"} <span style="font-size:11px;color:var(--accent-emerald)">(${st.recoil_reduction_pct ?? 0}%)</span></div>
          </div>
          <div class="stat-tile">
            <div class="stat-tile-lbl">Recoil Horizontal</div>
            <div class="stat-tile-val">${st.final_recoil_h ?? "—"}</div>
          </div>
          <div class="stat-tile">
            <div class="stat-tile-lbl">Ergonomía (ADS)</div>
            <div class="stat-tile-val" style="color:var(--accent-emerald)">${st.final_ergo ?? "—"} <span style="font-size:11px;color:var(--text-muted)">(${st.ergo_delta_total >= 0 ? "+" : ""}${st.ergo_delta_total ?? 0})</span></div>
          </div>
          <div class="stat-tile">
            <div class="stat-tile-lbl">Costo · Peso</div>
            <div class="stat-tile-val" style="color:var(--accent-amber);font-size:15px">${(st.total_cost_rubles || 0).toLocaleString("es-AR")} ₽ · ${st.final_weight_kg ?? "—"} kg</div>
          </div>
        </div>
      </div>
      <div class="cards-grid-3" id="wb-slots-grid"></div>
    `;

    const grid = body.querySelector("#wb-slots-grid");
    const slotPromises = visibleSlots.map(async (slotObj) => {
      const opts = await window.pywebview.api.get_weapon_slot_options(wbWeaponId, slotObj.key);
      return { slotObj, opts: opts || [] };
    });
    const resolvedSlots = await Promise.all(slotPromises);

    const qPart = wbSearch.trim().toLowerCase();
    for (const { slotObj, opts } of resolvedSlots) {
      if (!opts.length) continue;
      const sk = slotObj.key;
      const selectedId = wbSlots[sk] || "none";
      const filteredOpts = qPart
        ? opts.filter(o => o.id === "none" || o.id === selectedId || `${o.name} ${o.trader}`.toLowerCase().includes(qPart))
        : opts;
      const curOpt = opts.find(o => o.id === selectedId) || opts[0];
      const card = document.createElement("div");
      card.className = "glass-card panel-card";
      card.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px">
          <div class="panel-title">${escapeHtml(slotObj.label || sk)}</div>
          <span style="font-size:10.5px;color:var(--text-muted)">${Math.max(0, filteredOpts.length - 1)}/${Math.max(0, opts.length - 1)} piezas</span>
        </div>
        <select class="t-select" data-slot="${escapeHtml(sk)}">
          ${filteredOpts.map(o => {
            const rec = Number(o.recoil_pct_delta || 0);
            const ergo = Number(o.ergo_delta || 0);
            const price = Number(o.price_rubles || 0);
            const meta = o.id === "none" ? "" : ` (${rec > 0 ? "+" : ""}${rec}% Rec · ${ergo >= 0 ? "+" : ""}${ergo} Ergo · ${price.toLocaleString("es-AR")} ₽)`;
            return `<option value="${escapeHtml(o.id)}" ${selectedId === o.id ? "selected" : ""}>${escapeHtml(o.name)}${meta}</option>`;
          }).join("")}
        </select>
        ${curOpt && curOpt.id !== "none" ? `
          <div style="display:flex;align-items:center;gap:10px;margin-top:4px;font-size:11.5px;color:var(--text-muted)">
            ${curOpt.image_url ? `<img src="${escapeHtml(curOpt.image_url)}" style="width:44px;height:36px;object-fit:contain;background:var(--bg-darkest);border-radius:6px;padding:2px;border:1px solid var(--border-soft)" onerror="this.style.display='none'" />` : ""}
            <div style="flex:1;line-height:1.4">
              <div style="color:var(--accent-gold);font-weight:700">${escapeHtml(curOpt.trader || "Flea")} LL${curOpt.loyalty_level || 1} · ${(curOpt.price_rubles || 0).toLocaleString("es-AR")} ₽</div>
              <div>Recoil <strong style="color:${(curOpt.recoil_pct_delta || 0) <= 0 ? "var(--accent-emerald)" : "var(--accent-red)"}">${curOpt.recoil_pct_delta || 0}%</strong> · Ergo <strong style="color:var(--accent-blue)">${(curOpt.ergo_delta || 0) >= 0 ? "+" : ""}${curOpt.ergo_delta || 0}</strong></div>
            </div>
          </div>
        ` : `<div style="font-size:11px;color:var(--text-dim);margin-top:2px">Sin accesorio equipado en esta ranura.</div>`}
      `;
      card.querySelector("select").addEventListener("change", (e) => {
        wbSlots[sk] = e.target.value || "none";
        renderBuilder();
      });
      grid.appendChild(card);
    }

    body.querySelector("#wb-weapon-sel").addEventListener("change", (e) => {
      wbWeaponId = e.target.value;
      const nw = modCatalog.weapons.find(w => w.id === wbWeaponId);
      wbSlots = nw?.default_slots ? { ...nw.default_slots } : {};
      renderBuilder();
    });
    const partSearchEl = body.querySelector("#wb-part-search");
    if (partSearchEl) {
      partSearchEl.addEventListener("input", (e) => {
        wbSearch = e.target.value;
        clearTimeout(partSearchEl._t);
        partSearchEl._t = setTimeout(() => renderBuilder(), 180);
      });
    }
    body.querySelector("#wb-reset-stock").addEventListener("click", () => {
      wbSlots = curWpn?.default_slots ? { ...curWpn.default_slots } : {};
      renderBuilder();
      showToast("↺ Configuración de fábrica restaurada");
    });
    body.querySelectorAll("[data-preset]").forEach(btn => {
      btn.addEventListener("click", () => {
        const pn = btn.dataset.preset;
        if (curWpn?.presets?.[pn]) {
          wbSlots = { ...curWpn.presets[pn] };
          renderBuilder();
          showToast(`★ Preset "${pn}" aplicado`);
        }
      });
    });
    body.querySelector("#wb-opt-recoil").addEventListener("click", async () => { const r = await window.pywebview.api.auto_optimize_weapon(wbWeaponId, "meta_recoil", 4); wbSlots = r.slots || {}; renderBuilder(); showToast("⚡ Build Meta Recoil aplicada"); });
    body.querySelector("#wb-opt-ergo").addEventListener("click", async () => { const r = await window.pywebview.api.auto_optimize_weapon(wbWeaponId, "max_ergo", 4); wbSlots = r.slots || {}; renderBuilder(); showToast("🎯 Build CQC High Ergo aplicada"); });
    body.querySelector("#wb-opt-budget").addEventListener("click", async () => { const r = await window.pywebview.api.auto_optimize_weapon(wbWeaponId, "budget", 2); wbSlots = r.slots || {}; renderBuilder(); showToast("💰 Build Budget LL2 aplicada"); });
    body.querySelector("#wb-copy-b64").addEventListener("click", () => { navigator.clipboard?.writeText(calc.base64_code || ""); showToast("🔗 Código TTCBUILD copiado"); });
    body.querySelector("#wb-copy-shop").addEventListener("click", () => { navigator.clipboard?.writeText(calc.shopping_list || ""); showToast("📋 Lista de compras copiada"); });
    body.querySelector("#wb-import-b64").addEventListener("click", async () => {
      const code = prompt("Pega un código TTCBUILD:... para importar:");
      if (!code) return;
      const r = await window.pywebview.api.import_weapon_build(code);
      if (r && r.ok) { wbWeaponId = r.weapon_id; wbSlots = r.slots || {}; renderBuilder(); showToast("📥 Build importada correctamente"); }
      else showToast("⚠️ Código inválido");
    });
  }

  function renderMalfunctions() {
    const dg = data.durability_guide || {};
    body.innerHTML = `
      <div class="glass-card panel-card" style="margin-bottom:14px">
        <strong style="color:var(--accent-amber);font-size:15.5px">⚠️ ${escapeHtml(dg.threshold_93_title_es || "Regla de Oro del 93% de Durabilidad")}</strong>
        <p style="color:var(--text-soft);line-height:1.55">${escapeHtml(dg.threshold_93_desc_es || "")}</p>
      </div>
      <div class="cards-grid-2" style="margin-bottom:14px">
        ${(data.malfunctions || []).map(m => `
          <div class="glass-card panel-card">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <strong style="color:var(--accent-gold);font-size:15px">${escapeHtml(m.name_es || m.name)}</strong>
              <span class="kappa-tag">Durabilidad &lt; ${escapeHtml(m.min_durability_threshold || "93%")}</span>
            </div>
            <div style="font-size:12px;color:var(--text-muted)"><strong>Causas:</strong> ${escapeHtml(m.causes_es || "")}</div>
            <div class="info-box" style="font-size:12px;color:var(--accent-emerald)"><strong>🔧 Solución:</strong> ${escapeHtml(Array.isArray(m.fix_steps_es) ? m.fix_steps_es.join(" → ") : (m.fix_steps_es || ""))}</div>
            <div style="font-size:11.5px;color:var(--accent-blue)">💡 ${escapeHtml(m.pro_tip_es || "")}</div>
          </div>
        `).join("")}
      </div>
      <div class="cards-grid-2">
        <div class="glass-card panel-card">
          <div class="panel-title" style="color:var(--accent-red)">🔥 Etapas de Sobrecalentamiento</div>
          ${(dg.overheat_stages || []).map(s => `<div class="info-box" style="font-size:12px"><strong style="color:var(--accent-amber)">${escapeHtml(s.stage || s.title_es || "")}</strong> — ${escapeHtml(s.effect_es || s.desc_es || "")}</div>`).join("")}
        </div>
        <div class="glass-card panel-card">
          <div class="panel-title" style="color:var(--accent-emerald)">🧰 Kits y Comerciantes de Reparación</div>
          ${(dg.repair_kits_guide || []).map(r => `<div class="info-box" style="font-size:12px"><strong style="color:var(--accent-gold)">${escapeHtml(r.name || r.source || "")}</strong> — ${escapeHtml(r.notes_es || r.effect_es || "")}</div>`).join("")}
        </div>
      </div>
    `;
  }

  function render() {
    if (subtab === "arsenal") renderArsenal();
    else if (subtab === "gunsmith") renderGunsmith();
    else if (subtab === "builder") renderBuilder();
    else renderMalfunctions();
  }
  render();
};

/* ================= 2. BALÍSTICA (203 BALAS), DUELO STK & BLINDAJES ================= */
window.TTCViews.renderBallisticsView = async function (container) {
  const data = await window.pywebview.api.get_ballistics_data();
  let armorCache = null;
  let subtab = "matrix"; // matrix | duel | armor
  let caliber = "TODOS", search = "", sortKey = "penetration_power", sortDesc = true;

  container.innerHTML = `
    <div class="view-header">
      <h1 class="view-title">BALÍSTICA <span>&amp; BLINDAJES</span></h1>
      <div class="subtabs-bar" id="b-subtabs">
        <button class="subtab-btn active" data-st="matrix">💥 Matriz Penetración (${data.ammunition.length})</button>
        <button class="subtab-btn" data-st="duel">⚔️ Simulador STK / Bosses</button>
        <button class="subtab-btn" data-st="armor">🛡️ Blindajes, Placas &amp; Cascos</button>
      </div>
    </div>
    <div id="ballistics-body"></div>
  `;

  const body = container.querySelector("#ballistics-body");
  container.querySelectorAll("#b-subtabs .subtab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      subtab = btn.dataset.st;
      container.querySelectorAll("#b-subtabs .subtab-btn").forEach(b => b.classList.toggle("active", b.dataset.st === subtab));
      render();
    });
  });

  function renderMatrix() {
    const q = search.trim().toLowerCase();
    const rows = data.ammunition.filter(a => {
      if (caliber !== "TODOS" && a.caliber !== caliber) return false;
      if (q && !`${a.name} ${a.caliber} ${a.caliber_label || ""}`.toLowerCase().includes(q)) return false;
      return true;
    }).sort((a, b) => {
      const av = Number(a[sortKey] || 0), bv = Number(b[sortKey] || 0);
      return sortDesc ? bv - av : av - bv;
    });

    body.innerHTML = `
      <div class="glass-card toolbar-row">
        <input class="t-input" id="b-search" value="${escapeHtml(search)}" placeholder="Buscar munición (M80A1, BP, M995, SNB, RIP)..." style="flex:1;min-width:220px" />
        <select class="t-select" id="b-cal">
          <option value="TODOS">Todos los calibres (${data.calibers.length})</option>
          ${data.calibers.map(c => {
            const cid = typeof c === "string" ? c : c.id;
            const clbl = typeof c === "string" ? c : (c.label || c.id);
            return `<option value="${escapeHtml(cid)}" ${cid === caliber ? "selected" : ""}>${escapeHtml(clbl)}</option>`;
          }).join("")}
        </select>
        <span class="hud-chip">${rows.length} proyectiles</span>
      </div>
      <div class="table-wrap glass-card">
        <table class="tarkov-table ballistics-table">
          <thead>
            <tr>
              <th>Munición</th>
              <th>Calibre</th>
              <th class="col-center" data-sort="damage" style="cursor:pointer">Daño</th>
              <th class="col-center" data-sort="penetration_power" style="cursor:pointer">Pen</th>
              <th class="col-center" data-sort="armor_damage" style="cursor:pointer">Arm%</th>
              <th class="col-center">C1</th>
              <th class="col-center">C2</th>
              <th class="col-center">C3</th>
              <th class="col-center">C4</th>
              <th class="col-center">C5</th>
              <th class="col-center">C6</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map(a => `
              <tr>
                <td><strong>${escapeHtml(a.name)}</strong></td>
                <td style="color:var(--text-muted)">${escapeHtml(a.caliber_label || a.caliber)}</td>
                <td class="col-center" style="font-family:var(--font-mono);font-weight:700">${a.damage}</td>
                <td class="col-center" style="font-family:var(--font-mono);font-weight:800;color:var(--accent-gold)">${a.penetration_power}</td>
                <td class="col-center" style="font-family:var(--font-mono)">${a.armor_damage}%</td>
                ${[1, 2, 3, 4, 5, 6].map(c => {
                  const v = a.tiers?.[String(c)] ?? 0;
                  return `<td class="col-center"><span class="tier-cell t${v}">${v}</span></td>`;
                }).join("")}
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
    body.querySelector("#b-search").addEventListener("input", (e) => { search = e.target.value; renderMatrix(); });
    body.querySelector("#b-cal").addEventListener("change", (e) => { caliber = e.target.value; renderMatrix(); });
    body.querySelectorAll("[data-sort]").forEach(th => {
      th.addEventListener("click", () => {
        if (sortKey === th.dataset.sort) sortDesc = !sortDesc;
        else { sortKey = th.dataset.sort; sortDesc = true; }
        renderMatrix();
      });
    });
  }

  async function renderDuel() {
    let selectedAmmo = data.ammunition[0];
    let armorClass = 4, rpm = 700;

    async function draw() {
      const sim = await window.pywebview.api.simulate_ballistics_duel(
        selectedAmmo.damage, selectedAmmo.penetration_power, selectedAmmo.armor_damage, armorClass, 50, rpm
      );
      const stk = sim.stk || {};
      body.innerHTML = `
        <div class="glass-card toolbar-row">
          <select class="t-select" id="d-ammo" style="flex:1">
            ${data.ammunition.map((a, idx) => `<option value="${idx}" ${a === selectedAmmo ? "selected" : ""}>${escapeHtml(a.name)} (${escapeHtml(a.caliber)} · Dmg ${a.damage} / Pen ${a.penetration_power})</option>`).join("")}
          </select>
          <select class="t-select" id="d-cls">${[1, 2, 3, 4, 5, 6].map(c => `<option value="${c}" ${c === armorClass ? "selected" : ""}>Armadura Clase ${c}</option>`).join("")}</select>
          <input class="t-input" id="d-rpm" type="number" value="${rpm}" style="width:100px" title="RPM del arma" />
        </div>
        <div class="stat-grid-4" style="margin-bottom:14px">
          <div class="stat-tile"><div class="stat-tile-lbl">Disparos al Tórax (STK)</div><div class="stat-tile-val">${stk.stk ?? "—"} tiros</div></div>
          <div class="stat-tile"><div class="stat-tile-lbl">Time to Kill (TTK)</div><div class="stat-tile-val" style="color:var(--accent-emerald)">${stk.ttk_ms ?? 0} ms</div></div>
          <div class="stat-tile"><div class="stat-tile-lbl">Penetración 1er Disparo</div><div class="stat-tile-val" style="color:var(--accent-blue)">${stk.first_shot_pen_pct ?? 0}%</div></div>
          <div class="stat-tile"><div class="stat-tile-lbl">Leg Meta (Piernas)</div><div class="stat-tile-val" style="color:var(--accent-amber)">${sim.leg_meta ?? "—"} tiros</div></div>
        </div>
        <div class="glass-card panel-card">
          <div class="panel-title">Simulación contra Bosses de Tarkov</div>
          <div class="cards-grid-3">
            ${(sim.bosses || []).map(b => `
              <div class="info-box">
                <strong style="color:var(--accent-gold)">${escapeHtml(b.target)}</strong>
                <div style="font-size:12px;color:var(--accent-emerald);margin-top:4px;font-weight:700">${escapeHtml(b.verdict)} (Pen: ${b.pen_pct}%)</div>
              </div>
            `).join("")}
          </div>
        </div>
      `;
      body.querySelector("#d-ammo").addEventListener("change", (e) => { selectedAmmo = data.ammunition[Number(e.target.value)]; draw(); });
      body.querySelector("#d-cls").addEventListener("change", (e) => { armorClass = Number(e.target.value); draw(); });
      body.querySelector("#d-rpm").addEventListener("change", (e) => { rpm = Math.max(100, Number(e.target.value) || 700); draw(); });
    }
    draw();
  }

  async function renderArmor() {
    if (!armorCache) armorCache = await window.pywebview.api.get_armor_catalog();
    let aq = "", acat = "Todos", selArmorId = armorCache[0]?.id || "";
    function draw() {
      const q = aq.trim().toLowerCase();
      const cats = ["Todos", ...new Set(armorCache.map(x => x.category))];
      const list = armorCache.filter(x => (acat === "Todos" || x.category === acat) && (!q || `${x.name} ${x.material || ""} ${x.areas || ""}`.toLowerCase().includes(q)));
      if (list.length && !list.some(i => i.id === selArmorId)) selArmorId = list[0].id;
      const cur = list.find(i => i.id === selArmorId) || list[0];

      body.innerHTML = `
        <div class="glass-card toolbar-row">
          <input class="t-input" id="ar-q" value="${escapeHtml(aq)}" placeholder="Buscar placa, chaleco, casco o auricular..." style="flex:1" />
          <select class="t-select" id="ar-cat">${cats.map(c => `<option value="${escapeHtml(c)}" ${c === acat ? "selected" : ""}>${escapeHtml(c)}</option>`).join("")}</select>
          <span class="hud-chip">${list.length} ítems</span>
        </div>
        <div class="split-layout">
          <div class="glass-card split-list">
            ${list.map(x => `
              <button class="list-item-card ${x.id === selArmorId ? "active" : ""}" data-aid="${escapeHtml(x.id)}">
                <img class="item-thumb-sm" src="${escapeHtml(x.icon_url)}" loading="lazy" onerror="this.style.visibility='hidden'" />
                <div style="flex:1;min-width:0">
                  <div style="font-weight:700;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${escapeHtml(x.name)}</div>
                  <div style="font-size:11px;color:var(--accent-gold)">${x.armor_class ? `Clase ${x.armor_class}` : `${x.hearing_distance_m || ""}m`} · ${escapeHtml(x.material || x.category)}</div>
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
                  <div style="font-size:12.5px;color:var(--text-muted)">${escapeHtml(cur.category)} · ${cur.material ? `Material: ${escapeHtml(cur.material)}` : ""}</div>
                </div>
              </div>
              <div class="stat-grid-4">
                <div class="stat-tile"><div class="stat-tile-lbl">Clase / Alcance</div><div class="stat-tile-val">${cur.armor_class ? `Clase ${cur.armor_class}` : `${cur.hearing_distance_m || "—"}m`}</div></div>
                <div class="stat-tile"><div class="stat-tile-lbl">Durabilidad / Efectiva</div><div class="stat-tile-val" style="color:var(--accent-emerald)">${cur.durability ?? "—"} / ${cur.effective_durability ?? "—"}</div></div>
                <div class="stat-tile"><div class="stat-tile-lbl">Peso</div><div class="stat-tile-val" style="color:var(--accent-blue)">${cur.weight_kg ?? "—"} kg</div></div>
                <div class="stat-tile"><div class="stat-tile-lbl">Penalización Ergo</div><div class="stat-tile-val" style="color:var(--accent-amber)">${cur.ergo_penalty ?? 0}%</div></div>
              </div>
              <div class="info-box"><strong style="color:var(--accent-gold)">🛡️ Cobertura / Perfil:</strong><div style="margin-top:4px;color:var(--text-soft)">${escapeHtml(cur.areas || cur.audio_profile || cur.mount_type || "—")}</div></div>
              ${cur.move_penalty !== undefined ? `<div class="info-box" style="font-size:12px;color:var(--text-muted)">Velocidad movimiento: ${cur.move_penalty}% · Giro: ${cur.turn_penalty}%</div>` : ""}
            ` : `<div style="color:var(--text-muted)">Sin resultados.</div>`}
          </div>
        </div>
      `;
      body.querySelector("#ar-q").addEventListener("input", (e) => { aq = e.target.value; draw(); });
      body.querySelector("#ar-cat").addEventListener("change", (e) => { acat = e.target.value; draw(); });
      body.querySelectorAll("[data-aid]").forEach(b => b.addEventListener("click", () => { selArmorId = b.dataset.aid; draw(); }));
    }
    draw();
  }

  function render() {
    if (subtab === "matrix") renderMatrix();
    else if (subtab === "duel") renderDuel();
    else renderArmor();
  }
  render();
};
