"""
TarkovScope - Compositor Visual Dinámico de Armas y Blueprint Táctico
Dibuja el plano esquemático de armería estilo EFT en tiempo real:
renderiza el chasis del arma y ensambla visualmente cada accesorio instalado
(silenciadores, miras ópticas, empuñaduras, culatas, cargadores de tambor/curvos y láseres).
Lógica pura de renderizado gráfico desacoplada de la interfaz (Clean Architecture).
"""
import os
import math
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

from core.image_cache import _get_font, WEAPONS_DIR
from core.weapon_modding_data import MODDABLE_WEAPONS, ATTACHMENTS_CATALOG


# Perfiles geométricos de base según plataforma de arma
WEAPON_GEOMETRY: Dict[str, Dict[str, Any]] = {
    "m4a1": {
        "body_rect": [190, 110, 430, 158],
        "barrel_start": 430,
        "barrel_y": 126,
        "barrel_h": 14,
        "rail_y": 108,
        "mag_x": 310,
        "grip_x": 235,
        "stock_x": 190,
    },
    "ak74n": {
        "body_rect": [180, 108, 440, 156],
        "barrel_start": 440,
        "barrel_y": 124,
        "barrel_h": 13,
        "rail_y": 106,
        "mag_x": 320,
        "grip_x": 225,
        "stock_x": 180,
    },
    "spear": {
        "body_rect": [190, 106, 450, 160],
        "barrel_start": 450,
        "barrel_y": 125,
        "barrel_h": 16,
        "rail_y": 104,
        "mag_x": 315,
        "grip_x": 235,
        "stock_x": 190,
    },
    "sa58": {
        "body_rect": [170, 108, 440, 162],
        "barrel_start": 440,
        "barrel_y": 126,
        "barrel_h": 15,
        "rail_y": 106,
        "mag_x": 310,
        "grip_x": 220,
        "stock_x": 170,
    },
    "mp133": {
        "body_rect": [180, 114, 420, 156],
        "barrel_start": 420,
        "barrel_y": 122,
        "barrel_h": 12,
        "rail_y": 112,
        "mag_x": 350,
        "grip_x": 210,
        "stock_x": 180,
    },
    "vector45": {
        "body_rect": [220, 102, 390, 166],
        "barrel_start": 390,
        "barrel_y": 122,
        "barrel_h": 14,
        "rail_y": 100,
        "mag_x": 330,
        "grip_x": 260,
        "stock_x": 220,
    },
    "dvl10": {
        "body_rect": [170, 112, 410, 156],
        "barrel_start": 410,
        "barrel_y": 124,
        "barrel_h": 18,
        "rail_y": 108,
        "mag_x": 290,
        "grip_x": 220,
        "stock_x": 170,
    },
    "mk47": {
        "body_rect": [190, 108, 440, 158],
        "barrel_start": 440,
        "barrel_y": 125,
        "barrel_h": 14,
        "rail_y": 106,
        "mag_x": 320,
        "grip_x": 235,
        "stock_x": 190,
    }
}


