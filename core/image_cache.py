"""
TarkovScope - Gestor de Caché de Imágenes Locales y Pre-Baking Zero-Lag
Descarga, almacena en disco y pre-genera miniaturas optimizadas (cache/thumbs/)
y mapas tácticos con zonas de spawn de Bosses superpuestas (cache/boss_maps/).
"""
import os
import sys
import requests
import logging
from typing import Dict, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont
from core.config import CACHE_DIR
from core.maps_data import normalize_map_key, get_map_extractions_with_coords, get_map_tactical_pois

logger = logging.getLogger("TarkovScope.ImageCache")

AVATARS_DIR = os.path.join(CACHE_DIR, "avatars")
MAPS_DIR = os.path.join(CACHE_DIR, "maps")
THUMBS_DIR = os.path.join(CACHE_DIR, "thumbs")
BOSS_MAPS_DIR = os.path.join(CACHE_DIR, "boss_maps")
WEAPONS_DIR = os.path.join(CACHE_DIR, "weapons")
TRADER_STOCKS_DIR = os.path.join(CACHE_DIR, "trader_stocks")

for _d in (AVATARS_DIR, MAPS_DIR, THUMBS_DIR, BOSS_MAPS_DIR, WEAPONS_DIR, TRADER_STOCKS_DIR):
    os.makedirs(_d, exist_ok=True)

# URLs oficiales de la Wiki de Escape from Tarkov
TRADER_IMAGE_URLS: Dict[str, str] = {
    "Prapor": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/6/6b/Prapor_Portrait.png",
    "Therapist": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/c/c7/Therapist_Portrait.png",
    "Skier": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/0a/Skier_Portrait.png",
    "Peacekeeper": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/08/Peacekeeper_Portrait.png",
    "Mechanic": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/ef/Mechanic_Portrait.png",
    "Ragman": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/8/8b/Ragman_Portrait.png",
    "Jaeger": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/d1/Jaeger_Portrait.png",
    "Fence": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/f7/Fence_Portrait.png",
    "Ref": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/c/c8/Ref_Infobox.png",
    "Lightkeeper": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/9/9d/LightkeeperInfobox.png",
    "BTR Driver": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a9/BTR_Driver_Portrait.png",
}

BOSS_IMAGE_URLS: Dict[str, str] = {
    "reshala": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/1a/Dealmaker_Portrait.png",
    "killa": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/ac/Killa_Portrait.png",
    "tagilla": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/b4/Tagilla_Portrait.png",
    "shturman": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/3f/Shturman_Portrait.png",
    "glukhar": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/b7/GlukharInfobox.png",
    "sanitar": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/23/Sanitar_Portrait.png",
    "kaban": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/e3/Kaban_Portrait.png",
    "kollontay": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/d3/Kollontay_Portrait.png",
    "the_goons": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/16/KnightPortrait.png",
    "partisan": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/6/68/Partisan_Portrait.png",
    "zryachiy": "https://assets.tarkov.dev/zryachiy-portrait.png",
    "cultists": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/d6/CultistPriest.png",
    "wedge": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/eb/The_Wedge_Portrait.png",
}

# Planos 2D tácticos reales verificados de la Wiki
MAP_IMAGE_URLS: Dict[str, str] = {
    "groundzero": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/9/9b/GroundZeroByxTycho.png",
    "customs": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a3/Re3mrCustoms2.jpg",
    "woods": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/05/Glory4lyfeWoods_map_v4_marked.png",
    "factory": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/33/Factory2DMapbyRe3mr.jpg",
    "shoreline": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/17/Shoreline2DMapByMonkiUpdatedByJindouz.png",
    "interchange": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/27/InterchangeMapByre3mr.jpg",
    "reserve": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/7c/JindouzReserve_v1_2dmap.png",
    "lighthouse": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/9/9d/Lighthouse_Interactive_Map_Base.png",
    "streetsoftarkov": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/71/StreetsOfTarkov2DMapByJindouz.png",
    "lab": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/fd/The_Lab_Interactive_Map_Base.png",
}


