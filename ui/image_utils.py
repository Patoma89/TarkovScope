"""
TarkovScope - Utilidades de Imagen para CustomTkinter (Zero-Lag RAM Cache)
Mantiene un caché en memoria RAM (_CTK_IMAGE_RAM_CACHE) de objetos CTkImage
pre-escalados para que los cambios de mapa, boss o trader tomen 0 ms.
"""
import os
import threading
from typing import Optional, Callable, Tuple, Dict, Any
from PIL import Image
import customtkinter as ctk
from core.maps_data import normalize_map_key
from core.image_cache import (
    load_avatar,
    load_map_image,
    load_boss_spawn_map_image,
    load_weapon_or_part_image,
    get_boss_spawn_map_paths,
    get_cached_map_thumb_path,
    get_trader_stock_image_path,
    is_image_cached,
    is_map_cached,
    create_placeholder_avatar,
    create_placeholder_map,
    TRADER_IMAGE_URLS,
    BOSS_IMAGE_URLS,
    MAP_IMAGE_URLS
)

# Caché en memoria RAM de instancias CTkImage (acceso en O(1) = 0 ms)
_CTK_IMAGE_RAM_CACHE: Dict[str, ctk.CTkImage] = {}


def clear_image_ram_cache() -> None:
    """Limpia el caché en memoria RAM de imágenes CTkImage."""
    _CTK_IMAGE_RAM_CACHE.clear()


def get_trader_ctk_image(
    trader_name: str,
    size: Tuple[int, int] = (64, 64),
    widget_callback: Optional[Callable[[ctk.CTkImage], None]] = None
) -> ctk.CTkImage:
    """Retorna un CTkImage del trader desde RAM o miniatura pre-escalada."""
    cache_key = f"trader:{trader_name.lower()}:{size[0]}x{size[1]}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    url = TRADER_IMAGE_URLS.get(trader_name)
    if is_image_cached(trader_name):
        pil_img = load_avatar(trader_name, url, size)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        return ctk_img

    placeholder_pil = create_placeholder_avatar(trader_name, size)
    placeholder_ctk = ctk.CTkImage(light_image=placeholder_pil, dark_image=placeholder_pil, size=size)

    if widget_callback and url:
        def worker():
            new_pil = load_avatar(trader_name, url, size)
            new_ctk = ctk.CTkImage(light_image=new_pil, dark_image=new_pil, size=size)
            _CTK_IMAGE_RAM_CACHE[cache_key] = new_ctk
            widget_callback(new_ctk)

        threading.Thread(target=worker, daemon=True).start()

    return placeholder_ctk


def get_boss_ctk_image(
    boss_id: str,
    size: Tuple[int, int] = (100, 100),
    widget_callback: Optional[Callable[[ctk.CTkImage], None]] = None
) -> ctk.CTkImage:
    """Retorna un CTkImage del boss desde RAM o miniatura pre-escalada."""
    cache_key = f"boss:{boss_id.lower()}:{size[0]}x{size[1]}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    url = BOSS_IMAGE_URLS.get(boss_id)
    if is_image_cached(boss_id):
        pil_img = load_avatar(boss_id, url, size)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        return ctk_img

    placeholder_pil = create_placeholder_avatar(boss_id, size)
    placeholder_ctk = ctk.CTkImage(light_image=placeholder_pil, dark_image=placeholder_pil, size=size)

    if widget_callback and url:
        def worker():
            new_pil = load_avatar(boss_id, url, size)
            new_ctk = ctk.CTkImage(light_image=new_pil, dark_image=new_pil, size=size)
            _CTK_IMAGE_RAM_CACHE[cache_key] = new_ctk
            widget_callback(new_ctk)

        threading.Thread(target=worker, daemon=True).start()

    return placeholder_ctk


