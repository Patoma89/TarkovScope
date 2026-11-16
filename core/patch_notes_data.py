"""
TarkovScope - Historial de Notas de Versión (Patch Notes) Bilingüe (ES / EN)
Módulo de datos puro (sin dependencias de UI) para mostrar qué cambia en cada versión.
"""
from typing import Any, Dict, List

PATCH_NOTES: List[Dict[str, Any]] = [
    {
        "version": "1.4.0",
        "tag": "Release",
        "title_es": "Quest Tracker, Planner, Idioma ES/EN, Modding Studio Pro & Skills",
        "title_en": "Quest Tracker, Planner, ES/EN Language, Modding Studio Pro & Skills",
        "items": [
            {
                "kind": "NEW",
                "es": "Quest Tracker & Rutas Óptimas por mapa: marcá tus quests activas y calculá el orden más corto desde tu spawn hasta la extracción.",
                "en": "Quest Tracker & Optimal Map Routes: check active quests and compute the shortest route from your spawn to extraction.",
            },
            {
                "kind": "NEW",
                "es": "Planner de Progresión: elegí metas (Kappa, Lightkeeper, niveles de Traders o quests puntuales) y armá un plan unificado de raids.",
                "en": "Progression Planner: pick goals (Kappa, Lightkeeper, Trader levels or specific quests) and generate a unified raid plan.",
            },
            {
                "kind": "NEW",
                "es": "Selector Global de Idioma (Español / English) en la barra lateral con reconstrucción instantánea de la interfaz.",
                "en": "Global Language Switcher (Español / English) in the sidebar with instant UI rebuild.",
            },
            {
                "kind": "NEW",
                "es": "Visor clásico de Patch Notes y badges 'NEW' inteligentes que desaparecen automáticamente al visitar cada novedad.",
                "en": "Classic Patch Notes viewer and smart 'NEW' badges that automatically dismiss once you visit each new feature.",
            },
            {
                "kind": "IMPROVED",
                "es": "Modding Studio PRO: 110/110 imágenes reales de armas, compatibilidad estricta por plataforma, comparación Δ de stats y auto-optimizadores.",
                "en": "Modding Studio PRO: 110/110 real weapon PNGs, strict platform compatibility, Δ stat comparison and auto-optimizers.",
            },
            {
                "kind": "IMPROVED",
                "es": "Pestaña Skills renovada: las 35 skills activas de EFT Wiki con iconos oficiales en grilla y dossier completo Elite Nv. 51.",
                "en": "Revamped Skills tab: all 35 active EFT Wiki skills with official icon grid and full Elite Lv. 51 dossier.",
            },
            {
                "kind": "FIX",
                "es": "Corregido el sistema de Skins en Story & Lore y Quests de la Historia (tarkov_classic, labs_nvg y tactical_slate).",
                "en": "Fixed Skin theming in Story & Lore and Story Quests (tarkov_classic, labs_nvg and tactical_slate).",
            },
        ],
    },
    {
        "version": "1.3.1",
        "tag": "Release",
        "title_es": "Mapas Completos, Bosses PvE & Estabilidad de Instalador",
        "title_en": "Complete Maps, PvE Bosses & Installer Stability",
        "items": [
            {
                "kind": "IMPROVED",
                "es": "Bundling completo de mapas y avatares offline, retratos de Bosses sobre mapas y probabilidades PvE actualizadas.",
                "en": "Full offline bundling of maps and avatars, Boss portraits on maps and updated PvE spawn chances.",
            },
            {
                "kind": "FIX",
                "es": "Aislamiento automático de DB/caché escribible en LocalAppData cuando TTC se instala en Program Files.",
                "en": "Automatic writable DB/cache isolation in LocalAppData when TTC is installed under Program Files.",
            },
            {
                "kind": "FIX",
                "es": "Saneado de variables de entorno PyInstaller al lanzar auto-actualizaciones y mejoras en el instalador de Windows.",
                "en": "Sanitized PyInstaller environment variables during self-update and Windows installer destination guards.",
            },
        ],
    },
    {
        "version": "1.3.0",
        "tag": "Release",
        "title_es": "Blindaje, Contenedores, Barters, PMC Systems & Ctrl+K",
        "title_en": "Armor, Containers, Barters, PMC Systems & Ctrl+K",
        "items": [
            {
                "kind": "NEW",
                "es": "Búsqueda Global Táctica (Ctrl+K) en tiempo real sobre quests, bosses, mapas, munición, llaves, stims y barters.",
                "en": "Global Tactical Search (Ctrl+K) across quests, bosses, maps, ammo, keys, stims and barters.",
            },
            {
                "kind": "NEW",
                "es": "Pestañas dedicadas de Blindaje/Placas (simulación dual Plate + Aramid), Rigs/Mochilas/Cajas, Barters/Cultist Circle y PMC/Karma/BTR/Transits.",
                "en": "Dedicated tabs for Armor/Plates (dual Plate + Aramid simulation), Rigs/Backpacks/Cases, Barters/Cultist Circle and PMC/Karma/BTR/Transits.",
            },
        ],
    },
    {
        "version": "1.2.0",
        "tag": "Release",
        "title_es": "Llaves & Intel, Medicina & Stims, Story & Lore",
        "title_en": "Keys & Intel, Medical & Stims, Story & Lore",
        "items": [
            {
                "kind": "NEW",
                "es": "Catálogo táctico de 230+ Llaves, Keycards y Marked Rooms con checklist personal de llavero.",
                "en": "Tactical catalog of 230+ Keys, Keycards and Marked Rooms with personal keyring checklist.",
            },
            {
                "kind": "NEW",
                "es": "Guía de Medicina, Botiquines & Estimulantes (Stims) con filtro por lesión/síntoma.",
                "en": "Medical, Medkits & Stims guide with symptom/injury filtering.",
            },
            {
                "kind": "NEW",
                "es": "Archivo completo de Historia & Lore (10 capítulos y 72 misiones principales).",
                "en": "Complete Story & Lore archive (10 chapters and 72 main story missions).",
            },
        ],
    },
    {
        "version": "1.1.0",
        "tag": "Release",
        "title_es": "Caché Zero-Lag, Respaldo de Perfil & Skins Tácticas",
        "title_en": "Zero-Lag Cache, Profile Backup & Tactical Skins",
        "items": [
            {
                "kind": "NEW",
                "es": "DataStore en memoria RAM (<1 ms), Exportar/Importar progreso en JSON y selector de Skins tácticas.",
                "en": "In-memory RAM DataStore (<1 ms), JSON profile Export/Import and Tactical Skins switcher.",
            },
            {
                "kind": "IMPROVED",
                "es": "Modo Always-on-Top para usar TTC como compañero rápido sobre el juego.",
                "en": "Always-on-Top window mode for quick companion usage over the game.",
            },
        ],
    },
    {
        "version": "1.0.0",
        "tag": "Release",
        "title_es": "Lanzamiento Inicial de TarkovScope (TTC)",
        "title_en": "Initial Release of TarkovScope (TTC)",
        "items": [
            {
                "kind": "NEW",
                "es": "Bosses & Spawns, Mapas Interactivos con extracciones/POIs, Quests & Traders, Balística & Matriz de Penetración, Arsenal & Gunsmith y Hideout FiR.",
                "en": "Bosses & Spawns, Interactive Maps with extracts/POIs, Quests & Traders, Ballistics & Penetration Matrix, Arsenal & Gunsmith and Hideout FiR.",
            },
        ],
    },
]


def get_patch_notes(lang: str = "es") -> List[Dict[str, Any]]:
    """Devuelve el historial de patch notes adaptado al idioma ('es' o 'en')."""
    is_en = (lang or "es").strip().lower() == "en"
    out: List[Dict[str, Any]] = []
    for rel in PATCH_NOTES:
        out.append(
            {
                "version": rel["version"],
                "tag": rel["tag"],
                "title": rel["title_en"] if is_en else rel["title_es"],
                "items": [
                    {
                        "kind": item["kind"],
                        "text": item["en"] if is_en else item["es"],
                    }
                    for item in rel["items"]
                ],
            }
        )
    return out
