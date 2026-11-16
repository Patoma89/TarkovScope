"""
TarkovScope - Generador de mapas calibrados para el Quest Tracker (herramienta de desarrollo).

Para cada mapa del dataset de rutas:
  * Si tarkov.dev publica mosaicos (tiles), los descarga y los une en una sola imagen.
  * Si solo hay SVG (Streets, Lighthouse), lo rasteriza con Microsoft Edge en modo headless.
Guarda cache/route_maps/<mapa>.jpg y <mapa>.json con la calibración mundo -> píxel, de modo
que la app pueda dibujar rutas en metros reales sin conexión.

Uso:
    python tools_build_route_maps.py               # todos los mapas
    python tools_build_route_maps.py customs woods # solo algunos
    python tools_build_route_maps.py --refresh-data  # además re-descarga el dataset de rutas
"""
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple

import requests
from PIL import Image

from core.config import CACHE_DIR
from core.quest_route_data import (
    ROUTE_MAPS_SUBDIR,
    load_route_dataset,
    refresh_route_dataset,
    world_to_crs_pixel,
)

TARGET_MAX_SIDE = 2400
JPEG_QUALITY = 86
BG_COLOR = (18, 20, 18)
EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def _corner_pixels(bounds: List[List[float]], meta: Dict[str, Any]) -> List[Tuple[float, float]]:
    """Proyecta las 4 esquinas de los bounds de tarkov.dev ([x, z] por esquina) a píxeles zoom 0."""
    xs = [bounds[0][0], bounds[1][0]]
    zs = [bounds[0][1], bounds[1][1]]
    return [world_to_crs_pixel(x, z, meta, 0) for x in xs for z in zs]


