"""
TarkovScope - Render de rutas del Quest Tracker sobre los mapas calibrados de tarkov.dev.
Lógica pura (PIL): devuelve imágenes listas para mostrar en la UI.
"""
import json
import math
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

from core.config import resolve_cache_read_path
from core.quest_route_data import ROUTE_MAPS_SUBDIR, world_to_image
from core.quest_route_planner import RoutePlan

C_SPAWN = (74, 222, 128)
C_SPAWN_DIM = (190, 190, 190)
C_STOP = (234, 179, 8)
C_ALT = (234, 179, 8)
C_EXTRACT = (56, 189, 248)
C_LINE = (249, 115, 22)
C_OUTLINE = (10, 10, 10)

_BASE_CACHE: Dict[str, Tuple[Image.Image, Dict[str, Any]]] = {}


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("seguisb.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_route_map(map_key: str) -> Optional[Tuple[Image.Image, Dict[str, Any]]]:
    """Imagen base + calibración del mapa (None si no está generada)."""
    if map_key in _BASE_CACHE:
        return _BASE_CACHE[map_key]
    calib_path = resolve_cache_read_path(ROUTE_MAPS_SUBDIR, f"{map_key}.json")
    if not os.path.exists(calib_path):
        return None
    try:
        with open(calib_path, "r", encoding="utf-8") as fh:
            calib = json.load(fh)
        img_path = os.path.join(os.path.dirname(calib_path), calib.get("image", f"{map_key}.jpg"))
        img = Image.open(img_path).convert("RGB")
        img.load()
    except (OSError, ValueError):
        return None
    _BASE_CACHE[map_key] = (img, calib)
    return img, calib


def _blank_base(points_world: List[Sequence[float]]) -> Tuple[Image.Image, Dict[str, Any]]:
    """Lienzo neutro cuando falta la imagen del mapa: escala los puntos para que entren."""
    xs = [p[0] for p in points_world] or [0.0]
    zs = [p[2] for p in points_world] or [0.0]
    span = max(max(xs) - min(xs), max(zs) - min(zs), 50.0)
    size = 1400
    k = (size * 0.85) / span
    calib = {
        "transform": [k, 0, k, 0], "coordinateRotation": 180, "zoom": 0,
        "origin_px": [-(max(xs) * k) - size * 0.075, (min(zs) * k) - size * 0.075],
    }
    img = Image.new("RGB", (size, size), (22, 24, 22))
    d = ImageDraw.Draw(img)
    for g in range(0, size, 70):
        d.line([(g, 0), (g, size)], fill=(34, 37, 34))
        d.line([(0, g), (size, g)], fill=(34, 37, 34))
    return img, calib


def _dot(d: ImageDraw.ImageDraw, xy, r: int, fill, outline=C_OUTLINE, width: int = 3):
    x, y = xy
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=outline, width=width)


def _label(d: ImageDraw.ImageDraw, xy, text: str, font, fill=(255, 255, 255), gap: float = 0.0):
    """Texto a la derecha del punto; si no entra en la imagen, a la izquierda."""
    x, y = xy
    width = d.textlength(text, font=font)
    if x + width + 6 > d.im.size[0] and x - 2 * gap - width > 0:
        x = x - 2 * gap - width
    d.text((x, y), text, font=font, fill=fill, stroke_width=4, stroke_fill=C_OUTLINE)


def _arrow(d: ImageDraw.ImageDraw, a, b, color, width: int):
    d.line([a, b], fill=C_OUTLINE, width=width + 4)
    d.line([a, b], fill=color, width=width)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    size = width * 3.2
    p1 = (mx + size * math.cos(ang), my + size * math.sin(ang))
    p2 = (mx + size * math.cos(ang + 2.5), my + size * math.sin(ang + 2.5))
    p3 = (mx + size * math.cos(ang - 2.5), my + size * math.sin(ang - 2.5))
    d.polygon([p1, p2, p3], fill=color, outline=C_OUTLINE)