def render_weapon_workbench_composite(
    weapon_id: str,
    slots: Dict[str, str],
    target_size: Tuple[int, int] = (680, 260)
) -> Image.Image:
    """
    Renderiza el banco de trabajo táctico en tiempo real:
    dibuja el chasis del arma con cuadrícula milimétrica militar y ensambla
    visualmente las piezas instaladas (cañón, silenciador, óptica, cargador, grip, culata y láser).
    Responde en <1 ms sirviendo una visualización dinámica y viva.
    """
    w, h = target_size
    canvas = Image.new("RGBA", (w, h), (11, 15, 23, 255))
    draw = ImageDraw.Draw(canvas)

    weapon = MODDABLE_WEAPONS.get(weapon_id, MODDABLE_WEAPONS["m4a1"])
    geom = WEAPON_GEOMETRY.get(weapon_id, WEAPON_GEOMETRY["m4a1"])

    # 1. Fondo de tapete milimétrico militar (Workbench Grid)
    grid_step = 24
    for gx in range(0, w, grid_step):
        draw.line([(gx, 0), (gx, h)], fill=(18, 27, 40, 255), width=1)
    for gy in range(0, h, grid_step):
        draw.line([(0, gy), (w, gy)], fill=(18, 27, 40, 255), width=1)

    # Regla milimétrica en los bordes
    font_ruler = _get_font(9, bold=False)
    for rx in range(0, w, 48):
        draw.line([(rx, h - 8), (rx, h)], fill=(71, 85, 105, 255), width=1)
        if rx > 0 and rx < w - 40:
            draw.text((rx + 3, h - 14), f"{rx}mm", fill=(100, 116, 139, 200), font=font_ruler)

    # 2. Silueta del Chasis / Cajón de Mecanismos (Receiver & Handguard)
    rx1, ry1, rx2, ry2 = geom["body_rect"]
    draw.rounded_rectangle(
        [rx1, ry1, rx2, ry2],
        radius=5,
        fill=(36, 44, 58, 255),
        outline=(71, 85, 105, 255),
        width=2
    )
    # Riel Picatinny superior
    rail_y = geom["rail_y"]
    draw.rectangle([rx1 + 10, rail_y, rx2 - 10, rail_y + 4], fill=(71, 85, 105, 255))
    for tooth_x in range(rx1 + 14, rx2 - 14, 6):
        draw.line([(tooth_x, rail_y), (tooth_x, rail_y + 3)], fill=(20, 25, 35, 255), width=1)

    # Ventana de expulsión y cerrojo
    draw.rectangle([rx1 + 75, ry1 + 8, rx1 + 120, ry1 + 22], fill=(20, 25, 35, 255), outline=(51, 65, 85, 255), width=1)

    # 3. Cañón Dinámico (Barrel)
    b_start = geom["barrel_start"]
    by = geom["barrel_y"]
    bh = geom["barrel_h"]
    part_barrel = slots.get("barrel", "none")
    # Longitud según cañón
    barrel_len = 100
    if "260mm" in part_barrel or "short" in part_barrel or "11in" in part_barrel:
        barrel_len = 65
    elif "406mm" in part_barrel or "16in" in part_barrel or "660mm" in part_barrel or "21in" in part_barrel:
        barrel_len = 145
    elif "508mm" in part_barrel:
        barrel_len = 175

    b_end = b_start + barrel_len
    draw.rectangle([b_start, by, b_end, by + bh], fill=(45, 55, 72, 255), outline=(71, 85, 105, 255), width=2)
    # Ranuras de ventilación / paso de gases
    for gx in range(b_start + 12, b_end - 12, 14):
        draw.line([(gx, by + 3), (gx + 6, by + bh - 3)], fill=(25, 32, 45, 255), width=1)

    # 4. Bocacha o Silenciador Dinámico (Muzzle)
    part_muzzle = slots.get("muzzle", "none")
    muzzle_callout = None
    if part_muzzle != "none":
        m_item = ATTACHMENTS_CATALOG.get(part_muzzle, {})
        m_name = m_item.get("name", "")
        is_silencer = "silenciador" in m_name.lower() or "wave" in m_name.lower() or "waffel" in m_name.lower() or "prs" in m_name.lower() or "salvo" in m_name.lower() or "rotor" in m_name.lower() or "slx" in m_name.lower()

        if is_silencer:
            # Silenciador táctico cilíndrico extendido
            s_w = 68
            s_h = bh + 14
            s_y = by - 7
            draw.rounded_rectangle(
                [b_end, s_y, b_end + s_w, s_y + s_h],
                radius=4,
                fill=(26, 32, 44, 255),
                outline=(56, 189, 248, 255),  # Cyan táctico
                width=2
            )
            # Estrías de disipación de calor
            for sx in range(b_end + 8, b_end + s_w - 6, 8):
                draw.line([(sx, s_y + 3), (sx, s_y + s_h - 3)], fill=(56, 189, 248, 120), width=1)
            # Boca del silenciador
            draw.ellipse([b_end + s_w - 3, s_y + s_h // 2 - 3, b_end + s_w + 3, s_y + s_h // 2 + 3], fill=(15, 23, 42, 255))
            muzzle_callout = (b_end + s_w // 2, s_y, f"🔇 {m_name.split(' (')[0][:20]}")
        else:
            # Freno de boca / compensador corto con puertos de escape
            b_w = 26
            b_h = bh + 6
            b_y = by - 3
            draw.rectangle(
                [b_end, b_y, b_end + b_w, b_y + b_h],
                fill=(30, 41, 59, 255),
                outline=(148, 163, 184, 255),
                width=2
            )
            draw.line([(b_end + 8, b_y + 2), (b_end + 8, b_y + b_h - 2)], fill=(56, 189, 248, 200), width=2)
            draw.line([(b_end + 16, b_y + 2), (b_end + 16, b_y + b_h - 2)], fill=(56, 189, 248, 200), width=2)
            muzzle_callout = (b_end + b_w // 2, b_y, f"💥 {m_name.split(' (')[0][:20]}")

    # 5. Óptica / Mira Dinámica (Optic)
    part_optic = slots.get("optic", "none")
    optic_callout = None
    if part_optic != "none":
        o_item = ATTACHMENTS_CATALOG.get(part_optic, {})
        o_name = o_item.get("name", "")
        ox = rx1 + 80
        oy = rail_y - 2

        if "vortex" in part_optic or "schmidt" in part_optic or "valday" in part_optic or "1-6" in o_name or "1-8" in o_name:
            # Mira telescópica / LPVO con montura cantilever y torretas
            scope_w = 115
            scope_h = 24
            mount_h = 10
            # Montura cantilever
            draw.rectangle([ox + 15, oy - mount_h, ox + 35, oy], fill=(30, 41, 59, 255), outline=(212, 184, 134, 255), width=1)
            draw.rectangle([ox + 75, oy - mount_h, ox + 95, oy], fill=(30, 41, 59, 255), outline=(212, 184, 134, 255), width=1)
            draw.line([(ox + 15, oy - mount_h), (ox + 95, oy - mount_h)], fill=(212, 184, 134, 255), width=2)
            # Tubo principal de la mira
            tube_y = oy - mount_h - scope_h
            draw.rounded_rectangle([ox, tube_y, ox + scope_w, tube_y + scope_h], radius=4, fill=(24, 30, 42, 255), outline=(212, 184, 134, 255), width=2)
            # Campana delantera (objetivo) y trasera (ocular)
            draw.polygon([(ox + scope_w - 18, tube_y), (ox + scope_w, tube_y - 3), (ox + scope_w, tube_y + scope_h + 3), (ox + scope_w - 18, tube_y + scope_h)], fill=(36, 44, 58, 255))
            draw.polygon([(ox + 18, tube_y), (ox, tube_y - 2), (ox, tube_y + scope_h + 2), (ox + 18, tube_y + scope_h)], fill=(36, 44, 58, 255))
            # Torretas de ajuste
            draw.rectangle([ox + 50, tube_y - 6, ox + 62, tube_y], fill=(212, 184, 134, 255))
            draw.rectangle([ox + 48, tube_y + scope_h // 2 - 4, ox + 52, tube_y + scope_h // 2 + 4], fill=(212, 184, 134, 255))
            optic_callout = (ox + scope_w // 2, tube_y - 6, f"🎯 {o_name.split(' (')[0][:22]}")

        elif "eotech" in part_optic or "srs" in part_optic or "hologr" in o_name.lower():
            # Mira holográfica EOTech (capucha acorazada rectangular)
            holo_w = 58
            holo_h = 32
            draw.rounded_rectangle(
                [ox + 20, oy - holo_h, ox + 20 + holo_w, oy],
                radius=4,
                fill=(28, 36, 50, 255),
                outline=(212, 184, 134, 255),
                width=2
            )
            # Ventana óptica de cristal (cian translúcido)
            draw.rectangle([ox + 28, oy - holo_h + 6, ox + 20 + holo_w - 8, oy - 6], fill=(56, 189, 248, 80), outline=(56, 189, 248, 200), width=1)
            # Retícula central dorada
            cx = ox + 20 + holo_w // 2
            cy = oy - holo_h // 2
            draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=(245, 158, 11, 240), width=1)
            draw.point([(cx, cy)], fill=(255, 255, 255, 255))
            optic_callout = (ox + 20 + holo_w // 2, oy - holo_h, f"🎯 {o_name.split(' (')[0][:22]}")

        else:
            # Punto rojo colimador compacto (Micro T-1, PK-06, etc.)
            red_w = 42
            red_h = 24
            draw.rounded_rectangle(
                [ox + 30, oy - red_h, ox + 30 + red_w, oy],
                radius=3,
                fill=(30, 41, 59, 255),
                outline=(212, 184, 134, 255),
                width=2
            )
            draw.ellipse([ox + 30 + red_w - 6, oy - red_h + 4, ox + 30 + red_w, oy - 4], fill=(56, 189, 248, 140))
            optic_callout = (ox + 30 + red_w // 2, oy - red_h, f"🎯 {o_name.split(' (')[0][:22]}")

    # 6. Cargador Dinámico (Magazine)
    part_mag = slots.get("magazine", "none")
    mag_x = geom["mag_x"]
    mag_y = ry2
    mag_callout = None
    if part_mag != "none":
        m_item = ATTACHMENTS_CATALOG.get(part_mag, {})
        m_name = m_item.get("name", "")

        if "d60" in part_mag or "drum" in part_mag or "rpk_60" in part_mag:
            # Tambor redondo de alta capacidad (Drum Mag)
            drum_r = 34
            draw.ellipse(
                [mag_x - drum_r, mag_y + 4, mag_x + drum_r, mag_y + 4 + drum_r * 2],
                fill=(24, 30, 42, 255),
                outline=(245, 158, 11, 255),  # Ámbar táctico
                width=2
            )
            # Ranuras del tambor
            for ang in range(0, 360, 45):
                rad = math.radians(ang)
                dx = int(math.cos(rad) * 16)
                dy = int(math.sin(rad) * 16)
                draw.line([(mag_x, mag_y + 4 + drum_r), (mag_x + dx, mag_y + 4 + drum_r + dy)], fill=(71, 85, 105, 200), width=1)
            mag_callout = (mag_x, mag_y + 4 + drum_r * 2, f"🔋 {m_name.split(' (')[0][:20]}")

        elif "mp133" in weapon_id:
            # Tubo depósito escopeta (horizontal paralelo bajo el cañón)
            tube_len = 110 if "8" in part_mag else 80
            draw.rectangle([b_start - 30, by + bh + 4, b_start + tube_len, by + bh + 14], fill=(36, 44, 58, 255), outline=(245, 158, 11, 255), width=2)
            mag_callout = (b_start + tube_len // 2, by + bh + 16, f"🔋 {m_name[:18]}")

        else:
            # Cargador curvo tipo banana / STANAG / AK
            mag_w = 26
            mag_len = 62 if ("60" in part_mag or "30" in part_mag) else 38
            draw.polygon([
                (mag_x - 12, mag_y),
                (mag_x + mag_w - 12, mag_y),
                (mag_x + mag_w - 4, mag_y + mag_len),
                (mag_x - 4, mag_y + mag_len)
            ], fill=(28, 36, 50, 255), outline=(245, 158, 11, 255))
            # Costillas de polímero
            for my_step in range(mag_y + 10, mag_y + mag_len - 6, 8):
                draw.line([(mag_x - 9, my_step), (mag_x + mag_w - 7, my_step)], fill=(71, 85, 105, 180), width=1)
            mag_callout = (mag_x + 5, mag_y + mag_len, f"🔋 {m_name.split(' (')[0][:20]}")

    # 7. Empuñadura Frontal Dinámica (Foregrip)
    part_fg = slots.get("foregrip", "none")
    fg_x = rx2 - 50
    fg_y = ry2 - 6
    fg_callout = None
    if part_fg != "none":
        fg_item = ATTACHMENTS_CATALOG.get(part_fg, {})
        fg_name = fg_item.get("name", "")

        if "fortis" in part_fg or "bcm" in part_fg or "se5" in part_fg or "shift" in fg_name.lower():
            # Empuñadura esqueleto / inclinada hacia adelante
            draw.polygon([
                (fg_x, fg_y),
                (fg_x + 22, fg_y),
                (fg_x + 32, fg_y + 34),
                (fg_x + 16, fg_y + 34)
            ], fill=(30, 41, 59, 255), outline=(96, 165, 250, 255))
            fg_callout = (fg_x + 24, fg_y + 36, f"✊ {fg_name.split(' (')[0][:18]}")
        else:
            # Empuñadura vertical estándar / pesada (RVG / RK-2)
            draw.rounded_rectangle(
                [fg_x, fg_y, fg_x + 18, fg_y + 40],
                radius=3,
                fill=(26, 32, 44, 255),
                outline=(96, 165, 250, 255),
                width=2
            )
            # Textura de agarre
            for ty in range(fg_y + 6, fg_y + 36, 6):
                draw.line([(fg_x + 3, ty), (fg_x + 15, ty)], fill=(96, 165, 250, 140), width=1)
            fg_callout = (fg_x + 9, fg_y + 42, f"✊ {fg_name.split(' (')[0][:18]}")

    # 8. Pistolete (Pistol Grip)
    part_pg = slots.get("pistol_grip", "none")
    px = geom["grip_x"]
    py = ry2 - 2
    if part_pg != "none":
        draw.polygon([
            (px, py),
            (px + 24, py),
            (px + 8, py + 42),
            (px - 10, py + 40)
        ], fill=(30, 41, 59, 255), outline=(148, 163, 184, 255))
        # Guardamonte del gatillo
        draw.arc([px + 14, py - 4, px + 36, py + 18], start=0, end=180, fill=(71, 85, 105, 255), width=2)
        draw.line([(px + 25, py + 2), (px + 22, py + 12)], fill=(212, 184, 134, 255), width=2)  # Gatillo

    # 9. Culata Dinámica (Stock)
    part_stock = slots.get("stock", "none")
    sx = geom["stock_x"]
    sy = ry1 + 6
    stock_callout = None
    if part_stock != "none":
        s_item = ATTACHMENTS_CATALOG.get(part_stock, {})
        s_name = s_item.get("name", "")

        # Tubo buffer de amortiguación
        draw.rectangle([sx - 48, sy + 6, sx, sy + 22], fill=(45, 55, 72, 255), outline=(71, 85, 105, 255), width=1)

        if "prs" in part_stock or "precision" in s_name.lower():
            # Culata pesada de precisión PRS con carrillera regulable
            draw.rounded_rectangle([sx - 125, sy - 8, sx - 40, sy + 46], radius=4, fill=(24, 30, 42, 255), outline=(52, 211, 153, 255), width=2)
            # Carrillera superior elevada
            draw.rectangle([sx - 110, sy - 14, sx - 60, sy - 6], fill=(52, 211, 153, 200))
            # Cantonera de goma gruesa
            draw.rectangle([sx - 132, sy - 6, sx - 124, sy + 44], fill=(15, 23, 42, 255), outline=(52, 211, 153, 255), width=1)
            stock_callout = (sx - 80, sy + 50, f"🪖 {s_name.split(' (')[0][:18]}")

        elif "ctr" in part_stock or "sopmod" in part_stock or "moe" in part_stock or "pt3" in part_stock:
            # Culata táctica telescópica con cantonera de goma
            draw.polygon([
                (sx - 42, sy + 4),
                (sx - 105, sy + 2),
                (sx - 110, sy + 44),
                (sx - 80, sy + 40),
                (sx - 42, sy + 24)
            ], fill=(28, 36, 50, 255), outline=(52, 211, 153, 255))
            # Cantonera de goma
            draw.rectangle([sx - 116, sy, sx - 108, sy + 46], fill=(15, 23, 42, 255), outline=(52, 211, 153, 255), width=1)
            stock_callout = (sx - 75, sy + 48, f"🪖 {s_name.split(' (')[0][:18]}")

        else:
            # Culata estándar de fábrica
            draw.polygon([
                (sx - 35, sy + 6),
                (sx - 95, sy + 6),
                (sx - 98, sy + 40),
                (sx - 35, sy + 22)
            ], fill=(36, 44, 58, 255), outline=(52, 211, 153, 255))
            stock_callout = (sx - 65, sy + 46, f"🪖 {s_name.split(' (')[0][:18]}")

    # 10. Dispositivo Táctico (Laser / Torch)
    part_tac = slots.get("tactical", "none")
    if part_tac != "none":
        t_item = ATTACHMENTS_CATALOG.get(part_tac, {})
        tx = rx2 - 35
        ty = rail_y - 8
        draw.rounded_rectangle([tx, ty, tx + 34, ty + 12], radius=2, fill=(30, 41, 59, 255), outline=(239, 68, 68, 255), width=1)
        # Emisor láser (punto rojo brillante)
        draw.ellipse([tx + 32, ty + 3, tx + 36, ty + 7], fill=(239, 68, 68, 255))
        # Rayo láser guía semitransparente que se proyecta al frente
        draw.line([(tx + 36, ty + 5), (w - 20, ty + 5)], fill=(239, 68, 68, 60), width=1)

    # 11. Banderolas Tácticas de Anclaje (Callouts & Badges)
    font_callout = _get_font(10, bold=True)
    callouts = [c for c in (muzzle_callout, optic_callout, mag_callout, fg_callout, stock_callout) if c]

    for cx, cy, label in callouts:
        tb = draw.textbbox((0, 0), label, font=font_callout)
        tw = tb[2] - tb[0] + 12
        th = tb[3] - tb[1] + 6

        # Posicionar badge dentro de límites
        bx = max(10, min(w - tw - 10, cx - tw // 2))
        by = max(8, min(h - th - 8, cy - th - 6 if cy < h // 2 else cy + 6))

        # Color del badge según categoría
        b_color = (56, 189, 248, 255) if "🔇" in label or "💥" in label else (
            (212, 184, 134, 255) if "🎯" in label else (
                (245, 158, 11, 255) if "🔋" in label else (
                    (96, 165, 250, 255) if "✊" in label else (52, 211, 153, 255)
                )
            )
        )

        draw.rounded_rectangle([bx, by, bx + tw, by + th], radius=4, fill=(15, 23, 42, 235), outline=b_color, width=1)
        draw.text((bx + 6, by + 3), label, fill=(248, 250, 252, 255), font=font_callout)
        # Línea de conexión al anclaje
        draw.line([(cx, cy), (bx + tw // 2, by + (th if cy < h // 2 else 0))], fill=(b_color[0], b_color[1], b_color[2], 120), width=1)

    # 12. Título de plataforma y estado en esquinas
    font_title = _get_font(11, bold=True)
    draw.text((14, 10), f"BANCO MILITAR DE PRUEBAS: {weapon['name'].upper()}", fill=(212, 184, 134, 255), font=font_title)
    draw.text((w - 220, 10), f"ESTADO: MODDING ACTIVO ({len([s for s in slots.values() if s != 'none'])} PIEZAS)", fill=(148, 163, 184, 255), font=font_title)

    return canvas