def _get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Obtiene una fuente TrueType del sistema (Segoe UI / Arial) o fallback por defecto."""
    candidates = ["segoeuib.ttf", "arialbd.ttf", "segoeui.ttf", "arial.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def get_cached_image_path(name: str) -> str:
    """Retorna la ruta del archivo de avatar en caché, soportando PyInstaller _MEIPASS."""
    clean_name = name.lower().replace(" ", "_") + ".png"
    local_p = os.path.join(AVATARS_DIR, clean_name)
    if not os.path.exists(local_p) and hasattr(sys, '_MEIPASS'):
        bundle_p = os.path.join(sys._MEIPASS, "cache", "avatars", clean_name)
        if os.path.exists(bundle_p):
            return bundle_p
    return local_p


get_cached_avatar_path = get_cached_image_path


def get_cached_map_path(map_id: str) -> str:
    """Retorna la ruta del archivo de plano de mapa original en caché, soportando PyInstaller _MEIPASS."""
    norm_key = normalize_map_key(map_id)
    local_p = os.path.join(MAPS_DIR, f"{norm_key}.png")
    if not os.path.exists(local_p) and hasattr(sys, '_MEIPASS'):
        bundle_p = os.path.join(sys._MEIPASS, "cache", "maps", f"{norm_key}.png")
        if os.path.exists(bundle_p):
            return bundle_p
    return local_p


def get_trader_stock_image_path(trader_name: str, loyalty_level: int) -> str:
    """Retorna la ruta al archivo PNG de la cuadrícula de inventario oficial del comerciante."""
    clean_trader = trader_name.replace(" ", "").capitalize()
    file_name = f"{clean_trader}{loyalty_level}Stock.png"
    local_p = os.path.join(TRADER_STOCKS_DIR, file_name)
    if not os.path.exists(local_p) and hasattr(sys, '_MEIPASS'):
        bundle_p = os.path.join(sys._MEIPASS, "cache", "trader_stocks", file_name)
        if os.path.exists(bundle_p):
            return bundle_p
    return local_p


def get_cached_map_thumb_path(map_id: str, size: Tuple[int, int]) -> str:
    """Retorna la ruta del thumbnail pre-escalado en disco, soportando PyInstaller _MEIPASS."""
    norm_key = normalize_map_key(map_id)
    thumb_name = f"map_{norm_key}_{size[0]}x{size[1]}.png"
    local_p = os.path.join(THUMBS_DIR, thumb_name)
    if not os.path.exists(local_p) and hasattr(sys, '_MEIPASS'):
        bundle_p = os.path.join(sys._MEIPASS, "cache", "thumbs", thumb_name)
        if os.path.exists(bundle_p):
            return bundle_p
    return local_p


def get_boss_spawn_map_paths(boss_id: str, map_name: str, thumb_size: Tuple[int, int] = (740, 450)) -> Tuple[str, str]:
    """Retorna (ruta_thumb, ruta_hd) del mapa de spawns de un Boss, soportando PyInstaller _MEIPASS."""
    norm_map = normalize_map_key(map_name)
    clean_boss = boss_id.lower().strip()
    thumb_name = f"boss_{clean_boss}_{norm_map}_{thumb_size[0]}x{thumb_size[1]}.png"
    hd_name = f"boss_{clean_boss}_{norm_map}_hd.png"
    thumb_path = os.path.join(BOSS_MAPS_DIR, thumb_name)
    hd_path = os.path.join(BOSS_MAPS_DIR, hd_name)
    if not os.path.exists(thumb_path) and hasattr(sys, '_MEIPASS'):
        bundle_t = os.path.join(sys._MEIPASS, "cache", "boss_maps", thumb_name)
        if os.path.exists(bundle_t):
            thumb_path = bundle_t
    if not os.path.exists(hd_path) and hasattr(sys, '_MEIPASS'):
        bundle_h = os.path.join(sys._MEIPASS, "cache", "boss_maps", hd_name)
        if os.path.exists(bundle_h):
            hd_path = bundle_h
    return thumb_path, hd_path


def is_image_cached(name: str) -> bool:
    return os.path.exists(get_cached_image_path(name))


def is_map_cached(map_id: str) -> bool:
    return os.path.exists(get_cached_map_path(map_id))


def download_and_save_image(url: str, save_path: str) -> bool:
    """Descarga una imagen de internet y la guarda en disco con referer de la wiki."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TarkovScope/2.0",
            "Referer": "https://escapefromtarkov.fandom.com/"
        }
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(save_path, "wb") as f:
                f.write(resp.content)
            return True
    except Exception as e:
        logger.warning("Fallo al descargar imagen desde %s: %s", url, e)
    return False


