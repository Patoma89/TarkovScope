"""
TarkovScope - Historial de Notas de Versión (Patch Notes) Bilingüe (ES / EN)
Módulo de datos puro (sin dependencias de UI) para mostrar qué cambia en cada versión.
"""
from typing import Any, Dict, List

PATCH_NOTES: List[Dict[str, Any]] = [
    {
        "version": "2.0.0",
        "tag": "Major Release",
        "title_es": "Interfaz Next-Gen GPU (Edge WebView2), Kord Breach, 1.602 Attachments, 235 Logros & Mapas Calibrados",
        "title_en": "Next-Gen GPU UI (Edge WebView2), Kord Breach, 1,602 Attachments, 235 Achievements & Calibrated Maps",
        "items": [
            {
                "kind": "NEW",
                "es": "Nueva interfaz gráfica Next-Gen acelerada por GPU (Edge WebView2 + Glassmorphism) con 60 FPS fluidos, selector único de 6 skins instantáneas en 1 ms, nivel de PMC editable (1–79), cambio de idioma ES/EN en vivo y Visor Lightbox con Zoom/Pan.",
                "en": "Brand-new GPU-accelerated Next-Gen UI (Edge WebView2 + Glassmorphism) at smooth 60 FPS, single-click 6 skins in 1 ms, editable PMC level (1–79), live ES/EN language switch and Zoom/Pan Image Lightbox.",
            },
            {
                "kind": "NEW",
                "es": "Nueva pestaña Kord Breach (Season 1) con mapa interactivo embebido de kordmap.wiki, caché persistente en disco y cambio instantáneo en 0 ms sin recargar.",
                "en": "New Kord Breach (Season 1) tab with embedded interactive kordmap.wiki maps, persistent disk cache and 0 ms tab switching without reloads.",
            },
            {
                "kind": "NEW",
                "es": "Centro de Mando ampliado con 8 paneles interactivos 100% clickeables (Quests, Collector Kappa, Hideout, Logros, Radar de Bosses, Refugio Disponible, Llaves de Quest, Historia & Gunsmith).",
                "en": "Expanded Command Center with 8 fully clickable live panels (Quests, Kappa Collector, Hideout, Achievements, Boss Radar, Ready Hideout Upgrades, Quest Keys, Story & Gunsmith).",
            },
            {
                "kind": "IMPROVED",
                "es": "Modding Studio Pro expandido con 1.602 attachments oficiales de la Wiki, buscador rápido de piezas y las 110 miniaturas reales de armas.",
                "en": "Modding Studio Pro expanded to 1,602 official Wiki attachments, quick part search and all 110 real weapon thumbnails.",
            },
            {
                "kind": "IMPROVED",
                "es": "Mapas 2D calibrados con capas oficiales de tarkov.dev (Extracciones PMC/Scav, Puertas con Llave, Spawns de Bosses auditados visualmente contra la Wiki y Pines personales), Balística 0–6 alineada a eft-ammo.com, 235 Logros oficiales, Ítems FiR modernizados y Lore independiente.",
                "en": "Calibrated 2D Maps with official tarkov.dev layers (PMC/Scav extracts, Locked Doors, Wiki-verified Boss spawns & personal pins), eft-ammo.com 0–6 Ballistics matrix, 235 official Achievements, redesigned FiR checklist and standalone Lore section.",
            },
        ],
    },
    {
        "version": "1.5.1",
        "tag": "Release",
        "title_es": "Pre-calentamiento RAM de Miniaturas, Cambio de Pestañas 0 ms & Thumbs Empaquetados",
        "title_en": "RAM Thumbnail Pre-Warm, 0 ms Tab Switching & Bundled Pre-Scaled Thumbs",
        "items": [
            {
                "kind": "IMPROVED",
                "es": "450 miniaturas pre-escaladas incluidas en cache/thumbs/ dentro del repositorio e instalador para carga en 0 ms tras instalar o actualizar.",
                "en": "450 pre-scaled thumbnails bundled in cache/thumbs/ across the repository and installer for 0 ms loading right after installing or updating.",
            },
            {
                "kind": "IMPROVED",
                "es": "Pre-calentamiento asíncrono en RAM (prewarm_ui_thumbnails) al iniciar la app para más de 1.600 íconos (Armas, Llaves, Medicina, Provisiones, Contenedores, Blindajes, Barters, Hideout, Skills y Traders).",
                "en": "Asynchronous background RAM pre-warming (prewarm_ui_thumbnails) at startup for 1,600+ icons (Weapons, Keys, Medical, Provisions, Containers, Armor, Barters, Hideout, Skills & Traders).",
            },
            {
                "kind": "IMPROVED",
                "es": "Caché en memoria RAM para preferencias de usuario y estado de KPIs del Top HUD, eliminando lecturas SQLite al cambiar entre pestañas.",
                "en": "In-memory RAM caching for user preferences and Top HUD KPI state, eliminating SQLite reads on every tab switch.",
            },
        ],
    },
    {
        "version": "1.5.0",
        "tag": "Release",
        "title_es": "Centro de Mando, HUD Táctico, Prestigio 1-6, 45 Provisiones, Facciones IA & UI Moderna",
        "title_en": "Command Center, Tactical HUD, Prestige 1-6, 45 Provisions, AI Factions & Modern UI",
        "items": [
            {
                "kind": "NEW",
                "es": "Centro de Mando (Bento Grid) + Top HUD Bar global con KPIs en vivo y Reloj Dual In-Raid de Tarkov (ciclo 7x) con alerta nocturna de Cultists (22:00-07:00).",
                "en": "Command Center (Bento Grid) + global Top HUD Bar with live KPIs and official Dual In-Raid Tarkov Clock (7x cycle) with Cultists night window alert (22:00-07:00).",
            },
            {
                "kind": "NEW",
                "es": "Sidebar agrupado con indicador activo iluminado (Active Pill), modo colapsable, tipografía híbrida Bender/Segoe UI y 2 skins nuevas: Modern Obsidian y TerraGroup Clean.",
                "en": "Grouped collapsible sidebar with glowing Active Pill, hybrid Bender/Segoe UI typography and 2 new skins: Modern Obsidian and TerraGroup Clean.",
            },
            {
                "kind": "NEW",
                "es": "Prestige 1 a 6 oficial de Wiki (PvE/PvP) con iconos, guía Arena/Ref, 32 Achievements con checklist persistente y catálogo visual de 24 prendas tácticas USEC/BEAR.",
                "en": "Official Wiki Prestige 1-6 (PvE/PvP) with icons, Arena/Ref sync guide, 32 trackable Achievements and visual catalog of 24 USEC/BEAR tactical clothing items.",
            },
            {
                "kind": "NEW",
                "es": "Catálogo completo de 45 Provisiones (comida y bebida) con miniaturas PNG, matriz de 14 efectos de salud/debuffs, 6 Facciones IA activas y guía de Averías de Armas (Malfunctions & regla del 93%).",
                "en": "Complete catalog of 45 official Provisions (food & drink) with PNG thumbnails, 14 Health effects matrix, 6 active AI Factions and Weapon Malfunctions / 93% durability guide.",
            },
            {
                "kind": "IMPROVED",
                "es": "Balística sincronizada al 100% con eft-ammo.com (203 proyectiles, SNB Tier 6, M80A1, Ball 11, Tungsten Carbide AP), los 44 ítems vigentes de Collector (Kappa) y miniaturas en Hideout & Barters.",
                "en": "Ballistics synced 100% with eft-ammo.com (203 rounds, SNB Tier 6, M80A1, Ball 11, Tungsten Carbide AP), all 44 active Collector (Kappa) items and Hideout/Barters thumbnails.",
            },
        ],
    },
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
