"""
TarkovScope - Internacionalización (i18n) ES / EN
Gestiona el idioma activo de la interfaz ('es' Español / 'en' English),
persistido en SQLite (user_preferences) sin dependencias de UI.
"""
from typing import Dict

from core.user_data import get_user_preference, set_user_preference

SUPPORTED_LANGS: Dict[str, str] = {
    "es": "Español",
    "en": "English",
}

_VALID_LANGS = set(SUPPORTED_LANGS.keys())
_ACTIVE_LANG: str = get_user_preference("ui_lang", "es")
if _ACTIVE_LANG not in _VALID_LANGS:
    _ACTIVE_LANG = "es"


def get_active_lang() -> str:
    """Retorna el código de idioma activo ('es' o 'en')."""
    return _ACTIVE_LANG


def set_active_lang(lang_id: str) -> str:
    """Valida, persiste y activa el idioma de la UI ('es' o 'en')."""
    global _ACTIVE_LANG
    clean = (lang_id or "es").strip().lower()
    if clean not in _VALID_LANGS:
        clean = "es"
    _ACTIVE_LANG = clean
    set_user_preference("ui_lang", clean)
    return clean


def t_ui(es_text: str, en_text: str) -> str:
    """Helper bilingüe rápido: devuelve en_text en inglés o es_text en español."""
    return en_text if _ACTIVE_LANG == "en" else es_text


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "es": {
        "sidebar.search": "🔍 Buscar... (Ctrl+K)",
        "sidebar.topmost_on": "📌 Fijar Arriba: ACTIVO",
        "sidebar.topmost_off": "📌 Fijar Arriba: Desactivado",
        "sidebar.skin": "🎨 Skin:",
        "sidebar.lang": "🌐 Idioma:",
        "sidebar.db_ready": "● Caché RAM Zero-Lag activo",
        "sidebar.db_syncing": "● Descargando datos...",
        "sidebar.db_done": "● Datos sincronizados",
        "sidebar.db_offline": "● Modo Offline (Caché Local)",
        "sidebar.export": "📤 Exportar",
        "sidebar.import": "📥 Importar",
        "sidebar.sync": "Sincronizar Datos",
        "sidebar.syncing": "Sincronizando...",
        "sidebar.patch_notes": "📋 Notas de Versión",
        "sidebar.update": "🔄 Buscar Actualización (v{ver})",
        "nav.bosses": "Bosses & Spawns",
        "nav.maps": "Mapas & Extracciones",
        "nav.quests": "Quests & Traders",
        "nav.quest_tracker": "Quest Tracker & Rutas",
        "nav.progression_planner": "Planner de Progresión",
        "nav.story_quests": "Quests de la Historia",
        "nav.weapons": "Armas & Gunsmith",
        "nav.ballistics": "Balística & Blindaje",
        "nav.containers": "Rigs, Mochilas & Cajas",
        "nav.flea": "Hideout, Barters & FiR",
        "nav.keys": "Llaves & Intel",
        "nav.medical": "Medicina & Stims",
        "nav.pmc_systems": "PMC, Skills & Sistemas",
        "nav.lore": "Story & Lore",
        "search.title": "BÚSQUEDA GLOBAL TÁCTICA (CTRL + K)",
        "search.placeholder": "Buscar quests, bosses, mapas, munición, blindaje, llaves, stims, barters o skills...",
        "search.empty_hint": "Escribe al menos 2 letras para buscar instantáneamente en todo TarkovScope...",
        "search.min_chars": "Escribe al menos 2 letras para buscar...",
        "search.no_results": "No se encontraron resultados coincidentes.",
        "search.tip": "Tip: Puedes presionar Ctrl + K desde cualquier ventana de la app para abrir este buscador.",
        "search.matches": "{n} coincidencias",
        "search.go": "Ir ➔",
    },
    "en": {
        "sidebar.search": "🔍 Search... (Ctrl+K)",
        "sidebar.topmost_on": "📌 Always on Top: ON",
        "sidebar.topmost_off": "📌 Always on Top: Off",
        "sidebar.skin": "🎨 Skin:",
        "sidebar.lang": "🌐 Lang:",
        "sidebar.db_ready": "● Zero-Lag RAM Cache active",
        "sidebar.db_syncing": "● Downloading data...",
        "sidebar.db_done": "● Data synchronized",
        "sidebar.db_offline": "● Offline Mode (Local Cache)",
        "sidebar.export": "📤 Export",
        "sidebar.import": "📥 Import",
        "sidebar.sync": "Sync Data",
        "sidebar.syncing": "Syncing...",
        "sidebar.patch_notes": "📋 Patch Notes",
        "sidebar.update": "🔄 Check Updates (v{ver})",
        "nav.bosses": "Bosses & Spawns",
        "nav.maps": "Maps & Extracts",
        "nav.quests": "Quests & Traders",
        "nav.quest_tracker": "Quest Tracker & Routes",
        "nav.progression_planner": "Progression Planner",
        "nav.story_quests": "Story Quests",
        "nav.weapons": "Weapons & Gunsmith",
        "nav.ballistics": "Ballistics & Armor",
        "nav.containers": "Rigs, Backpacks & Cases",
        "nav.flea": "Hideout, Barters & FiR",
        "nav.keys": "Keys & Intel",
        "nav.medical": "Medical & Stims",
        "nav.pmc_systems": "PMC, Skills & Systems",
        "nav.lore": "Story & Lore",
        "search.title": "TACTICAL GLOBAL SEARCH (CTRL + K)",
        "search.placeholder": "Search quests, bosses, maps, ammo, armor, keys, stims, barters or skills...",
        "search.empty_hint": "Type at least 2 characters to search instantaneously across TarkovScope...",
        "search.min_chars": "Type at least 2 characters to search...",
        "search.no_results": "No matching results found.",
        "search.tip": "Tip: Press Ctrl + K anywhere in the app to open global search.",
        "search.matches": "{n} matches",
        "search.go": "Go ➔",
    },
}


def tr(key: str, default: str = "", **kwargs) -> str:
    """Devuelve el texto traducido para el idioma activo."""
    lang_map = TRANSLATIONS.get(_ACTIVE_LANG, TRANSLATIONS["es"])
    text = lang_map.get(key) or TRANSLATIONS["es"].get(key) or default or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