def create_placeholder_avatar(text: str, size: tuple = (80, 80), bg_color: str = "#20252F") -> Image.Image:
    """Genera un avatar táctico alternativo con iniciales si no hay conexión."""
    img = Image.new("RGBA", size, bg_color)
    draw = ImageDraw.Draw(img)
    initials = "".join([part[0] for part in text.split()[:2]]).upper() or "?"

    w, h = size
    draw.rectangle([0, 0, w - 1, h - 1], outline="#E5732F", width=2)
    font = _get_font(max(14, h // 3), bold=True)
    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) // 2, (h - th) // 2), initials, fill="#FFFFFF", font=font)
    return img


def create_placeholder_map(text: str, size: tuple = (740, 440)) -> Image.Image:
    """Genera un plano táctico militar esquemático de mapa."""
    img = Image.new("RGBA", size, "#12151B")
    draw = ImageDraw.Draw(img)
    w, h = size
    draw.rectangle([2, 2, w - 3, h - 3], outline="#2B323D", width=2)

    for x in range(40, w, 60):
        draw.line([(x, 0), (x, h)], fill="#1A1F28", width=1)
    for y in range(40, h, 60):
        draw.line([(0, y), (w, y)], fill="#1A1F28", width=1)

    font = _get_font(18, bold=True)
    label = f"PLANO TÁCTICO: {text.upper()}"
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) // 2, (h - th) // 2), label, fill="#E5732F", font=font)
    return img


def load_avatar(name: str, url: Optional[str] = None, size: tuple = (80, 80)) -> Image.Image:
    """Carga el avatar desde la caché de miniaturas o lo genera una única vez."""
    clean_name = name.lower().replace(" ", "_")
    thumb_name = f"avatar_{clean_name}_{size[0]}x{size[1]}.png"
    thumb_path = os.path.join(THUMBS_DIR, thumb_name)
    if not os.path.exists(thumb_path) and hasattr(sys, '_MEIPASS'):
        bundle_t = os.path.join(sys._MEIPASS, "cache", "thumbs", thumb_name)
        if os.path.exists(bundle_t):
            thumb_path = bundle_t

    if os.path.exists(thumb_path):
        try:
            return Image.open(thumb_path).convert("RGBA")
        except Exception:
            pass

    raw_path = get_cached_image_path(name)
    if not os.path.exists(raw_path) and url:
        download_and_save_image(url, raw_path)

    if os.path.exists(raw_path):
        try:
            img = Image.open(raw_path).convert("RGBA")
            img = img.resize(size, Image.Resampling.LANCZOS)
            img.save(thumb_path, "PNG")
            return img
        except Exception:
            pass

    return create_placeholder_avatar(name, size)


def load_map_image(map_id: str, target_size: Tuple[int, int] = (780, 480)) -> Image.Image:
    """
    Carga el thumbnail pre-escalado del mapa en <3 ms desde cache/thumbs/.
    Si aún no existe el thumbnail, lo genera una sola vez a partir del mapa en cache/maps/.
    """
    norm_key = normalize_map_key(map_id)
    thumb_path = get_cached_map_thumb_path(norm_key, target_size)

    # 1. Lectura instantánea de miniatura pre-horneada (Sin LANCZOS en vivo)
    if os.path.exists(thumb_path):
        try:
            return Image.open(thumb_path).convert("RGBA")
        except Exception:
            pass

    # 2. Si no existe el thumbnail, abrir el mapa original (o descargarlo) y guardar el thumbnail
    raw_path = get_cached_map_path(norm_key)
    if not os.path.exists(raw_path):
        url = MAP_IMAGE_URLS.get(norm_key)
        if url:
            download_and_save_image(url, raw_path)

    if os.path.exists(raw_path):
        try:
            img = Image.open(raw_path).convert("RGBA")
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            img.save(thumb_path, "PNG")
            return img
        except Exception as e:
            logger.warning("Error pre-generando miniatura para %s: %s", norm_key, e)

    return create_placeholder_map(map_id, target_size)


def load_full_res_map_image(map_id: str, max_dim: int = 2000) -> Image.Image:
    """Carga el mapa en alta resolución (para el visor interactivo Zoom/Pan)."""
    norm_key = normalize_map_key(map_id)
    raw_path = get_cached_map_path(norm_key)
    if os.path.exists(raw_path):
        try:
            img = Image.open(raw_path).convert("RGBA")
            if max(img.size) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            return img
        except Exception:
            pass
    return load_map_image(norm_key, (1200, 800))


_BOSS_STICKER_PIL_CACHE: Dict[Tuple[str, int], Image.Image] = {}


