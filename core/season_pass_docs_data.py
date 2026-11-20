"""
TarkovScope - Datos Puros de Docs del Pase de Temporada (Season 1: Kord Breach)
Catálogo de los 8 tipos oficiales de documentación TerraGroup + Classified Documents,
límites diarios (Seasonal / PvP / PvE), matriz de mapas y rutas/llaves de farmeo
inspirado en kordmap.wiki y tarkovdocsmap.com.
Módulo 100% puro (sin dependencias de UI).
"""
from typing import Any, Dict, List


SEASON_PASS_META: Dict[str, Any] = {
    "season_name": "Season 1 — Kord Breach",
    "total_required_docs": 501,
    "exchange_rule_es": "Podés intercambiar cualquier combinación de 5 documentos por 1 documento a elección, o usar Classified Documents como comodín.",
    "exchange_rule_en": "You can trade any 5 documents for 1 document of your choice, or use Classified Documents as a wildcard.",
    "personal_loot_note_es": "Los documentos del Pase son loot personal instanciado: otros jugadores NO pueden robártelos ni lootearlos de tu cuerpo.",
    "personal_loot_note_en": "Battle Pass documents are personal instanced loot: other players cannot snatch them or loot them from your body.",
    "daily_limits": {
        "seasonal": {"label": "Seasonal", "limit": 40, "color": "#10b981"},
        "pvp": {"label": "PvP", "limit": 25, "color": "#38bdf8"},
        "pve": {"label": "PvE", "limit": 15, "color": "#f59e0b"},
    },
    "external_links": [
        {"label": "kordmap.wiki (Mapa Interactivo)", "url": "https://kordmap.wiki/"},
        {"label": "tarkovdocsmap.com (Spawns con Capturas)", "url": "https://tarkovdocsmap.com/"},
    ],
}


SEASON_PASS_DOC_TYPES: List[Dict[str, Any]] = [
    {
        "id": "blueprints_technical",
        "name": "Blueprints & Technical Documentation",
        "name_es": "Planos y Documentación Técnica",
        "color": "#38bdf8",
        "maps": ["Interchange", "Factory", "The Labyrinth"],
        "target_hint": 63,
        "hotspots_es": "Interchange (oficinas de OLI, IDEA, Power Station, salas de servidores) · Factory (Oficina 3F y pasarelas técnicas) · The Labyrinth.",
        "keys_hint": "Emercom Medical, KIBA, Factory Emergency Exit, Power Station",
    },
    {
        "id": "financial_docs",
        "name": "Financial Documents",
        "name_es": "Documentos Financieros",
        "color": "#f59e0b",
        "maps": ["Customs", "Streets of Tarkov", "Interchange"],
        "target_hint": 63,
        "hotspots_es": "Customs (Big Red / Tarcone Director's Office, Dorms 2F/3F cajas fuertes) · Streets (Tarbank, Beluga, Chekannaya, oficinas) · Interchange (cajas y oficinas administrativas).",
        "keys_hint": "Tarcone Director's Office, Dorm 114/105/110, Tarbank, Chekannaya 15",
    },
    {
        "id": "medical_docs",
        "name": "Medical Documents",
        "name_es": "Documentos Médicos",
        "color": "#10b981",
        "maps": ["The Lab", "Ground Zero", "The Labyrinth", "Icebreaker"],
        "target_hint": 63,
        "hotspots_es": "The Lab (Blue/Black Keycard, Quarantine, Medical Block) · Ground Zero (Emercom tent, TerraGroup Science Office) · The Labyrinth · Icebreaker.",
        "keys_hint": "Lab Black/Blue Keycard, TerraGroup Scientist Key",
    },
    {
        "id": "pmc_personnel",
        "name": "PMC Personnel Files",
        "name_es": "Expedientes de Personal PMC",
        "color": "#ef4444",
        "maps": ["Reserve", "Lighthouse", "Icebreaker"],
        "target_hint": 63,
        "hotspots_es": "Reserve (Búnker D-2, Black/White Pawn barracas, King Building) · Lighthouse (Water Treatment Plant edificios 1-3, Chalets) · Icebreaker.",
        "keys_hint": "RB-KPRL, RB-OB, RB-AM, Operating Room, Rogue Usec Stash",
    },
    {
        "id": "user_docs",
        "name": "User Documentation",
        "name_es": "Documentación de Usuario",
        "color": "#a855f7",
        "maps": ["Ground Zero", "Streets of Tarkov", "The Lab"],
        "target_hint": 63,
        "hotspots_es": "Ground Zero (Oficinas Empire, Capital Insight, Nakatani) · Streets (Concordia, Pinewood, LexOs, Post Office) · The Lab (Server Room, Manager's Office).",
        "keys_hint": "TerraGroup Science, Concordia 64/8, Lab Manager's Office",
    },
    {
        "id": "test_docs",
        "name": "Test Documentation",
        "name_es": "Documentación de Pruebas",
        "color": "#ec4899",
        "maps": ["Shoreline", "Woods", "Icebreaker"],
        "target_hint": 62,
        "hotspots_es": "Shoreline (Health Resort Admin, East/West Wings, Weather Station) · Woods (USEC Camp, Sawmill cabañas, Bunker) · Icebreaker.",
        "keys_hint": "West 301/216, East 226/306, Admin Office, Shturman Stash",
    },
    {
        "id": "technical_docs",
        "name": "Technical Documentation",
        "name_es": "Documentación Técnica",
        "color": "#06b6d4",
        "maps": ["Shoreline", "Woods", "Lighthouse"],
        "target_hint": 62,
        "hotspots_es": "Shoreline (Pier, Weather Station, Power Station, Resort) · Woods (Sawmill, Emercom Medical Camp, Old Sawmill) · Lighthouse (Water Treatment, Radar).",
        "keys_hint": "Cottage Back Door, Radar Station, Water Treatment Offices",
    },
    {
        "id": "project_docs",
        "name": "Project Documentation",
        "name_es": "Documentación de Proyecto",
        "color": "#d4b886",
        "maps": ["Factory", "Reserve", "Customs"],
        "target_hint": 62,
        "hotspots_es": "Factory (Oficina 3F, salas técnicas, subterráneo) · Reserve (Dome / Queen, White/Black Bishop, Command Bunker) · Customs (Stronghold, Dorms, Warehouse 4).",
        "keys_hint": "Factory Exit, RB-ST, RB-KSM, Dorm 206/303/314",
    },
    {
        "id": "classified_docs",
        "name": "Classified Documents (Wildcard)",
        "name_es": "Documentos Clasificados (Comodín)",
        "color": "#fbbf24",
        "maps": ["Expansion Hub / Intercambio 5→1"],
        "target_hint": 0,
        "hotspots_es": "Sustituyen cualquier tipo de documento requerido en el Pase. Se obtienen en el Expansion Hub o intercambiando 5 documentos sobrantes por 1 a elección.",
        "keys_hint": "Sin llave — Comodín universal del Pase",
    },
]


