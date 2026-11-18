"""
TarkovScope - Utilidades de Imagen para CustomTkinter (Zero-Lag RAM Cache)
Mantiene un caché en memoria RAM (_CTK_IMAGE_RAM_CACHE) de objetos CTkImage
pre-escalados para que los cambios de mapa, boss o trader tomen 0 ms.
"""
import os
import threading
from typing import Optional, Callable, Tuple, Dict, Any
from PIL import Image, ImageTk
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
_TK_PHOTO_RAM_CACHE: Dict[str, Any] = {}
_PIL_THUMB_RAM_CACHE: Dict[str, Image.Image] = {}
_RAM_CACHE_LOCK = threading.Lock()
_STORY_FULL_PIL_CACHE: Dict[Tuple[str, Tuple[int, int]], Image.Image] = {}
_STORY_FULL_PIL_CACHE_MAX = 6


def clear_image_ram_cache() -> None:
    """Limpia el caché en memoria RAM de imágenes CTkImage."""
    with _RAM_CACHE_LOCK:
        _CTK_IMAGE_RAM_CACHE.clear()
        _TK_PHOTO_RAM_CACHE.clear()
        _PIL_THUMB_RAM_CACHE.clear()
        _STORY_FULL_PIL_CACHE.clear()


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
    """Resuelve rutas dentro de cache/story_chapters en desarrollo, instalación protegida o _MEIPASS."""
    from core.config import resolve_cache_read_path

    return resolve_cache_read_path("story_chapters", *subpaths)


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
        pil_img = pil_img.resize(size, Image.Resampling.BILINEAR)
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
        pil_img = pil_img.resize((target_width, new_h), Image.Resampling.BILINEAR)
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
        pil_img.thumbnail(max_size, Image.Resampling.BILINEAR)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        _CTK_IMAGE_RAM_CACHE[cache_key] = ctk_img
        return ctk_img
    except Exception:
        return None


def get_story_gallery_full_pil(gallery_file: str, max_size: Tuple[int, int] = (1280, 760)) -> Optional[Image.Image]:
    """Retorna la imagen PIL en alta resolución para el modal de zoom al hacer clic en una captura."""
    if not gallery_file:
        return None
    cache_key = (gallery_file, max_size)
    if cache_key in _STORY_FULL_PIL_CACHE:
        img = _STORY_FULL_PIL_CACHE.pop(cache_key)
        _STORY_FULL_PIL_CACHE[cache_key] = img
        return img

    path = _resolve_story_asset_path("gallery", gallery_file)
    if not os.path.exists(path):
        return None
    try:
        pil_img = Image.open(path).convert("RGBA")
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        if len(_STORY_FULL_PIL_CACHE) >= _STORY_FULL_PIL_CACHE_MAX:
            oldest_key = next(iter(_STORY_FULL_PIL_CACHE))
            _STORY_FULL_PIL_CACHE.pop(oldest_key, None)
        _STORY_FULL_PIL_CACHE[cache_key] = pil_img
        return pil_img
    except Exception:
        return None


def get_dynamic_weapon_composite_ctk_image(
    weapon_id: str,
    slots: Dict[str, str],
    target_size: Tuple[int, int] = (680, 260),
    active_slot: str = "",
) -> ctk.CTkImage:
    """
    Genera el plano esquemático dinámico del arma con accesorios montados en tiempo real (<1 ms).
    Permite ver visualmente cómo cambia el arma al instalar cada silenciador, mira, culata o cargador.
    """
    from core.weapon_visual_compositor import render_weapon_workbench_composite
    pil_img = render_weapon_workbench_composite(weapon_id, slots, target_size, active_slot=active_slot)
    return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=target_size)


