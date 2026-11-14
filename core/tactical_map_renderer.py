"""
TarkovScope - Motor de Renderizado Táctico de Mapas y Radares de Spawns
Dibuja capas tácticas, extracciones, puntos de interés (POIs), alfileres de usuario
y radares balísticos de Bosses sobre los mapas topográficos 2D en alta resolución.
Extraído de image_cache.py para cumplir con el principio de responsabilidad única (SOLID).
"""
import os
import logging
from typing import Tuple, Dict, Any, List, Optional
from PIL import Image, ImageDraw

from core.maps_data import (
    normalize_map_key,
    get_map_extractions_with_coords,
    get_map_tactical_pois,
)
from core.bosses_data import BOSSES_DATA, get_boss_map_spawn_chance
from core.image_cache import (
    _get_font,
    load_map_image,
    load_full_res_map_image,
    create_placeholder_map,
    get_boss_spawn_map_paths,
    get_boss_chibi_sticker,
    get_cached_map_path,
)

logger = logging.getLogger("TarkovScope.TacticalMapRenderer")


def load_boss_spawn_map_image(
    boss: Dict[str, Any],
    map_name: str,
    target_size: Tuple[int, int] = (740, 450),
    high_res: bool = False
) -> Image.Image:
    """
    Retorna el plano 2D del mapa con las zonas de spawn del Boss dibujadas tácticamente.
    Usa archivos pre-generados en cache/boss_maps/ para responder en <3 ms.
    """
    boss_id = boss.get("id", "boss")
    thumb_path, hd_path = get_boss_spawn_map_paths(boss_id, map_name, target_size)

    if high_res and os.path.exists(hd_path):
        try:
            return Image.open(hd_path).convert("RGBA")
        except Exception:
            pass

    if not high_res and os.path.exists(thumb_path):
        try:
            return Image.open(thumb_path).convert("RGBA")
        except Exception:
            pass

    # Generar plano táctico con marcadores de spawn
    norm_map = normalize_map_key(map_name)
    raw_map_path = get_cached_map_path(norm_map)
    if os.path.exists(raw_map_path):
        try:
            base = Image.open(raw_map_path).convert("RGBA")
            base.thumbnail((1500, 1000), Image.Resampling.LANCZOS)
        except Exception:
            base = create_placeholder_map(map_name, (1200, 750))
    else:
        base = create_placeholder_map(map_name, (1200, 750))

    w, h = base.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    spawns = boss.get("map_spawns", {}).get(map_name, [])
    if not spawns:
        # Buscar coincidencia insensible a mayúsculas
        for k, v in boss.get("map_spawns", {}).items():
            if normalize_map_key(k) == norm_map:
                spawns = v
                break

    font_num = _get_font(max(18, int(min(w, h) * 0.024)), bold=True)
    font_lbl = _get_font(max(14, int(min(w, h) * 0.017)), bold=True)
    font_hdr = _get_font(max(16, int(min(w, h) * 0.020)), bold=True)

    # Banner superior táctico semitransparente
    banner_h = max(38, int(h * 0.055))
    draw.rectangle([0, 0, w, banner_h], fill=(15, 17, 21, 215))
    draw.line([(0, banner_h), (w, banner_h)], fill=(229, 115, 47, 255), width=3)
    m_chances = boss.get("map_spawn_chances", {}).get(map_name, {})
    if m_chances and m_chances.get("pve"):
        pve_str = m_chances.get("pve", "")
        pvp_str = m_chances.get("pvp", "")
        prob_str = f"{pve_str} (PvE)" if pve_str == pvp_str else f"{pve_str} (PvE) / {pvp_str} (PvP)"
    else:
        prob_str = boss.get("spawn_chance", "")
    short_name = boss.get('name', '').split(' (')[0].upper()
    hdr_text = f"RADAR DE SPAWNS: {short_name}  |  MAPA: {map_name.upper()}  |  SPAWN: {prob_str}"
    draw.text((16, (banner_h - int(banner_h * 0.55)) // 2), hdr_text, fill=(230, 232, 236, 255), font=font_hdr)

    r_outer = max(34, int(min(w, h) * 0.052))
    r_inner = max(16, int(min(w, h) * 0.022))

    for idx, sp in enumerate(spawns, start=1):
        x_pct = float(sp.get("x", 0.5))
        y_pct = float(sp.get("y", 0.5))
        cx = int(w * x_pct)
        cy = int(h * y_pct)

        # Círculo exterior de zona de peligro (Rojo táctico traslúcido)
        draw.ellipse(
            [cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
            fill=(239, 68, 68, 82),
            outline=(239, 68, 68, 245),
            width=3
        )
        # Líneas de mira (Crosshair)
        draw.line([(cx - r_outer - 8, cy), (cx - r_inner - 2, cy)], fill=(239, 68, 68, 230), width=2)
        draw.line([(cx + r_inner + 2, cy), (cx + r_outer + 8, cy)], fill=(239, 68, 68, 230), width=2)
        draw.line([(cx, cy - r_outer - 8), (cx, cy - r_inner - 2)], fill=(239, 68, 68, 230), width=2)
        draw.line([(cx, cy + r_inner + 2), (cx, cy + r_outer + 8)], fill=(239, 68, 68, 230), width=2)

        # Miniatura Chibi Sticker del Boss en lugar de los números en los spawns
        sticker_img = get_boss_chibi_sticker(boss_id, target_size=max(56, int(min(w, h) * 0.085)))
        if sticker_img:
            sw, sh = sticker_img.size
            overlay.paste(sticker_img, (cx - sw // 2, cy - sh // 2), sticker_img)
            # Insignia táctica numerada (#idx) en la esquina inferior del sticker
            badge_r = max(11, int(sw * 0.20))
            bx_b = cx + sw // 2 - badge_r + 2
            by_b = cy + sh // 2 - badge_r + 2
            draw.ellipse(
                [bx_b - badge_r, by_b - badge_r, bx_b + badge_r, by_b + badge_r],
                fill=(229, 115, 47, 255),
                outline=(255, 255, 255, 255),
                width=2
            )
            num_str = str(idx)
            font_badge = _get_font(max(10, int(badge_r * 1.15)), bold=True)
            nb = draw.textbbox((0, 0), num_str, font=font_badge)
            draw.text((bx_b - (nb[2] - nb[0]) // 2, by_b - (nb[3] - nb[1]) // 2 - 1), num_str, fill=(255, 255, 255, 255), font=font_badge)
        else:
            # Fallback a pin clásico si no hubiese imagen
            draw.ellipse(
                [cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner],
                fill=(229, 115, 47, 255),
                outline=(255, 255, 255, 255),
                width=2
            )
            num_str = str(idx)
            nb = draw.textbbox((0, 0), num_str, font=font_num)
            nw, nh = nb[2] - nb[0], nb[3] - nb[1]
            draw.text((cx - nw // 2, cy - nh // 2 - 2), num_str, fill=(255, 255, 255, 255), font=font_num)

        # Etiqueta flotante con el nombre de la zona
        zone_title = f"#{idx} {sp.get('zone', 'Spawn')}"
        if len(zone_title) > 34:
            zone_title = zone_title[:32] + ".."
        tb = draw.textbbox((0, 0), zone_title, font=font_lbl)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]

        pill_x = min(max(10, cx + r_outer + 6), w - tw - 24)
        if cx > w * 0.68:
            pill_x = max(10, cx - r_outer - tw - 22)
        pill_y = min(max(banner_h + 8, cy - th // 2 - 4), h - th - 16)

        draw.rounded_rectangle(
            [pill_x, pill_y, pill_x + tw + 16, pill_y + th + 10],
            radius=6,
            fill=(15, 17, 21, 235),
            outline=(229, 115, 47, 255),
            width=2
        )
        draw.text((pill_x + 8, pill_y + 4), zone_title, fill=(255, 255, 255, 255), font=font_lbl)

    composed = Image.alpha_composite(base, overlay)

    try:
        composed.save(hd_path, "PNG")
        thumb_img = composed.copy()
        thumb_img.thumbnail(target_size, Image.Resampling.LANCZOS)
        thumb_img.save(thumb_path, "PNG")
    except Exception as e:
        logger.warning("No se pudo guardar mapa de boss pre-generado: %s", e)
        thumb_img = composed.copy()
        thumb_img.thumbnail(target_size, Image.Resampling.LANCZOS)

    return composed if high_res else thumb_img


PIN_COLOR_CYCLE = [
    "#EF4444",  # 1. Rojo Carmesí
    "#3B82F6",  # 2. Azul Eléctrico
    "#10B981",  # 3. Verde Esmeralda
    "#F59E0B",  # 4. Amarillo Ámbar
    "#A855F7",  # 5. Violeta Intenso
    "#06B6D4",  # 6. Cian Brillante
    "#EC4899",  # 7. Rosa Magenta
    "#84CC16",  # 8. Verde Lima
    "#F97316",  # 9. Naranja Táctico
    "#14B8A6",  # 10. Turquesa
]


def get_pin_color_for_index(idx_zero_based: int) -> str:
    """Retorna un color de cabeza de alfiler distinto para cada marcador según su orden."""
    return PIN_COLOR_CYCLE[idx_zero_based % len(PIN_COLOR_CYCLE)]


def render_map_with_user_markers(
    map_id: str,
    markers: list,
    target_size: Tuple[int, int] = (780, 480),
    high_res: bool = False,
    show_pins: bool = True,
    show_pmc: bool = True,
    show_scav: bool = True,
    show_boss: bool = True,
    show_keys: bool = False,
    show_loot: bool = False
) -> Image.Image:
    """
    Dibuja capas interactivas de inteligencia táctica sobre el plano del mapa:
    1) Spawns y zonas de peligro de Jefes (Bosses).
    2) Extracciones PMC (verde esmeralda táctico).
    3) Extracciones Scav (naranja ámbar).
    4) Llaves críticas / Habitaciones Marcadas (violeta táctico).
    5) Cajas fuertes / Botín de alto valor (cian táctico).
    6) Alfileres 3D interactivos con aguja metálica y cabezas esféricas numeradas.
    """
    base = load_full_res_map_image(map_id, max_dim=1800) if high_res else load_map_image(map_id, target_size)
    norm_key = normalize_map_key(map_id)

    # Si no hay ninguna capa activa ni marcadores, retornar base directamente
    if not (show_pins and markers) and not show_pmc and not show_scav and not show_boss and not show_keys and not show_loot:
        return base

    img = base.copy().convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_pin = _get_font(max(11, int(min(w, h) * 0.019)), bold=True)
    font_txt = _get_font(max(12, int(min(w, h) * 0.018)), bold=True)
    font_poi = _get_font(max(11, int(min(w, h) * 0.016)), bold=True)
    r_head = max(12, int(min(w, h) * 0.022))

    # --- 1. CAPA: Zonas de Spawn de Bosses ---
    if show_boss:
        try:
            from core.bosses_data import BOSSES_DATA, get_boss_map_spawn_chance
            for b in BOSSES_DATA:
                b_spawns = b.get("map_spawns", {})
                spawns_list = []
                matched_map_name = map_id
                for k, v in b_spawns.items():
                    if normalize_map_key(k) == norm_key:
                        spawns_list.extend(v)
                        matched_map_name = k
                if not spawns_list:
                    continue
                m_pve = get_boss_map_spawn_chance(b, matched_map_name, "pve")
                b_stk = get_boss_chibi_sticker(b.get("id"), target_size=max(46, int(min(w, h) * 0.068)))
                for sp in spawns_list:
                    if str(sp.get("chance", "")).startswith("0%"):
                        continue
                    bx = int(w * float(sp.get("x", 0.5)))
                    by = int(h * float(sp.get("y", 0.5)))
                    r_b = max(24, int(min(w, h) * 0.040))

                    # Círculo traslúcido de peligro
                    draw.ellipse(
                        [bx - r_b, by - r_b, bx + r_b, by + r_b],
                        fill=(239, 68, 68, 55),
                        outline=(239, 68, 68, 220),
                        width=2
                    )
                    # Crosshairs tácticos
                    draw.line([(bx - r_b - 4, by), (bx + r_b + 4, by)], fill=(239, 68, 68, 160), width=1)
                    draw.line([(bx, by - r_b - 4), (bx, by + r_b + 4)], fill=(239, 68, 68, 160), width=1)

                    if b_stk:
                        sw, sh = b_stk.size
                        overlay.paste(b_stk, (bx - sw // 2, by - sh // 2), b_stk)

                    # Etiqueta de Boss con % PvE
                    short_b_name = b.get("name", "Boss").split(" (")[0]
                    b_lbl = f"BOSS: {short_b_name} ({m_pve})" if m_pve else f"BOSS: {short_b_name}"
                    bb = draw.textbbox((0, 0), b_lbl, font=font_poi)
                    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
                    px = min(max(4, bx - bw // 2), w - bw - 12)
                    py = max(4, by - r_b - bh - 6)
                    draw.rounded_rectangle(
                        [px - 4, py - 2, px + bw + 4, py + bh + 2],
                        radius=3,
                        fill=(15, 23, 42, 235),
                        outline=(239, 68, 68, 240),
                        width=1
                    )
                    draw.text((px, py), b_lbl, fill=(254, 202, 202, 255), font=font_poi)
        except Exception as e:
            logger.warning("Error al dibujar capa de Bosses: %s", e)

    # --- 2. CAPA: Extracciones PMC y Scav ---
    if show_pmc or show_scav:
        try:
            extractions = get_map_extractions_with_coords(norm_key)
            for ex in extractions:
                is_pmc = ex.get("is_pmc", True)
                is_scav = ex.get("is_scav", False)
                if is_scav and not show_scav:
                    continue
                if not is_scav and not show_pmc:
                    continue

                ex_x = int(w * float(ex.get("x", 0.5)))
                ex_y = int(h * float(ex.get("y", 0.5)))

                # Colores según facción
                if is_scav:
                    outline_col = (245, 158, 11, 255)
                    prefix = "SCAV: "
                else:
                    outline_col = (16, 185, 129, 255)
                    prefix = "EXT: "

                # Punto en coordenadas exactas
                draw.ellipse([ex_x - 3, ex_y - 3, ex_x + 3, ex_y + 3], fill=outline_col, outline=(255, 255, 255, 220), width=1)

                ex_name = prefix + ex.get("name", "Extracción")
                if len(ex_name) > 24:
                    ex_name = ex_name[:22] + ".."
                eb = draw.textbbox((0, 0), ex_name, font=font_poi)
                ew, eh = eb[2] - eb[0], eb[3] - eb[1]

                epx = min(max(6, ex_x - ew // 2), w - ew - 14)
                epy = max(6, ex_y - eh - 8) if ex_y > 40 else ex_y + 8

                draw.rounded_rectangle(
                    [epx - 5, epy - 2, epx + ew + 5, epy + eh + 3],
                    radius=4,
                    fill=(10, 15, 25, 235),
                    outline=outline_col,
                    width=1
                )
                draw.text((epx, epy), ex_name, fill=(248, 250, 252, 255), font=font_poi)
        except Exception as e:
            logger.warning("Error al dibujar capa de extracciones: %s", e)

    # --- 2B. CAPA: Llaves / Marked Rooms y Zonas de Botín Top ---
    if show_keys or show_loot:
        try:
            tactical_pois = get_map_tactical_pois(norm_key)
            for poi in tactical_pois:
                p_type = poi.get("type", "key")
                if p_type == "key" and not show_keys:
                    continue
                if p_type == "loot" and not show_loot:
                    continue

                px_c = int(w * float(poi.get("x", 0.5)))
                py_c = int(h * float(poi.get("y", 0.5)))

                if p_type == "key":
                    p_col = (168, 85, 247, 255)  # Violeta táctico para Llaves / Marked
                    p_prefix = "KEY: "
                else:
                    p_col = (6, 182, 212, 255)   # Cian brillante para Cajas Fuertes / Botín Top
                    p_prefix = "LOOT: "

                draw.ellipse(
                    [px_c - 5, py_c - 5, px_c + 5, py_c + 5],
                    fill=p_col,
                    outline=(255, 255, 255, 240),
                    width=1
                )
                p_label = p_prefix + poi.get("name", "POI")
                if len(p_label) > 28:
                    p_label = p_label[:26] + ".."
                pb = draw.textbbox((0, 0), p_label, font=font_poi)
                pw, ph = pb[2] - pb[0], pb[3] - pb[1]
                plx = min(max(6, px_c - pw // 2), w - pw - 14)
                ply = min(h - ph - 8, py_c + 8)

                draw.rounded_rectangle(
                    [plx - 5, ply - 2, plx + pw + 5, ply + ph + 3],
                    radius=4,
                    fill=(12, 16, 26, 238),
                    outline=p_col,
                    width=1
                )
                draw.text((plx, ply), p_label, fill=(248, 250, 252, 255), font=font_poi)
        except Exception as e:
            logger.warning("Error al dibujar capa de POIs: %s", e)

    # --- 3. CAPA: Alfileres y Notas Personalizadas del Usuario ---
    if show_pins and markers:
        used_colors = []
        for idx, mk in enumerate(markers, start=1):
            tx = int(w * float(mk.get("x_pct", 0.5)))
            ty = int(h * float(mk.get("y_pct", 0.5)))

            raw_hex = (mk.get("color") or "").strip()
            if not raw_hex or raw_hex.upper() == "#E5732F" or (used_colors and raw_hex.upper() == used_colors[-1]):
                raw_hex = get_pin_color_for_index(idx - 1)
            used_colors.append(raw_hex.upper())

            hex_col = raw_hex.lstrip("#")
            try:
                rgb = tuple(int(hex_col[i:i + 2], 16) for i in (0, 2, 4))
            except Exception:
                rgb = (239, 68, 68)

            dark_rgb = (max(0, int(rgb[0] * 0.58)), max(0, int(rgb[1] * 0.58)), max(0, int(rgb[2] * 0.58)))
            light_rgb = (min(255, int(rgb[0] + (255 - rgb[0]) * 0.42)),
                         min(255, int(rgb[1] + (255 - rgb[1]) * 0.42)),
                         min(255, int(rgb[2] + (255 - rgb[2]) * 0.42)))

            needle_dx = int(r_head * 0.42)
            needle_dy = int(r_head * 2.05)
            hx = min(max(r_head + 4, tx + needle_dx), w - r_head - 4)
            hy = max(r_head + 4, ty - needle_dy)

            sh_x = min(w - r_head, tx + int(r_head * 0.85))
            sh_y = max(r_head, ty - int(r_head * 0.55))
            draw.line([(tx, ty), (sh_x, sh_y)], fill=(0, 0, 0, 110), width=max(3, r_head // 4))
            draw.ellipse(
                [sh_x - int(r_head * 0.65), sh_y - int(r_head * 0.35),
                 sh_x + int(r_head * 0.65), sh_y + int(r_head * 0.35)],
                fill=(0, 0, 0, 95)
            )

            draw.ellipse([tx - 3, ty - 2, tx + 3, ty + 2], fill=(15, 23, 42, 230), outline=(255, 255, 255, 200), width=1)

            neck_x = hx - int(needle_dx * 0.28)
            neck_y = hy + int(r_head * 0.72)
            draw.polygon(
                [
                    (tx, ty),
                    (neck_x - max(2, r_head // 6), neck_y),
                    (neck_x + max(2, r_head // 6), neck_y),
                ],
                fill=(203, 213, 225, 255),
                outline=(71, 85, 105, 255)
            )
            draw.line([(tx, ty), (neck_x, neck_y)], fill=(248, 250, 252, 240), width=1)

            collar_r = max(5, int(r_head * 0.46))
            draw.ellipse(
                [neck_x - collar_r, neck_y - int(collar_r * 0.65),
                 neck_x + collar_r, neck_y + int(collar_r * 0.65)],
                fill=(dark_rgb[0], dark_rgb[1], dark_rgb[2], 255),
                outline=(15, 23, 42, 255),
                width=1
            )

            draw.ellipse(
                [hx - r_head, hy - r_head, hx + r_head, hy + r_head],
                fill=(dark_rgb[0], dark_rgb[1], dark_rgb[2], 255),
                outline=(15, 23, 42, 255),
                width=2
            )
            inner_r = max(4, int(r_head * 0.86))
            draw.ellipse(
                [hx - inner_r - 1, hy - inner_r - 1, hx + inner_r - 1, hy + inner_r - 1],
                fill=(rgb[0], rgb[1], rgb[2], 255)
            )
            glow_r = max(3, int(r_head * 0.55))
            draw.ellipse(
                [hx - glow_r - 2, hy - glow_r - 2, hx + glow_r - 2, hy + glow_r - 2],
                fill=(light_rgb[0], light_rgb[1], light_rgb[2], 210)
            )
            spec_r = max(2, int(r_head * 0.24))
            spec_x = hx - int(r_head * 0.38)
            spec_y = hy - int(r_head * 0.38)
            draw.ellipse(
                [spec_x - spec_r, spec_y - spec_r, spec_x + spec_r, spec_y + spec_r],
                fill=(255, 255, 255, 235)
            )

            num_s = str(idx)
            nb = draw.textbbox((0, 0), num_s, font=font_pin)
            nw, nh = nb[2] - nb[0], nb[3] - nb[1]
            nx = hx - nw // 2
            ny = hy - nh // 2 - 1
            for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                draw.text((nx + ox, ny + oy), num_s, fill=(10, 12, 16, 245), font=font_pin)
            draw.text((nx, ny), num_s, fill=(255, 255, 255, 255), font=font_pin)

            note_str = f"{mk.get('title', 'Nota')}"
            if len(note_str) > 30:
                note_str = note_str[:28] + ".."
            tb = draw.textbbox((0, 0), note_str, font=font_txt)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]

            px = min(max(8, hx + r_head + 8), w - tw - 22)
            if hx > w * 0.68:
                px = max(8, hx - r_head - tw - 22)
            py = min(max(8, hy - th // 2 - 4), h - th - 14)

            draw.rounded_rectangle(
                [px, py, px + tw + 16, py + th + 8],
                radius=5,
                fill=(10, 12, 16, 238),
                outline=(rgb[0], rgb[1], rgb[2], 255),
                width=2
            )
            draw.rounded_rectangle(
                [px, py, px + 5, py + th + 8],
                radius=2,
                fill=(rgb[0], rgb[1], rgb[2], 255)
            )
            draw.text((px + 10, py + 3), note_str, fill=(248, 250, 252, 255), font=font_txt)

    return Image.alpha_composite(img, overlay)


def render_quest_objective_map(
    map_key: str,
    pin_coords: Tuple[float, float],
    quest_title: str,
    objective_poi: str,
    target_size: Tuple[int, int] = (680, 380)
) -> Image.Image:
    """
    Genera un mapa táctico 2D optimizado de la misión con retícula luminosa,
    anillo de objetivo y cartel con el nombre del POI (Ground Zero, Customs, Woods, etc.).
    """
    norm = normalize_map_key(map_key)
    base = load_map_image(norm, target_size).convert("RGBA")
    w, h = base.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    px = max(0.05, min(0.95, float(pin_coords[0])))
    py = max(0.05, min(0.95, float(pin_coords[1])))
    cx, cy = int(w * px), int(h * py)

    # 1. Círculo de área de objetivo (Cian táctico translúcido #38BDF8)
    r_outer = 26
    r_inner = 8
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=(56, 189, 248, 70), outline=(56, 189, 248, 240), width=2)
    draw.line([(cx - r_outer - 6, cy), (cx - r_inner, cy)], fill=(56, 189, 248, 220), width=2)
    draw.line([(cx + r_inner, cy), (cx + r_outer + 6, cy)], fill=(56, 189, 248, 220), width=2)
    draw.line([(cx, cy - r_outer - 6), (cx, cy - r_inner)], fill=(56, 189, 248, 220), width=2)
    draw.line([(cx, cy + r_inner), (cx, cy + r_outer + 6)], fill=(56, 189, 248, 220), width=2)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(248, 250, 252, 255))

    # 2. Cartel con el POI del objetivo
    font_poi = _get_font(12, bold=True)
    lbl_text = f"🎯 {objective_poi}"
    tb = draw.textbbox((0, 0), lbl_text, font=font_poi)
    bw, bh = tb[2] - tb[0] + 16, tb[3] - tb[1] + 8
    bx = max(10, min(w - bw - 10, cx - bw // 2))
    by = cy - r_outer - bh - 6 if (cy - r_outer - bh - 6) > 34 else (cy + r_outer + 8)

    draw.rectangle([bx, by, bx + bw, by + bh], fill=(15, 23, 42, 230), outline=(56, 189, 248, 200), width=1)
    draw.text((bx + 8, by + 4), lbl_text, fill=(248, 250, 252, 255), font=font_poi)

    # 3. Banner superior con título de la misión
    banner_h = 32
    draw.rectangle([0, 0, w, banner_h], fill=(10, 14, 22, 210))
    draw.line([(0, banner_h), (w, banner_h)], fill=(212, 184, 134, 255), width=2)
    font_hdr = _get_font(12, bold=True)
    draw.text((12, 8), f"📍 SECTOR DE OPERACIÓN: {quest_title.upper()} ({map_key.upper()})", fill=(212, 184, 134, 255), font=font_hdr)

    composed = Image.alpha_composite(base, overlay)
    return composed