SEASON_PASS_MAP_SUMMARY: List[Dict[str, Any]] = [
    {"map": "Customs", "doc_ids": ["financial_docs", "project_docs"], "route_tip_es": "Ruta rápida: Big Red (Tarcone) → Dorms (cajas fuertes y escritorios) → Stronghold → Extract ZB-1011 / Smuggler's."},
    {"map": "Interchange", "doc_ids": ["blueprints_technical", "financial_docs"], "route_tip_es": "Ruta rápida: Power Station → Oficinas de IDEA → Oficinas administrativas centrales → Oficinas de OLI → Emercom/Railway."},
    {"map": "Factory", "doc_ids": ["blueprints_technical", "project_docs"], "route_tip_es": "Ruta ultra rápida (5 min): Oficina 3F (cajones, escritorio y estantes) → pasarelas técnicas → Gate 3."},
    {"map": "Streets of Tarkov", "doc_ids": ["financial_docs", "user_docs"], "route_tip_es": "Alta densidad: Tarbank → Post Office → Concordia → Beluga → Chekannaya."},
    {"map": "Ground Zero", "doc_ids": ["medical_docs", "user_docs"], "route_tip_es": "Excelente para farmear seguro: Nakatani → Capital Insight → TerraGroup Building (oficina científica) → Emercom."},
    {"map": "Shoreline", "doc_ids": ["test_docs", "technical_docs"], "route_tip_es": "Weather Station → Health Resort (Admin + East/West Wings) → Power Station → Path to Lighthouse."},
    {"map": "Woods", "doc_ids": ["test_docs", "technical_docs"], "route_tip_es": "USEC Camp → Bunker → Sawmill (cabañas 1-3 y galpón gris) → Emercom Camp → Outskirts."},
    {"map": "Reserve", "doc_ids": ["pmc_personnel", "project_docs"], "route_tip_es": "Dome (Queen) → Black/White Bishop → Command Bunker D-2 → Pawn buildings."},
    {"map": "Lighthouse", "doc_ids": ["pmc_personnel", "technical_docs"], "route_tip_es": "Chalets (Superior e Inferior) → Water Treatment Plant (Edificios 1, 2 y 3) → Northern Checkpoint."},
    {"map": "The Lab", "doc_ids": ["medical_docs", "user_docs"], "route_tip_es": "Manager's Office → Server Room → Black/Blue Keycard rooms → Medical Block."},
    {"map": "The Labyrinth", "doc_ids": ["blueprints_technical", "medical_docs"], "route_tip_es": "Salas de observación y puestos médicos centrales del Laberinto."},
    {"map": "Icebreaker", "doc_ids": ["medical_docs", "pmc_personnel", "test_docs"], "route_tip_es": "3 tipos en un mismo mapa: Enfermería, puente de mando y laboratorios de pruebas."},
]
