"""
TarkovScope - Compositor Visual Dinámico de Armas estilo Escape from Tarkov
Renderiza la imagen real del arma desde cache/weapons/ sobre un banco de armería
táctico, rodeada por los recuadros reales de sus accesorios montados (con sus PNGs
oficiales p_*.png) y líneas guía hacia cada zona de anclaje del arma.
Lógica pura de renderizado gráfico desacoplada de la interfaz (Clean Architecture).
"""
import os
import sys
import threading
import requests
from typing import Dict, Any, Tuple, Optional, List, Set, Callable
from PIL import Image, ImageDraw

from core.image_cache import _get_font, WEAPONS_DIR
from core.config import TARKOV_DEV_GRAPHQL_URL
from core.weapon_modding_data import MODDABLE_WEAPONS, ATTACHMENTS_CATALOG, get_attachment_image_key


# Mapeo de weapon_id -> nombre de archivo PNG real en cache/weapons/
WEAPON_IMAGE_FILES: Dict[str, str] = {
    "m4a1": "m4a1.png",
    "ak74n": "ak_74n.png",
    "spear": "mcx_spear.png",
    "mk47": "mk47_mutant.png",
    "dvl10": "dvl_10.png",
    "mp7a2": "mp7a2.png",
    "rd704": "rd_704.png",
    "saiga12": "saiga_12.png",
    "sr25": "sr_25.png",
    "vss": "vss_val.png",
    "asval": "vss_val.png",
    "hk416": "m4a1.png",
    "tx15": "m4a1.png",
    "adar": "m4a1.png",
    "akm": "ak_74n.png",
    "ak101": "ak_74n.png",
    "ak103": "ak_74n.png",
    "ak104": "ak_74n.png",
    "ak105": "ak_74n.png",
    "ak12": "ak_74n.png",
    "rpk16": "ak_74n.png",
    "mp133": "gs_1.png",
    "m870": "gs_1.png",
    "mp153": "gs_1.png",
    "mp155": "gs_1.png",
    "vector45": "gs_11.png",
    "mpx": "gs_12.png",
    "pp19": "gs_3.png",
    "mp5": "gs_5.png",
    "rsass": "gs_6.png",
    "m1a": "gs_14.png",
    "ak74m": "ak_74n.png",
    "sks": "gs_24.png",
    "svds": "gs_21.png",
    "p90": "gs_20.png",
    "sa58": "gs_18.png",
    "scar_h": "gs_18.png",
    "scar_l": "m4a1.png",
    "mdr_556": "m4a1.png",
    "mdr_762": "gs_18.png",
    "mcx300": "mcx_spear.png",
    "m700": "dvl_10.png",
    "axmc": "dvl_10.png",
    "sv98": "dvl_10.png",
    "t5000": "dvl_10.png",
}

_RAW_PNG_CACHE: Dict[str, Image.Image] = {}
_FACTORY_FETCH_IN_FLIGHT: Set[str] = set()
_FACTORY_FETCH_FAILED: Set[str] = set()


def _resolve_factory_png_path(weapon_id: str) -> str:
    return os.path.join(WEAPONS_DIR, f"factory_{weapon_id}.png")