def render_route_map(
    map_key: str,
    plan: Optional[RoutePlan],
    spawns: Sequence[Dict[str, Any]] = (),
    selected_spawn: int = -1,
    extracts: Sequence[Dict[str, Any]] = (),
    alternatives: Sequence[Sequence[float]] = (),
    crop_to_route: bool = True,
    target_size: Tuple[int, int] = (900, 640),
) -> Tuple[Image.Image, Dict[str, Any]]:
    """Dibuja spawns, extracciones, ruta numerada y ubicaciones alternativas; recorta a la ruta.

    Devuelve (imagen, vista); con la vista, world_to_view() ubica cualquier punto en la imagen.
    """
    world_pts: List[Sequence[float]] = [s["pos"] for s in spawns] + [e["pos"] for e in extracts]
    if plan:
        world_pts += [plan.start] + [leg.point for leg in plan.legs]
    loaded = load_route_map(map_key)
    base, calib = loaded if loaded else _blank_base(world_pts)
    img = base.copy()
    d = ImageDraw.Draw(img)
    scale = max(img.size) / 2000.0
    r_big, r_small = int(17 * scale) + 6, int(7 * scale) + 3
    font = _font(int(26 * scale) + 8)
    small = _font(int(18 * scale) + 7)

    def px(p):
        return world_to_image(p[0], p[2], calib)

    focus: List[Tuple[float, float]] = []

    chosen_extract = plan.extract_name if plan else None
    for e in extracts:
        if e["name"] == chosen_extract:
            continue  # la extracción elegida se dibuja más abajo, grande y con su propia etiqueta
        x, y = px(e["pos"])
        d.rectangle([x - r_small, y - r_small, x + r_small, y + r_small], fill=C_EXTRACT, outline=C_OUTLINE, width=2)
        _label(d, (x + r_small + 4, y - r_small - 4), e["name"], small, C_EXTRACT, gap=r_small + 4)

    for i, s in enumerate(spawns):
        if i == selected_spawn:
            continue
        _dot(d, px(s["pos"]), r_small, C_SPAWN_DIM, width=2)

    for alt in alternatives:
        x, y = px(alt)
        d.ellipse([x - r_small, y - r_small, x + r_small, y + r_small], outline=C_ALT, width=max(2, int(3 * scale)))

    if plan:
        pts = [px(plan.start)] + [px(leg.point) for leg in plan.legs]
        focus += pts
        lw = max(4, int(7 * scale))
        for a, b in zip(pts, pts[1:]):
            _arrow(d, a, b, C_LINE, lw)
        _dot(d, pts[0], r_big, C_SPAWN)
        _label(d, (pts[0][0] + r_big + 4, pts[0][1] - r_big * 2.2), "SPAWN", font, C_SPAWN, gap=r_big + 4)
        focus.append((min(img.size[0], pts[0][0] + r_big + 12 + d.textlength("SPAWN", font=font)), pts[0][1]))
        # Paradas que caen en el mismo lugar se dibujan como un solo marcador "1-2".
        markers: List[List[Any]] = []  # [xy, [números]]
        n = 0
        for leg, xy in zip(plan.legs, pts[1:]):
            if leg.stop is None:
                x, y = xy
                d.rectangle([x - r_big, y - r_big, x + r_big, y + r_big], fill=C_EXTRACT, outline=C_OUTLINE, width=3)
                text = f"EXTRACCIÓN: {plan.extract_name}"
                _label(d, (x + r_big + 4, y - r_big), text, font, C_EXTRACT, gap=r_big + 4)
                # Que el recorte deje ver la etiqueta completa.
                focus.append((min(img.size[0], x + r_big + 12 + d.textlength(text, font=font)), y))
                continue
            n += 1
            same = next((m for m in markers if math.hypot(m[0][0] - xy[0], m[0][1] - xy[1]) < r_big), None)
            if same:
                same[1].append(n)
            else:
                markers.append([xy, [n]])
        for xy, nums in markers:
            text = str(nums[0]) if len(nums) == 1 else f"{nums[0]}-{nums[-1]}"
            tw = d.textlength(text, font=font)
            r = max(r_big, int(tw / 2) + 6)
            _dot(d, xy, r, C_STOP)
            d.text((xy[0] - tw / 2, xy[1] - font.size * 0.62), text, font=font, fill=(0, 0, 0))
    elif 0 <= selected_spawn < len(spawns):
        xy = px(spawns[selected_spawn]["pos"])
        focus.append(xy)
        _dot(d, xy, r_big, C_SPAWN)

    crop_x0, crop_y0 = 0, 0
    if crop_to_route and len(focus) >= 2:
        margin = 0.12 * max(img.size)
        x0 = max(0, min(p[0] for p in focus) - margin)
        y0 = max(0, min(p[1] for p in focus) - margin)
        x1 = min(img.size[0], max(p[0] for p in focus) + margin)
        y1 = min(img.size[1], max(p[1] for p in focus) + margin)
        # Mantener la relación de aspecto del destino para que no se deforme.
        want = target_size[0] / target_size[1]
        w, h = x1 - x0, y1 - y0
        if w / max(h, 1) < want:
            grow = (h * want - w) / 2
            x0, x1 = max(0, x0 - grow), min(img.size[0], x1 + grow)
        else:
            grow = (w / want - h) / 2
            y0, y1 = max(0, y0 - grow), min(img.size[1], y1 + grow)
        crop_x0, crop_y0 = int(x0), int(y0)
        img = img.crop((crop_x0, crop_y0, int(x1), int(y1)))

    full_w = img.size[0]
    img.thumbnail(target_size, Image.LANCZOS)
    view = {"calib": calib, "offset": (crop_x0, crop_y0), "scale": img.size[0] / max(1, full_w)}
    return img, view


def world_to_view(p: Sequence[float], view: Dict[str, Any]) -> Tuple[float, float]:
    """Punto mundo -> píxel de la imagen devuelta por render_route_map (tras recorte y escala)."""
    x, y = world_to_image(p[0], p[2], view["calib"])
    return (x - view["offset"][0]) * view["scale"], (y - view["offset"][1]) * view["scale"]