def get_map_ctk_image(
    map_id: str,
    target_size: Tuple[int, int] = (780, 480),
    widget_callback: Optional[Callable[[ctk.CTkImage], None]] = None
) -> ctk.CTkImage:
    """Retorna un CTkImage del plano del mapa en 0 ms desde RAM o miniatura en disco."""
    norm_key = normalize_map_key(map_id)
    cache_key = f"map:{norm_key}:{target_size[0]}x{target_size[1]}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    thumb_path = get_cached_map_thumb_path(norm_key, target_size)
    if os.path.exists(thumb_path) or is_map_cached(norm_key):
        pil_img = load_map_image(norm_key, target_size)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        return ctk_img

    placeholder_pil = create_placeholder_map(map_id, target_size)
    placeholder_ctk = ctk.CTkImage(light_image=placeholder_pil, dark_image=placeholder_pil, size=placeholder_pil.size)

    url = MAP_IMAGE_URLS.get(norm_key)
    if widget_callback and url:
        def worker():
            new_pil = load_map_image(norm_key, target_size)
            new_ctk = ctk.CTkImage(light_image=new_pil, dark_image=new_pil, size=new_pil.size)
            _CTK_IMAGE_RAM_CACHE[cache_key] = new_ctk
            widget_callback(new_ctk)

        threading.Thread(target=worker, daemon=True).start()

    return placeholder_ctk


def get_boss_spawn_map_ctk_image(
    boss: Dict[str, Any],
    map_name: str,
    target_size: Tuple[int, int] = (740, 450),
    widget_callback: Optional[Callable[[ctk.CTkImage], None]] = None
) -> ctk.CTkImage:
    """Retorna el CTkImage del mapa con spawns de un Boss desde RAM o disco pre-generado."""
    boss_id = boss.get("id", "boss")
    norm_map = normalize_map_key(map_name)
    cache_key = f"boss_map:{boss_id}:{norm_map}:{target_size[0]}x{target_size[1]}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    thumb_path, _ = get_boss_spawn_map_paths(boss_id, map_name, target_size)
    if os.path.exists(thumb_path):
        pil_img = load_boss_spawn_map_image(boss, map_name, target_size, high_res=False)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        return ctk_img

    # Si no estaba pre-generado aún, generarlo en hilo secundario para no bloquear
    placeholder_pil = create_placeholder_map(f"{boss.get('name', '')} - {map_name}", target_size)
    placeholder_ctk = ctk.CTkImage(light_image=placeholder_pil, dark_image=placeholder_pil, size=placeholder_pil.size)

    def worker():
        pil_img = load_boss_spawn_map_image(boss, map_name, target_size, high_res=False)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        if widget_callback:
            widget_callback(ctk_img)

    threading.Thread(target=worker, daemon=True).start()
    return placeholder_ctk


def get_quest_objective_map_ctk_image(
    map_key: str,
    pin_coords: Tuple[float, float],
    quest_title: str,
    objective_poi: str,
    target_size: Tuple[int, int] = (640, 360),
    widget_callback: Optional[Callable[[ctk.CTkImage], None]] = None
) -> ctk.CTkImage:
    """Retorna el CTkImage del mapa táctico con retícula del objetivo de la misión."""
    norm_map = normalize_map_key(map_key)
    cache_key = f"quest_map:{quest_title}:{norm_map}:{target_size[0]}x{target_size[1]}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    placeholder_pil = create_placeholder_map(f"{quest_title} - {map_key}", target_size)
    placeholder_ctk = ctk.CTkImage(light_image=placeholder_pil, dark_image=placeholder_pil, size=placeholder_pil.size)

    def worker():
        from core.tactical_map_renderer import render_quest_objective_map
        pil_img = render_quest_objective_map(map_key, pin_coords, quest_title, objective_poi, target_size)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        if widget_callback:
            widget_callback(ctk_img)

    threading.Thread(target=worker, daemon=True).start()
    return placeholder_ctk


def get_weapon_or_part_ctk_image(
    image_key: str,
    size: Tuple[int, int] = (200, 96),
    label_fallback: str = ""
) -> ctk.CTkImage:
    """Retorna el CTkImage de un arma o accesorio Gunsmith desde RAM (0 ms)."""
    cache_key = f"wpn:{image_key.lower()}:{size[0]}x{size[1]}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    pil_img = load_weapon_or_part_image(image_key, size, label_fallback=label_fallback)
    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
    _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
    return ctk_img