def ensure_factory_weapon_image_async(
    weapon_id: str,
    on_ready: Optional[Callable[[], None]] = None
) -> None:
    """
    Descarga en segundo plano la imagen del arma de fábrica completa (defaultPreset)
    desde tarkov.dev y la guarda en cache/weapons/factory_<id>.png.
    """
    if not weapon_id or weapon_id in _FACTORY_FETCH_IN_FLIGHT or weapon_id in _FACTORY_FETCH_FAILED:
        return
    dst_path = _resolve_factory_png_path(weapon_id)
    if os.path.exists(dst_path):
        return
    weapon = MODDABLE_WEAPONS.get(weapon_id)
    if not weapon:
        return

    _FACTORY_FETCH_IN_FLIGHT.add(weapon_id)
    # Usar nombre base sin calibre final para mejor coincidencia en tarkov.dev
    raw_name = weapon["name"].split(" 5.")[0].split(" 7.")[0].split(" 9x")[0].split(" .")[0].split(" 12/")[0].split(" 4.")[0].split(" 23x")[0].split(" 20/")[0].strip()

    def worker():
        try:
            q = (
                'query($n: String!) { items(name: $n, types: [gun], limit: 3) { '
                'name image512pxLink properties { ... on ItemPropertiesWeapon { '
                'defaultPreset { image512pxLink inspectImageLink } } } } }'
            )
            resp = requests.post(
                TARKOV_DEV_GRAPHQL_URL,
                json={"query": q, "variables": {"n": raw_name}},
                timeout=8,
            )
            if resp.status_code != 200:
                _FACTORY_FETCH_FAILED.add(weapon_id)
                return
            items = resp.json().get("data", {}).get("items", []) or []
            img_url = None
            for it in items:
                props = it.get("properties") or {}
                preset = props.get("defaultPreset") or {}
                img_url = preset.get("image512pxLink") or preset.get("inspectImageLink") or it.get("image512pxLink")
                if img_url:
                    break
            if not img_url:
                _FACTORY_FETCH_FAILED.add(weapon_id)
                return
            img_resp = requests.get(img_url, timeout=10)
            if img_resp.status_code == 200 and len(img_resp.content) > 500:
                with open(dst_path, "wb") as fh:
                    fh.write(img_resp.content)
                _RAW_PNG_CACHE.pop(f"factory_{weapon_id}", None)
                if on_ready:
                    on_ready()
            else:
                _FACTORY_FETCH_FAILED.add(weapon_id)
        except Exception:
            _FACTORY_FETCH_FAILED.add(weapon_id)
        finally:
            _FACTORY_FETCH_IN_FLIGHT.discard(weapon_id)

    threading.Thread(target=worker, daemon=True).start()


def _resolve_weapon_png_path(filename_no_ext: str) -> Optional[str]:
    clean = filename_no_ext if filename_no_ext.endswith(".png") else f"{filename_no_ext}.png"
    p1 = os.path.join(WEAPONS_DIR, clean)
    if os.path.exists(p1):
        return p1
    if hasattr(sys, "_MEIPASS"):
        p2 = os.path.join(sys._MEIPASS, "cache", "weapons", clean)
        if os.path.exists(p2):
            return p2
    return None


def _load_raw_png(filename_no_ext: str) -> Optional[Image.Image]:
    if not filename_no_ext:
        return None
    if filename_no_ext in _RAW_PNG_CACHE:
        return _RAW_PNG_CACHE[filename_no_ext]
    path = _resolve_weapon_png_path(filename_no_ext)
    if not path:
        return None
    try:
        img = Image.open(path).convert("RGBA")
        if len(_RAW_PNG_CACHE) > 96:
            _RAW_PNG_CACHE.clear()
        _RAW_PNG_CACHE[filename_no_ext] = img
        return img
    except Exception:
        return None


def _fit_contain(img: Image.Image, max_w: int, max_h: int, allow_upscale: float = 1.0) -> Image.Image:
    ow, oh = img.size
    if ow <= 0 or oh <= 0:
        return img.copy()
    scale = min(max(16, max_w) / ow, max(16, max_h) / oh)
    if scale > allow_upscale:
        scale = allow_upscale
    nw, nh = max(16, int(round(ow * scale))), max(16, int(round(oh * scale)))
    if (nw, nh) == (ow, oh):
        return img.copy()
    return img.resize((nw, nh), Image.Resampling.LANCZOS)