def get_boss_chibi_sticker(boss_id: str, target_size: int = 56) -> Optional[Image.Image]:
    """
    Carga y escala la miniatura en estilo sticker chibi del Boss para dibujarla
    en los puntos de spawn tácticos de los mapas con 0 ms de latencia.
    """
    clean_id = (boss_id or "boss").lower().strip()
    cache_key = (clean_id, target_size)
    if cache_key in _BOSS_STICKER_PIL_CACHE:
        return _BOSS_STICKER_PIL_CACHE[cache_key]

    sticker_path = os.path.join(CACHE_DIR, "boss_stickers", f"{clean_id}.png")
    if not os.path.exists(sticker_path):
        alt_ids = {
            "the_goons": "the_goons",
            "goons": "the_goons",
            "knight": "the_goons",
            "priest": "cultists",
            "cultist": "cultists",
        }
        mapped_id = alt_ids.get(clean_id, clean_id)
        sticker_path = os.path.join(CACHE_DIR, "boss_stickers", f"{mapped_id}.png")

    if not os.path.exists(sticker_path) and hasattr(sys, '_MEIPASS'):
        bundle_stk = os.path.join(sys._MEIPASS, "cache", "boss_stickers", f"{clean_id}.png")
        if os.path.exists(bundle_stk):
            sticker_path = bundle_stk

    if os.path.exists(sticker_path):
        try:
            stk = Image.open(sticker_path).convert("RGBA")
            stk.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
            _BOSS_STICKER_PIL_CACHE[cache_key] = stk
            return stk
        except Exception as e:
            logger.warning("Error cargando boss sticker para %s: %s", clean_id, e)

    avatar_path = get_cached_avatar_path(clean_id)
    if os.path.exists(avatar_path):
        try:
            av = Image.open(avatar_path).convert("RGBA")
            av.thumbnail((target_size - 8, target_size - 8), Image.Resampling.LANCZOS)
            aw, ah = av.size
            bg = Image.new("RGBA", (aw + 8, ah + 8), (0, 0, 0, 0))
            d = ImageDraw.Draw(bg)
            d.ellipse([0, 0, aw + 7, ah + 7], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)
            bg.paste(av, (4, 4), av)
            _BOSS_STICKER_PIL_CACHE[cache_key] = bg
            return bg
        except Exception:
            pass

    return None


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


def load_boss_spawn_map_image(*args, **kwargs):
    from core.tactical_map_renderer import load_boss_spawn_map_image as _fn
    return _fn(*args, **kwargs)


def render_map_with_user_markers(*args, **kwargs):
    from core.tactical_map_renderer import render_map_with_user_markers as _fn
    return _fn(*args, **kwargs)


def render_quest_objective_map(*args, **kwargs):
    from core.tactical_map_renderer import render_quest_objective_map as _fn
    return _fn(*args, **kwargs)


def get_pin_color_for_index(idx_zero_based: int) -> str:
    from core.tactical_map_renderer import get_pin_color_for_index as _fn
    return _fn(idx_zero_based)


def prebake_all_assets(force_boss_maps: bool = False) -> None:
    """
    Pre-genera en disco todas las miniaturas de mapas (cache/thumbs/) y todos los mapas
    de spawns de Bosses (cache/boss_maps/) para garantizar 0 ms de espera en la interfaz.
    """
    from core.bosses_data import get_all_bosses

    if force_boss_maps and os.path.exists(BOSS_MAPS_DIR):
        for fname in os.listdir(BOSS_MAPS_DIR):
            if fname.endswith(".png"):
                try:
                    os.remove(os.path.join(BOSS_MAPS_DIR, fname))
                except OSError:
                    pass

    # 1. Pre-bake de los 10 mapas principales en tamaño UI (780, 480)
    for map_key in MAP_IMAGE_URLS.keys():
        load_map_image(map_key, (780, 480))

    # 2. Pre-bake de todos los mapas de spawns de los 12 Bosses (740, 450)
    for boss in get_all_bosses():
        b_id = boss.get("id", "")
        load_avatar(b_id, BOSS_IMAGE_URLS.get(b_id), (42, 42))
        load_avatar(b_id, BOSS_IMAGE_URLS.get(b_id), (108, 108))
        for m_name in boss.get("maps", []):
            load_boss_spawn_map_image(boss, m_name, (740, 450), high_res=False)

    # 3. Pre-bake de avatares de Traders (56, 56) y (68, 68)
    for tr_name, tr_url in TRADER_IMAGE_URLS.items():
        load_avatar(tr_name, tr_url, (56, 56))
        load_avatar(tr_name, tr_url, (68, 68))

    # 4. Pre-bake de miniaturas de Armas y Piezas Gunsmith
    from core.weapons_data import WEAPONS_ARSENAL_DATA, GUNSMITH_GUIDES_DATA
    for wp in WEAPONS_ARSENAL_DATA:
        load_weapon_or_part_image(wp["id"], (66, 36), wp["name"])
        load_weapon_or_part_image(wp["id"], (240, 108), wp["name"])
        for p_key, p_lbl in wp.get("featured_parts", []):
            load_weapon_or_part_image(p_key, (92, 54), p_lbl)
    for gs in GUNSMITH_GUIDES_DATA:
        load_weapon_or_part_image(gs.get("image_key", f"gs_{gs['part']}"), (210, 104), gs["weapon"])
        for p_key, _ in gs.get("parts_detailed", []):
            load_weapon_or_part_image(p_key, (60, 40), "MOD")