def get_trader_stock_ctk_image(
    trader_name: str,
    loyalty_level: int,
    target_width: Optional[int] = None
) -> Optional[ctk.CTkImage]:
    """
    Retorna el CTkImage oficial de la cuadrícula de inventario del comerciante en alta resolución.
    Preserva el aspect ratio exacto y se almacena en memoria RAM (_CTK_IMAGE_RAM_CACHE).
    """
    cache_key = f"trader_stock:{trader_name.lower()}:{loyalty_level}:{target_width}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    path = get_trader_stock_image_path(trader_name, loyalty_level)
    if not os.path.exists(path):
        return None

    try:
        pil_img = Image.open(path).convert("RGBA")
        orig_w, orig_h = pil_img.size
        if target_width and target_width != orig_w:
            scale = target_width / orig_w
            new_h = int(orig_h * scale)
            pil_img = pil_img.resize((target_width, new_h), Image.Resampling.LANCZOS)
            final_size = (target_width, new_h)
        else:
            final_size = (orig_w, orig_h)

        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=final_size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        return ctk_img
    except Exception:
        return None


def _resolve_story_asset_path(*subpaths: str) -> str:
    """Resuelve rutas dentro de cache/story_chapters tanto en desarrollo como en PyInstaller (_MEIPASS)."""
    import sys
    from core.config import CACHE_DIR

    p1 = os.path.join(CACHE_DIR, "story_chapters", *subpaths)
    if os.path.exists(p1):
        return p1
    if hasattr(sys, "_MEIPASS"):
        p2 = os.path.join(sys._MEIPASS, "cache", "story_chapters", *subpaths)
        if os.path.exists(p2):
            return p2
    return p1


def get_story_chapter_icon_ctk(icon_file: str, size: Tuple[int, int] = (28, 28)) -> Optional[ctk.CTkImage]:
    """Carga el ícono oficial del capítulo de historia desde cache/story_chapters/."""
    if not icon_file:
        return None
    cache_key = f"story_icon:{icon_file}:{size[0]}x{size[1]}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    path = _resolve_story_asset_path(icon_file)
    if not os.path.exists(path):
        return None
    try:
        pil_img = Image.open(path).convert("RGBA")
        pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        return ctk_img
    except Exception:
        return None


def get_story_chapter_banner_ctk(banner_file: str, target_width: int = 860) -> Optional[ctk.CTkImage]:
    """Carga el banner panorámico oficial del capítulo desde cache/story_chapters/."""
    if not banner_file:
        return None
    cache_key = f"story_banner:{banner_file}:{target_width}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    path = _resolve_story_asset_path(banner_file)
    if not os.path.exists(path):
        return None
    try:
        pil_img = Image.open(path).convert("RGBA")
        w, h = pil_img.size
        new_h = max(80, int(h * (target_width / w)))
        pil_img = pil_img.resize((target_width, new_h), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_width, new_h))
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        return ctk_img
    except Exception:
        return None


def get_story_gallery_ctk_image(
    gallery_file: str,
    max_size: Tuple[int, int] = (340, 192)
) -> Optional[ctk.CTkImage]:
    """Carga una captura o mapa de la galería paso a paso de un capítulo con caché en RAM."""
    if not gallery_file:
        return None
    cache_key = f"story_gal:{gallery_file}:{max_size[0]}x{max_size[1]}"
    if cache_key in _CTK_IMAGE_RAM_CACHE:
        return _CTK_IMAGE_RAM_CACHE[cache_key]

    path = _resolve_story_asset_path("gallery", gallery_file)
    if not os.path.exists(path):
        return None
    try:
        pil_img = Image.open(path).convert("RGBA")
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        return ctk_img
    except Exception:
        return None


def get_story_gallery_full_pil(gallery_file: str, max_size: Tuple[int, int] = (1280, 760)) -> Optional[Image.Image]:
    """Retorna la imagen PIL en alta resolución para el modal de zoom al hacer clic en una captura."""
    if not gallery_file:
        return None
    path = _resolve_story_asset_path("gallery", gallery_file)
    if not os.path.exists(path):
        return None
    try:
        pil_img = Image.open(path).convert("RGBA")
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return pil_img
    except Exception:
        return None


def get_dynamic_weapon_composite_ctk_image(
    weapon_id: str,
    slots: Dict[str, str],
    target_size: Tuple[int, int] = (680, 260)
) -> ctk.CTkImage:
    """
    Genera el plano esquemático dinámico del arma con accesorios montados en tiempo real (<1 ms).
    Permite ver visualmente cómo cambia el arma al instalar cada silenciador, mira, culata o cargador.
    """
    from core.weapon_visual_compositor import render_weapon_workbench_composite
    pil_img = render_weapon_workbench_composite(weapon_id, slots, target_size)
    return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=target_size)