def get_gear_ctk_icon(
    cache_key: str,
    icon_url: str = "",
    max_size: Tuple[int, int] = (54, 42),
    on_ready: Optional[Callable[[ctk.CTkImage], None]] = None,
) -> Optional[ctk.CTkImage]:
    """
    Carga en O(1) un ícono de blindaje, casco, contenedor, mochila o trueque desde cache/gear/
    manteniendo relación de aspecto. Si falta localmente y se pasa callback, lo descarga en segundo plano.
    """
    if not cache_key:
        return None
    mw, mh = max_size
    ram_key = f"gear:{cache_key}:{mw}x{mh}"
    with _RAM_CACHE_LOCK:
        cached = _CTK_IMAGE_RAM_CACHE.get(ram_key)
    if cached is not None:
        return cached

    from core.gear_cache import get_gear_icon_path, ensure_gear_icon_async

    def _build_ctk_from_path(path: str) -> Optional[ctk.CTkImage]:
        try:
            resample = Image.Resampling.BILINEAR if max(mw, mh) <= 96 else Image.Resampling.LANCZOS
            with Image.open(path) as img:
                rgba = img.convert("RGBA")
                iw, ih = rgba.size
                scale = min(mw / max(1, iw), mh / max(1, ih))
                tw = max(1, int(round(iw * scale)))
                th = max(1, int(round(ih * scale)))
                resized = rgba.resize((tw, th), resample)
                ctk_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(tw, th))
                with _RAM_CACHE_LOCK:
                    _CTK_IMAGE_RAM_CACHE[ram_key] = ctk_img
                return ctk_img
        except Exception:
            return None

    local_path = get_gear_icon_path(cache_key)
    if local_path:
        return _build_ctk_from_path(local_path)

    if icon_url and on_ready:
        def _after_dl(downloaded_path: str):
            built = _build_ctk_from_path(downloaded_path)
            if built:
                try:
                    on_ready(built)
                except Exception:
                    pass

        ensure_gear_icon_async(cache_key, icon_url, on_ready=_after_dl)
    return None


def _get_or_load_pil_thumb(
    cache_key: str,
    path: str,
    max_size: Tuple[int, int],
) -> Optional[Image.Image]:
    """Carga y pre-escala en PIL una miniatura cacheándola en _PIL_THUMB_RAM_CACHE (thread-safe)."""
    if not path or not os.path.exists(path):
        return None
    mw, mh = max_size
    pil_key = f"pil:{cache_key}:{mw}x{mh}"
    with _RAM_CACHE_LOCK:
        cached = _PIL_THUMB_RAM_CACHE.get(pil_key)
    if cached is not None:
        return cached
    try:
        resample = Image.Resampling.BILINEAR if max(mw, mh) <= 96 else Image.Resampling.LANCZOS
        with Image.open(path) as img:
            rgba = img.convert("RGBA")
            rgba.thumbnail((mw, mh), resample)
            thumb = rgba.copy()
        with _RAM_CACHE_LOCK:
            _PIL_THUMB_RAM_CACHE[pil_key] = thumb
        return thumb
    except Exception:
        return None


def get_resized_ctk_image(
    cache_key: str,
    path: str,
    max_size: Tuple[int, int],
) -> Optional[ctk.CTkImage]:
    """Carga, pre-escala en PIL y cachea en RAM un CTkImage para miniaturas locales."""
    if not path:
        return None
    mw, mh = max_size
    ram_key = f"thumb:{cache_key}:{mw}x{mh}"
    with _RAM_CACHE_LOCK:
        cached = _CTK_IMAGE_RAM_CACHE.get(ram_key)
    if cached is not None:
        return cached
    thumb = _get_or_load_pil_thumb(cache_key, path, max_size)
    if thumb is None:
        return None
    tw, th = max(1, thumb.size[0]), max(1, thumb.size[1])
    ctk_img = ctk.CTkImage(light_image=thumb, dark_image=thumb, size=(tw, th))
    with _RAM_CACHE_LOCK:
        _CTK_IMAGE_RAM_CACHE[ram_key] = ctk_img
    return ctk_img


def get_resized_tk_image(
    cache_key: str,
    path: str,
    max_size: Tuple[int, int],
) -> Optional[ImageTk.PhotoImage]:
    """Carga, pre-escala en PIL y cachea en RAM un PhotoImage nativo para widgets tk.Label sin CTkCanvas."""
    if not path:
        return None
    mw, mh = max_size
    ram_key = f"tk:{cache_key}:{mw}x{mh}"
    with _RAM_CACHE_LOCK:
        cached = _TK_PHOTO_RAM_CACHE.get(ram_key)
    if cached is not None:
        return cached
    thumb = _get_or_load_pil_thumb(cache_key, path, max_size)
    if thumb is None:
        return None
    try:
        tk_img = ImageTk.PhotoImage(thumb)
        with _RAM_CACHE_LOCK:
            _TK_PHOTO_RAM_CACHE[ram_key] = tk_img
        return tk_img
    except Exception:
        return None


