"""
TarkovScope - Gestor de Caché de Iconos de Equipamiento, Contenedores & Trueques (Zero-Lag)
Resuelve rutas locales en cache/gear/ (y fallback a _MEIPASS) y descarga asíncronamente en segundo plano
cualquier ícono faltante desde la Wiki oficial sin bloquear la UI.
Módulo de lógica pura (sin dependencias de UI).
"""
import io
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Iterable, Optional, Tuple

import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from core.config import BUNDLE_DIR, CACHE_DIR

GEAR_CACHE_DIR = os.path.join(CACHE_DIR, "gear")
BUNDLED_GEAR_CACHE_DIR = os.path.join(BUNDLE_DIR, "cache", "gear")
os.makedirs(GEAR_CACHE_DIR, exist_ok=True)

_DOWNLOAD_LOCK = threading.Lock()
_IN_FLIGHT: set[str] = set()
_SESSION: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        session = requests.Session()
        retry = Retry(
            total=2,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=16)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Referer": "https://escapefromtarkov.fandom.com/",
            "Accept": "image/avif,image/webp,image/png,image/*,*/*;q=0.8",
        })
        _SESSION = session
    return _SESSION


def get_gear_icon_path(cache_key: str) -> Optional[str]:
    """Retorna la ruta local del ícono en cache/gear/<key>.png si existe y es válido."""
    if not cache_key:
        return None
    safe_key = os.path.basename(cache_key.strip())
    if not safe_key:
        return None
    for base_dir in (GEAR_CACHE_DIR, BUNDLED_GEAR_CACHE_DIR):
        p = os.path.join(base_dir, f"{safe_key}.png")
        if os.path.exists(p) and os.path.getsize(p) > 80:
            return p
    return None


def download_gear_icon(cache_key: str, url: str, timeout: float = 8.0) -> Optional[str]:
    """Descarga un ícono de equipamiento y lo normaliza como PNG transparente en cache/gear/."""
    existing = get_gear_icon_path(cache_key)
    if existing:
        return existing
    if not url or not url.startswith("http"):
        return None

    safe_key = os.path.basename(cache_key.strip())
    dst = os.path.join(GEAR_CACHE_DIR, f"{safe_key}.png")
    tmp = dst + ".tmp"
    try:
        resp = _get_session().get(url, timeout=timeout)
        if resp.status_code != 200 or not resp.content:
            return None
        with Image.open(io.BytesIO(resp.content)) as im:
            rgba = im.convert("RGBA")
            rgba.save(tmp, format="PNG", optimize=True)
        os.replace(tmp, dst)
        return dst
    except Exception:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        return None


def ensure_gear_icon_async(
    cache_key: str,
    url: str,
    on_ready: Optional[Callable[[str], None]] = None,
) -> None:
    """Lanza la descarga en segundo plano si no está en caché y ejecuta on_ready(path) al terminar."""
    existing = get_gear_icon_path(cache_key)
    if existing:
        if on_ready:
            on_ready(existing)
        return
    if not url:
        return

    with _DOWNLOAD_LOCK:
        if cache_key in _IN_FLIGHT:
            return
        _IN_FLIGHT.add(cache_key)

    def worker():
        try:
            path = download_gear_icon(cache_key, url)
            if path and on_ready:
                on_ready(path)
        finally:
            with _DOWNLOAD_LOCK:
                _IN_FLIGHT.discard(cache_key)

    threading.Thread(target=worker, daemon=True).start()


def prewarm_gear_icons(items: Iterable[Tuple[str, str]], max_workers: int = 8) -> int:
    """Descarga en paralelo todos los íconos (cache_key, url) faltantes. Retorna cuántos se descargaron."""
    missing = [(k, u) for k, u in items if k and u and not get_gear_icon_path(k)]
    if not missing:
        return 0
    downloaded = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for res in pool.map(lambda pair: download_gear_icon(pair[0], pair[1]), missing):
            if res:
                downloaded += 1
    return downloaded