# Posiciones normalizadas de los recuadros de accesorios alrededor del arma (9 ranuras clickeables)
_SLOT_LAYOUT: List[Tuple[str, str, Tuple[int, int, int, int], Tuple[float, float], Tuple[float, float]]] = [
    ("barrel", "CAÑÓN", (148, 163, 184, 255), (0.13, 0.165), (0.28, 0.46)),
    ("muzzle", "BOCA", (56, 189, 248, 255), (0.37, 0.165), (0.21, 0.45)),
    ("optic", "ÓPTICA", (212, 184, 134, 255), (0.63, 0.165), (0.50, 0.36)),
    ("tactical", "TÁCTICO", (239, 68, 68, 255), (0.87, 0.165), (0.41, 0.44)),
    ("handguard", "GUARDAM.", (148, 163, 184, 255), (0.11, 0.835), (0.38, 0.49)),
    ("foregrip", "EMPUÑAD.", (96, 165, 250, 255), (0.305, 0.835), (0.43, 0.53)),
    ("magazine", "CARGADOR", (245, 158, 11, 255), (0.50, 0.835), (0.52, 0.61)),
    ("pistol_grip", "PISTOLETE", (168, 85, 247, 255), (0.695, 0.835), (0.58, 0.58)),
    ("stock", "CULATA", (52, 211, 153, 255), (0.89, 0.835), (0.68, 0.48)),
]