def prewarm_ui_thumbnails() -> None:
    """Pre-carga miniaturas locales en RAM en segundo plano para apertura instantánea de pestañas."""
    try:
        for t_name in TRADER_IMAGE_URLS:
            if is_image_cached(t_name):
                for sz in ((56, 56), (60, 60), (68, 68)):
                    get_trader_ctk_image(t_name, size=sz)
    except Exception:
        pass

    try:
        for b_id in BOSS_IMAGE_URLS:
            if is_image_cached(b_id):
                for sz in ((42, 42), (108, 108)):
                    get_boss_ctk_image(b_id, size=sz)
    except Exception:
        pass

    try:
        for map_key in MAP_IMAGE_URLS:
            thumb_path = get_cached_map_thumb_path(map_key, (780, 480))
            if os.path.exists(thumb_path) or is_map_cached(map_key):
                get_map_ctk_image(map_key, target_size=(780, 480))
    except Exception:
        pass

    try:
        from core.weapons_data import KAPPA_COLLECTOR_ITEMS, WEAPONS_ARSENAL_DATA

        for wp in WEAPONS_ARSENAL_DATA:
            get_weapon_or_part_ctk_image(wp["id"], size=(66, 36), label_fallback=wp["name"])
            get_weapon_or_part_ctk_image(wp["id"], size=(240, 108), label_fallback=wp["name"])

        for it in KAPPA_COLLECTOR_ITEMS:
            ik = it.get("icon_key", "")
            if ik:
                get_gear_ctk_icon(ik, max_size=(34, 34))
                get_gear_ctk_icon(ik, max_size=(46, 46))
    except Exception:
        pass

    try:
        from core.hideout_crafts_data import HIDEOUT_CRAFTS_DATA, HIDEOUT_STATION_ICONS

        for st_info in HIDEOUT_STATION_ICONS.values():
            ik = st_info.get("icon_key", "")
            if ik:
                get_gear_ctk_icon(ik, max_size=(40, 40))

        for cr in HIDEOUT_CRAFTS_DATA:
            ik = cr.get("icon_key", "")
            if ik:
                get_gear_ctk_icon(ik, max_size=(48, 48))
    except Exception:
        pass

    try:
        from core.barters_data import BARTERS_CATALOG

        for b in BARTERS_CATALOG:
            ck = b.get("cache_key", "")
            if ck:
                get_gear_ctk_icon(ck, max_size=(42, 38))
    except Exception:
        pass

    try:
        from core.containers_data import get_all_storage_items

        for st in get_all_storage_items():
            ck = st.get("cache_key", "")
            if ck:
                get_gear_ctk_icon(ck, max_size=(46, 38))
    except Exception:
        pass

    try:
        from core.armor_data import get_all_protection_items

        for prot in get_all_protection_items():
            ck = prot.get("cache_key", "")
            if ck:
                get_gear_ctk_icon(ck, max_size=(46, 38))
    except Exception:
        pass

    try:
        from core.pmc_systems_data import PMC_SKILLS_CATALOG
        from core.pmc_prestige_achievements_data import PRESTIGE_LEVELS_DATA, TACTICAL_CLOTHING_CATALOG

        for sk in PMC_SKILLS_CATALOG:
            ck = sk.get("cache_key", "")
            if ck:
                get_gear_ctk_icon(ck, max_size=(60, 60))

        for p_data in PRESTIGE_LEVELS_DATA:
            ik = p_data.get("icon_key", "")
            if ik:
                get_gear_ctk_icon(ik, max_size=(52, 52))

        for cl in TACTICAL_CLOTHING_CATALOG:
            ik = cl.get("icon_key", cl.get("id", ""))
            if ik:
                get_gear_ctk_icon(ik, max_size=(64, 64))
    except Exception:
        pass

    try:
        from core.provisions_health_data import PROVISIONS_CATALOG

        for prov in PROVISIONS_CATALOG:
            ik = prov.get("icon_key", prov.get("id", ""))
            if ik:
                get_gear_ctk_icon(ik, max_size=(56, 56))
    except Exception:
        pass

    try:
        from core.keys_data import KEYS_CATALOG, get_key_icon_path

        for k in KEYS_CATALOG:
            path = get_key_icon_path(k["id"])
            if path:
                _get_or_load_pil_thumb(f"key:{k['id']}", path, (42, 42))
                _get_or_load_pil_thumb(f"key:{k['id']}", path, (44, 44))
    except Exception:
        pass

    try:
        from core.medical_data import MEDICAL_CATALOG, get_medical_icon_path

        for m in MEDICAL_CATALOG:
            path = get_medical_icon_path(m["id"])
            if path:
                _get_or_load_pil_thumb(f"med:{m['id']}", path, (58, 44))
    except Exception:
        pass