def load_weapon_or_part_image(
    image_key: str,
    target_size: Tuple[int, int] = (200, 96),
    label_fallback: str = ""
) -> Image.Image:
    """
    Carga y centra la imagen de un arma o pieza Gunsmith sobre un lienzo táctico
    del tamaño exacto solicitado, guardando la miniatura en cache/thumbs/ para 0 ms de carga.
    """
    clean_key = image_key.lower().strip()
    thumb_path = os.path.join(THUMBS_DIR, f"wpn_{clean_key}_{target_size[0]}x{target_size[1]}.png")
    if os.path.exists(thumb_path):
        try:
            return Image.open(thumb_path).convert("RGBA")
        except Exception:
            pass

    raw_path = os.path.join(WEAPONS_DIR, f"{clean_key}.png")
    if not os.path.exists(raw_path) and hasattr(sys, '_MEIPASS'):
        bundle_wpn = os.path.join(sys._MEIPASS, "cache", "weapons", f"{clean_key}.png")
        if os.path.exists(bundle_wpn):
            raw_path = bundle_wpn
    w_box, h_box = target_size
    canvas = Image.new("RGBA", (w_box, h_box), (18, 22, 29, 255))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, w_box - 1, h_box - 1], outline=(43, 50, 61, 255), width=1)

    if os.path.exists(raw_path):
        try:
            src = Image.open(raw_path).convert("RGBA")
            pad = 6
            src.thumbnail((max(16, w_box - pad * 2), max(16, h_box - pad * 2)), Image.Resampling.LANCZOS)
            sw, sh = src.size
            ox = (w_box - sw) // 2
            oy = (h_box - sh) // 2
            canvas.alpha_composite(src, (ox, oy))
            canvas.save(thumb_path, "PNG")
            return canvas
        except Exception as e:
            logger.warning("Error procesando imagen de arma/pieza %s: %s", clean_key, e)

    # Fallback táctico profesional con categoría de accesorio y acento visual de alto contraste
    category_styles = [
        (("supp", "choke", "dtk", "brake", "silencer", "rotor", "pbs", "ultra", "hybrid", "annihilator", "saker", "slx"), "SILENCIADOR", "#38BDF8"),
        (("vudu", "pso", "schmidt", "atacr", "march", "hamr", "razor", "exps", "holosun", "sight", "scope", "optic", "t1"), "ÓPTICA / MIRA", "#A855F7"),
        (("grip", "vfg", "afg", "se5", "rk", "uvg", "skeleton", "kag"), "EMPUÑADURA", "#10B981"),
        (("stock", "sass", "archangel", "pt3", "ubr", "buttpad", "moe_stock", "ctr", "slk"), "CULATA / CHASIS", "#F59E0B"),
        (("mag", "drum", "60", "pmag", "stick", "box"), "CARGADOR", "#EC4899"),
        (("laser", "klesch", "ncstar", "xc1", "peq", "light", "lam"), "TÁCTICO / LÁSER", "#EF4444"),
        (("rail", "forestock", "barrel", "b30", "b11", "b10", "urx", "sai", "cmmg", "mpx", "sag", "slide"), "GUARDAMANOS / RIEL", "#64748B"),
        (("warn", "importante", "gs_"), "AVISO CLAVE", "#E86C25"),
    ]

    badge_text = "ACCESORIO"
    accent_color = "#D4B886"

    key_lower = clean_key.lower()
    lbl_lower = (label_fallback or "").lower()

    for triggers, title, color in category_styles:
        if any(tr in key_lower or tr in lbl_lower for tr in triggers):
            badge_text = title
            accent_color = color
            break

    # Fondo oscuro pulido con barra indicadora de categoría
    draw.rounded_rectangle([2, 2, w_box - 3, h_box - 3], radius=4, fill=(16, 20, 28, 255), outline=(45, 53, 69, 255), width=1)
    draw.rounded_rectangle([3, 3, 7, h_box - 4], radius=2, fill=accent_color)

    font_b = _get_font(max(9, min(12, int(h_box * 0.28))), bold=True)
    tb = draw.textbbox((0, 0), badge_text, font=font_b)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    draw.text(((w_box - tw) // 2 + 3, (h_box - th) // 2), badge_text, fill=(248, 250, 252, 255), font=font_b)

    canvas.save(thumb_path, "PNG")
    return canvas