def get_slot_hitboxes(
    weapon_id: str,
    target_size: Tuple[int, int] = (920, 310),
) -> List[Dict[str, Any]]:
    """Retorna los rectángulos (x1, y1, x2, y2) de cada ranura sobre el canvas para hacer el diagrama interactivo."""
    w, h = target_size
    weapon = MODDABLE_WEAPONS.get(weapon_id, MODDABLE_WEAPONS["m4a1"])
    supported = set(weapon.get("supported_slots", []))
    box_w = max(108, min(156, int(w * 0.165)))
    box_h = max(42, min(54, int(h * 0.168)))
    boxes: List[Dict[str, Any]] = []
    for slot_key, slot_lbl, accent_rgba, (bcx_p, bcy_p), (ax_p, ay_p) in _SLOT_LAYOUT:
        if supported and slot_key not in supported:
            continue
        bx = max(8, min(w - box_w - 8, int(w * bcx_p) - box_w // 2))
        by = max(24, min(h - box_h - 6, int(h * bcy_p) - box_h // 2))
        boxes.append({
            "slot_key": slot_key,
            "slot_lbl": slot_lbl,
            "accent_rgba": accent_rgba,
            "bcy_p": bcy_p,
            "ax": int(w * ax_p),
            "ay": int(h * ay_p),
            "bx": bx,
            "by": by,
            "bw": box_w,
            "bh": box_h,
        })
    return boxes


def render_weapon_workbench_composite(
    weapon_id: str,
    slots: Dict[str, str],
    target_size: Tuple[int, int] = (680, 260),
    active_slot: str = "",
) -> Image.Image:
    """
    Genera la vista de armería estilo Escape from Tarkov con la imagen real del arma
    y los recuadros visuales de cada accesorio instalado.
    """
    w, h = target_size
    weapon = MODDABLE_WEAPONS.get(weapon_id, MODDABLE_WEAPONS["m4a1"])

    canvas = Image.new("RGBA", (w, h), (10, 13, 19, 255))
    draw = ImageDraw.Draw(canvas)

    # 1. Fondo de banco de armería con cuadrícula sutil
    grid_step = 26
    for gx in range(0, w, grid_step):
        draw.line([(gx, 0), (gx, h)], fill=(20, 26, 38, 255), width=1)
    for gy in range(0, h, grid_step):
        draw.line([(0, gy), (w, gy)], fill=(20, 26, 38, 255), width=1)

    # Marco perimetral y esquinas tácticas
    draw.rectangle([1, 1, w - 2, h - 2], outline=(38, 48, 66, 255), width=1)
    b_len = 14
    gold = (200, 176, 126, 220)
    for (cx, cy, dx, dy) in [
        (4, 4, 1, 1), (w - 5, 4, -1, 1),
        (4, h - 5, 1, -1), (w - 5, h - 5, -1, -1),
    ]:
        draw.line([(cx, cy), (cx + dx * b_len, cy)], fill=gold, width=2)
        draw.line([(cx, cy), (cx, cy + dy * b_len)], fill=gold, width=2)

    # 2. Imagen REAL del arma de fábrica centrada en la zona central
    factory_key = f"factory_{weapon_id}"
    weapon_pil = _load_raw_png(factory_key)
    is_factory_full = weapon_pil is not None
    if not weapon_pil:
        img_file = weapon.get("img_key") or WEAPON_IMAGE_FILES.get(weapon_id, f"{weapon_id}.png")
        weapon_pil = _load_raw_png(img_file)
        if not weapon_pil and weapon_id in WEAPON_IMAGE_FILES:
            weapon_pil = _load_raw_png(WEAPON_IMAGE_FILES[weapon_id])

    center_top = int(h * 0.27)
    center_bot = int(h * 0.71)
    center_h = max(60, center_bot - center_top)
    center_w = int(w * 0.64)

    if weapon_pil:
        ow, oh = weapon_pil.size
        is_bare_receiver = (not is_factory_full) and (ow <= 90 or (ow / max(1, oh)) < 1.55)
        if is_bare_receiver:
            # Integrar silueta táctica de arma completa detrás del receiver para que nunca flote solo
            cy = center_top + center_h // 2
            cx = w // 2
            # Culata trasera integrada
            draw.polygon([(cx - 145, cy - 12), (cx - 40, cy - 10), (cx - 40, cy + 8), (cx - 148, cy + 20)], fill=(22, 28, 39, 235), outline=(56, 70, 92, 220))
            # Guardamanos y cañón delantero integrados
            draw.rectangle([cx + 35, cy - 12, cx + 145, cy + 8], fill=(24, 30, 42, 235), outline=(56, 70, 92, 220), width=1)
            draw.rectangle([cx + 145, cy - 5, cx + 205, cy + 2], fill=(32, 40, 54, 240), outline=(74, 90, 114, 220), width=1)
            # Cargador curvo inferior
            draw.polygon([(cx + 6, cy + 12), (cx + 28, cy + 12), (cx + 36, cy + 44), (cx + 14, cy + 44)], fill=(20, 26, 36, 235), outline=(56, 70, 92, 200))

        wpn_fit = _fit_contain(weapon_pil, center_w, center_h, allow_upscale=1.8 if is_bare_receiver else 2.2)
        ww, wh = wpn_fit.size
        wx = (w - ww) // 2
        wy = center_top + (center_h - wh) // 2
        if not is_bare_receiver:
            draw.rounded_rectangle(
                [wx - 12, wy - 7, wx + ww + 12, wy + wh + 7],
                radius=10,
                fill=(13, 17, 26, 200),
                outline=(52, 66, 92, 190),
                width=1,
            )
        canvas.alpha_composite(wpn_fit, (wx, wy))
    else:
        font_fb = _get_font(16, bold=True)
        fb_txt = weapon["name"].upper()
        tb = draw.textbbox((0, 0), fb_txt, font=font_fb)
        draw.rounded_rectangle(
            [w // 2 - 180, h // 2 - 24, w // 2 + 180, h // 2 + 24],
            radius=8,
            fill=(18, 24, 36, 230),
            outline=gold,
            width=1,
        )
        draw.text((w // 2 - (tb[2] - tb[0]) // 2, h // 2 - (tb[3] - tb[1]) // 2), fb_txt, fill=(245, 243, 236, 255), font=font_fb)

    # 3. Recuadros reales de accesorios estilo EFT alrededor del arma
    font_slot = _get_font(8, bold=True)
    font_part = _get_font(9, bold=True)
    font_stat = _get_font(8, bold=False)

    for hb in get_slot_hitboxes(weapon_id, target_size):
        slot_key = hb["slot_key"]
        slot_lbl = hb["slot_lbl"]
        accent_rgba = hb["accent_rgba"]
        bcy_p = hb["bcy_p"]
        ax, ay = hb["ax"], hb["ay"]
        bx, by, box_w, box_h = hb["bx"], hb["by"], hb["bw"], hb["bh"]

        part_id = slots.get(slot_key, "none")
        is_equipped = part_id != "none"
        is_active = bool(active_slot and slot_key == active_slot)
        part = ATTACHMENTS_CATALOG.get(part_id, ATTACHMENTS_CATALOG["none"])

        line_col = gold if is_active else (accent_rgba[0], accent_rgba[1], accent_rgba[2], 150 if is_equipped else 45)
        edge_y = by + box_h if bcy_p < 0.5 else by
        draw.line([(bx + box_w // 2, edge_y), (ax, ay)], fill=line_col, width=2 if is_active else 1)
        draw.ellipse([ax - 3 if is_active else ax - 2, ay - 3 if is_active else ay - 2, ax + 3 if is_active else ax + 2, ay + 3 if is_active else ay + 2], fill=line_col)

        fill_col = (24, 31, 46, 245) if is_active else ((18, 24, 34, 240) if is_equipped else (13, 17, 24, 195))
        border_col = (212, 184, 134, 255) if is_active else (accent_rgba if is_equipped else (42, 52, 68, 180))
        draw.rounded_rectangle([bx, by, bx + box_w, by + box_h], radius=5, fill=fill_col, outline=border_col, width=2 if is_active else 1)

        icon_box = box_h - 10
        if is_equipped:
            p_img_key = get_attachment_image_key(part_id)
            p_pil = _load_raw_png(p_img_key)
            if p_pil:
                p_fit = _fit_contain(p_pil, icon_box, icon_box)
                pw, ph = p_fit.size
                canvas.alpha_composite(p_fit, (bx + 4 + (icon_box - pw) // 2, by + 5 + (icon_box - ph) // 2))
            text_x = bx + icon_box + 7
        else:
            text_x = bx + 7

        draw.text((text_x, by + 4), slot_lbl, fill=(212, 184, 134, 255) if is_active else (accent_rgba if is_equipped else (100, 116, 139, 255)), font=font_slot)
        p_name = part.get("name", "Vacío").split(" (")[0] if is_equipped else "Vacío"
        max_chars = 14 if is_equipped else 16
        if len(p_name) > max_chars:
            p_name = p_name[:max_chars - 1] + "…"
        draw.text((text_x, by + 15), p_name, fill=(248, 250, 252, 255) if is_equipped else (100, 116, 139, 200), font=font_part)

        if is_equipped and box_h >= 44:
            e_d = part.get("ergo_delta", 0.0)
            r_d = part.get("recoil_pct_delta", 0.0)
            stat_bits = []
            if e_d:
                stat_bits.append(f"{e_d:+g}E")
            if r_d:
                stat_bits.append(f"{r_d:+g}%R")
            if stat_bits:
                draw.text((text_x, by + 29), " ".join(stat_bits), fill=(110, 231, 183, 255), font=font_stat)

    # 4. Cabecera superior estilo EFT Inspect
    font_hdr = _get_font(11, bold=True)
    active_count = len([s for s in slots.values() if s != "none"])
    draw.text((14, 7), f"{weapon['name'].upper()}  •  {weapon.get('caliber', '')}", fill=(212, 184, 134, 255), font=font_hdr)
    right_txt = f"{weapon.get('fire_rate', 600)} RPM  |  {active_count} PIEZAS"
    rtb = draw.textbbox((0, 0), right_txt, font=font_hdr)
    draw.text((w - (rtb[2] - rtb[0]) - 14, 7), right_txt, fill=(148, 163, 184, 255), font=font_hdr)

    return canvas