def _leaflet_overlay_box(bounds: List[List[float]], meta: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """Caja que ocupa un L.svgOverlay: bbox de los píxeles proyectados de las esquinas NW y SE."""
    lats = [bounds[0][1], bounds[1][1]]
    lngs = [bounds[0][0], bounds[1][0]]
    nw = world_to_crs_pixel(min(lngs), max(lats), meta, 0)
    se = world_to_crs_pixel(max(lngs), min(lats), meta, 0)
    return min(nw[0], se[0]), min(nw[1], se[1]), max(nw[0], se[0]), max(nw[1], se[1])


def _fetch(url: str) -> Optional[bytes]:
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and r.content:
            return r.content
    except requests.RequestException:
        pass
    return None


def build_from_tiles(meta: Dict[str, Any]) -> Tuple[Image.Image, Dict[str, Any]]:
    corners = _corner_pixels(meta["bounds"], meta)
    min_x0 = min(p[0] for p in corners)
    min_y0 = min(p[1] for p in corners)
    max_x0 = max(p[0] for p in corners)
    max_y0 = max(p[1] for p in corners)
    side0 = max(max_x0 - min_x0, max_y0 - min_y0)
    zoom = int(math.floor(math.log2(TARGET_MAX_SIDE / side0)))
    zoom = max(meta.get("minZoom") or 0, min(meta.get("maxZoom") or 6, zoom))
    k = 2 ** zoom
    ts = int(meta.get("tileSize") or 256)
    min_x, min_y, max_x, max_y = min_x0 * k, min_y0 * k, max_x0 * k, max_y0 * k
    tx0, ty0 = int(math.floor(min_x / ts)), int(math.floor(min_y / ts))
    tx1, ty1 = int(math.floor((max_x - 1) / ts)), int(math.floor((max_y - 1) / ts))
    origin = (tx0 * ts, ty0 * ts)
    width, height = (tx1 - tx0 + 1) * ts, (ty1 - ty0 + 1) * ts
    canvas = Image.new("RGB", (width, height), BG_COLOR)

    jobs = [(tx, ty) for tx in range(tx0, tx1 + 1) for ty in range(ty0, ty1 + 1)]

    def get_tile(job):
        tx, ty = job
        url = meta["tilePath"].replace("{z}", str(zoom)).replace("{x}", str(tx)).replace("{y}", str(ty))
        return job, _fetch(url)

    ok = 0
    with ThreadPoolExecutor(max_workers=12) as pool:
        for (tx, ty), data in pool.map(get_tile, jobs):
            if not data:
                continue
            tile = Image.open(io.BytesIO(data)).convert("RGBA")
            if tile.size != (ts, ts):
                tile = tile.resize((ts, ts), Image.LANCZOS)
            canvas.paste(tile, (tx * ts - origin[0], ty * ts - origin[1]), tile)
            ok += 1
    if ok == 0:
        raise RuntimeError("no se pudo descargar ningún mosaico")

    # Recortar al área real del mapa (los mosaicos de borde sobran).
    crop = (
        max(0, int(min_x - origin[0])), max(0, int(min_y - origin[1])),
        min(width, int(math.ceil(max_x - origin[0]))), min(height, int(math.ceil(max_y - origin[1]))),
    )
    canvas = canvas.crop(crop)
    origin = (origin[0] + crop[0], origin[1] + crop[1])
    calib = {"zoom": zoom, "origin_px": [origin[0], origin[1]], "source": "tiles", "tiles": f"{ok}/{len(jobs)}"}
    return canvas, calib


def _find_edge() -> str:
    for cand in EDGE_CANDIDATES:
        if os.path.exists(cand):
            return cand
    found = shutil.which("msedge")
    if found:
        return found
    raise RuntimeError("Microsoft Edge no encontrado: es necesario para rasterizar los mapas SVG")


def build_from_svg(meta: Dict[str, Any]) -> Tuple[Image.Image, Dict[str, Any]]:
    bounds = meta.get("svgBounds") or meta["bounds"]
    bx0, by0, bx1, by1 = _leaflet_overlay_box(bounds, meta)
    scale = TARGET_MAX_SIDE / max(bx1 - bx0, by1 - by0)
    width, height = int(round((bx1 - bx0) * scale)), int(round((by1 - by0) * scale))
    svg_bytes = _fetch(meta["svgPath"])
    if not svg_bytes:
        raise RuntimeError("no se pudo descargar el SVG")

    work = tempfile.mkdtemp(prefix="ttc_svg_")
    try:
        svg_path = os.path.join(work, "map.svg")
        with open(svg_path, "wb") as fh:
            fh.write(svg_bytes)
        html_path = os.path.join(work, "map.html")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(
                "<!doctype html><html><body style='margin:0;background:#121412;overflow:hidden'>"
                f"<img src='map.svg' style='display:block;width:{width}px;height:{height}px'>"
                "</body></html>"
            )
        png_path = os.path.join(work, "out.png")
        subprocess.run(
            [_find_edge(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--user-data-dir={os.path.join(work, 'profile')}",
             f"--window-size={width},{height}", f"--screenshot={png_path}",
             "file:///" + html_path.replace("\\", "/")],
            check=True, timeout=180, capture_output=True,
        )
        # Edge headless devuelve el control antes de terminar de escribir la captura.
        img = None
        deadline = time.time() + 120
        last_size = -1
        while time.time() < deadline:
            if os.path.exists(png_path):
                size = os.path.getsize(png_path)
                if size > 0 and size == last_size:
                    img = Image.open(png_path).convert("RGB")
                    img.load()
                    break
                last_size = size
            time.sleep(1.0)
        if img is None:
            raise RuntimeError("Edge no generó la captura del SVG a tiempo")
    finally:
        time.sleep(2.0)
        shutil.rmtree(work, ignore_errors=True)
    if img.size != (width, height):
        img = img.resize((width, height), Image.LANCZOS)
    zoom = math.log2(scale)
    calib = {"zoom": zoom, "origin_px": [bx0 * scale, by0 * scale], "source": "svg"}
    return img, calib


def build_map(map_entry: Dict[str, Any], out_dir: str) -> str:
    meta = map_entry["meta"]
    if meta.get("tilePath"):
        img, calib = build_from_tiles(meta)
    elif meta.get("svgPath"):
        img, calib = build_from_svg(meta)
    else:
        raise RuntimeError("el mapa no tiene ni mosaicos ni SVG")
    calib.update({
        "map": map_entry["key"],
        "transform": meta["transform"],
        "coordinateRotation": meta.get("coordinateRotation", 0),
        "width": img.size[0],
        "height": img.size[1],
        "image": f"{map_entry['key']}.jpg",
    })
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, calib["image"]), "JPEG", quality=JPEG_QUALITY, optimize=True)
    with open(os.path.join(out_dir, f"{map_entry['key']}.json"), "w", encoding="utf-8") as fh:
        json.dump(calib, fh, indent=1)
    return f"{map_entry['key']}: {img.size[0]}x{img.size[1]} ({calib['source']})"


def main(argv: List[str]) -> int:
    if "--refresh-data" in argv:
        print("Descargando dataset de rutas desde tarkov.dev...")
        print("OK" if refresh_route_dataset() else "FALLÓ (se usa el dataset local)")
    wanted = [a for a in argv if not a.startswith("--")]
    dataset = load_route_dataset(force=True)
    out_dir = os.path.join(CACHE_DIR, ROUTE_MAPS_SUBDIR)
    failures = 0
    for key, entry in dataset.get("maps", {}).items():
        if wanted and key not in wanted:
            continue
        try:
            print(build_map(entry, out_dir))
        except Exception as exc:  # herramienta de desarrollo: reportar y seguir con el resto
            failures += 1
            print(f"{key}: ERROR {exc}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
