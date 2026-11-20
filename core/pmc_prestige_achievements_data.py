"""
TarkovScope - Datos Puros de Prestige, Arena/Ref Sync, Achievements y Ropa Táctica (EFT Wiki)
Cero dependencias de UI / Tkinter.
"""
import json
import os
from typing import Any, Dict, List, Optional, Set

from core.config import BASE_DIR, BUNDLE_DIR


PRESTIGE_LEVELS_DATA: List[Dict[str, Any]] = [
    {
        "level": 1,
        "code": "PRESTIGE I",
        "icon_key": "prestige_1",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/7d/Prestige_1_icon.png/revision/latest?cb=20261008215226",
        "title_es": "Prestige 1 — Primer Reinicio",
        "title_en": "Prestige 1 — First Reset",
        "summary_es": (
            "Primer escalón de Prestige. En PvE pide requisitos reducidos; en PvP exige "
            "New Beginning (Prestige 1) y 3 módulos iniciales de Hideout."
        ),
        "summary_en": (
            "First Prestige rank. PvE has lighter requirements; PvP requires New Beginning (Prestige 1) "
            "and 3 Hideout stations."
        ),
        "requirements_es": [
            "Nivel de PMC: PvE 15  |  PvP 25",
            "Quests: PvE Ninguna  |  PvP 'New Beginning (Prestige 1)'",
            "Historia (Story Chapters): Ninguno",
            "Skills: Ninguna",
            "Hideout: PvE Ninguno  |  PvP Intelligence Center Nv. 1, Nutrition Unit Nv. 2, Rest Space Nv. 2",
            "Dinero: PvE 5.000.000 ₽  |  PvP 10.000.000 ₽",
        ],
        "requirements_en": [
            "PMC Level: PvE 15  |  PvP 25",
            "Quests: PvE None  |  PvP 'New Beginning (Prestige 1)'",
            "Story Chapters: None",
            "Skills: None",
            "Hideout: PvE None  |  PvP Intelligence Center Lv.1, Nutrition Unit Lv.2, Rest Space Lv.2",
            "Money: PvE 5,000,000 RUB  |  PvP 10,000,000 RUB",
        ],
        "rewards_es": [
            "Retención permanente: 5% Skills/Maestrías (PvP)  |  10% + 50× TarCoin (PvE)",
            "Grilla de transferencia de ítems: 8x3 celdas + +1 Charisma permanente",
            "Dogtag Prestige 1, Brazalete Prestige 1 y logro 'Prestigious'",
            "Póster + Suelo Luxury Flooring + Gestos Piedra/Papel/Tijera + Pose 'Feel My Gains'",
        ],
        "rewards_en": [
            "Permanent retention: 5% Skills/Mastery (PvP)  |  10% + 50× TarCoin (PvE)",
            "Item transfer window: 8x3 grid + +1 Charisma skill level",
            "Prestige 1 Dogtag, Armband & 'Prestigious' achievement",
            "Poster + Luxury flooring + Rock/Paper/Scissors gestures + 'Feel My Gains' pose",
        ],
    },
    {
        "level": 2,
        "code": "PRESTIGE II",
        "icon_key": "prestige_2",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a0/Prestige_2_icon.png/revision/latest?cb=20261008215232",
        "title_es": "Prestige 2 — Segundo Escalón",
        "title_en": "Prestige 2 — Second Tier",
        "summary_es": (
            "Exige completar el capítulo de historia 'Tour', subir Strength/Endurance Nv.10 y Charisma Nv.7, "
            "y otorga +1 misión diaria/semanal permanente."
        ),
        "summary_en": (
            "Requires completing the 'Tour' story chapter, Strength/Endurance Lv.10 & Charisma Lv.7, "
            "and grants permanent +1 daily and +1 weekly operational task."
        ),
        "requirements_es": [
            "Nivel de PMC: PvE 25  |  PvP 30",
            "Quests: 'New Beginning (Prestige 2)'",
            "Historia: Completar el capítulo 'Tour'",
            "Skills: Strength Nv. 10, Endurance Nv. 10, Charisma Nv. 7",
            "Hideout: Intelligence Center Nv. 1, Nutrition Unit Nv. 2, Rest Space Nv. 2",
            "Dinero: PvE 10.000.000 ₽  |  PvP 15.000.000 ₽",
        ],
        "requirements_en": [
            "PMC Level: PvE 25  |  PvP 30",
            "Quests: 'New Beginning (Prestige 2)'",
            "Story Chapters: Complete 'Tour'",
            "Skills: Strength Lv.10, Endurance Lv.10, Charisma Lv.7",
            "Hideout: Intelligence Center Lv.1, Nutrition Unit Lv.2, Rest Space Lv.2",
            "Money: PvE 10,000,000 RUB  |  PvP 15,000,000 RUB",
        ],
        "rewards_es": [
            "Retención permanente: 10% Skills/Maestrías (PvP)  |  20% + 50× TarCoin (PvE)",
            "Grilla de transferencia: 8x4 celdas + +1 Charisma + +1 Daily & +1 Weekly task",
            "Daga Akula (PvP) / Kasatka (PvE) + Fondo de menú 'CyberTark'",
            "Dogtag/Brazalete Prestige 2, logro 'More Prestigious', gesto 'Ok' y pose 'Slav Squat'",
        ],
        "rewards_en": [
            "Permanent retention: 10% Skills/Mastery (PvP)  |  20% + 50× TarCoin (PvE)",
            "Item transfer grid: 8x4 + +1 Charisma + +1 Daily & +1 Weekly task",
            "Akula (PvP) / Kasatka (PvE) push dagger + 'CyberTark' main menu background",
            "Prestige 2 Dogtag/Armband, 'More Prestigious' achievement, 'Ok' gesture & 'Slav Squat' pose",
        ],
    },
    {
        "level": 3,
        "code": "PRESTIGE III",
        "icon_key": "prestige_3",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/4b/Prestige_3_icon.png/revision/latest?cb=20261008215239",
        "title_es": "Prestige 3 — Voces & Figurín",
        "title_en": "Prestige 3 — Voices & Figurine",
        "summary_es": (
            "Unifica requisitos en PvE y PvP a nivel 35, agregando el capítulo 'Falling Skies' "
            "y desbloqueando las voces exclusivas Vitaly (BEAR) y Rob (USEC)."
        ),
        "summary_en": (
            "Unifies PvE & PvP requirements at Level 35, adding the 'Falling Skies' story chapter "
            "and unlocking exclusive character voices Vitaly (BEAR) & Rob (USEC)."
        ),
        "requirements_es": [
            "Nivel de PMC: 35 (PvE y PvP)",
            "Quests: 'New Beginning (Prestige 3)'",
            "Historia: Completar 'Tour' y 'Falling Skies'",
            "Skills: Strength Nv. 10, Endurance Nv. 10, Charisma Nv. 7",
            "Hideout: Intelligence Center Nv. 1, Nutrition Unit Nv. 2, Rest Space Nv. 2",
            "Dinero: 15.000.000 ₽",
        ],
        "requirements_en": [
            "PMC Level: 35 (PvE & PvP)",
            "Quests: 'New Beginning (Prestige 3)'",
            "Story Chapters: Complete 'Tour' and 'Falling Skies'",
            "Skills: Strength Lv.10, Endurance Lv.10, Charisma Lv.7",
            "Hideout: Intelligence Center Lv.1, Nutrition Unit Lv.2, Rest Space Lv.2",
            "Money: 15,000,000 RUB",
        ],
        "rewards_es": [
            "Retención permanente: 15% Skills/Maestrías (PvP)  |  30% + 100× TarCoin (PvE)",
            "Grilla de transferencia: 8x5 celdas + +1 Charisma permanente",
            "Voz BEAR 'Vitaly' & Voz USEC 'Rob' + Figurín PMC Origins + Pose 'Honor'",
            "Dogtag/Brazalete Prestige 3, logro 'Keeping Up the Pace' y diana de tiro Crow/Mosquito",
        ],
        "rewards_en": [
            "Permanent retention: 15% Skills/Mastery (PvP)  |  30% + 100× TarCoin (PvE)",
            "Item transfer grid: 8x5 + +1 Charisma skill level",
            "BEAR voice 'Vitaly' & USEC voice 'Rob' + PMC Origins figurine + 'Honor' pose",
            "Prestige 3 Dogtag/Armband, 'Keeping Up the Pace' achievement & target style",
        ],
    },
    {
        "level": 4,
        "code": "PRESTIGE IV",
        "icon_key": "prestige_4",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/2e/Prestige_4_icon.png/revision/latest?cb=20261008215245",
        "title_es": "Prestige 4 — El Ticket de Tarkov",
        "title_en": "Prestige 4 — The Ticket from Tarkov",
        "summary_es": (
            "Sube el listón a nivel 40, exige obtener el Ticket from Tarkov (Kruglov's RFID keycard) "
            "y recompensa con las camisas hawaianas exclusivas."
        ),
        "summary_en": (
            "Raises PMC threshold to Level 40, requires obtaining the Ticket from Tarkov (Kruglov's RFID keycard), "
            "and unlocks exclusive Hawaiian shirts."
        ),
        "requirements_es": [
            "Nivel de PMC: 40 (PvE y PvP)",
            "Quests: 'New Beginning (Prestige 4)'",
            "Historia: Completar 'Tour' y obtener 'Ticket from Tarkov' (Kruglov's RFID keycard)",
            "Skills: Strength Nv. 15, Endurance Nv. 15, Charisma Nv. 12",
            "Hideout: Intelligence Center Nv. 1, Nutrition Unit Nv. 2, Rest Space Nv. 2",
            "Dinero: 15.000.000 ₽",
        ],
        "requirements_en": [
            "PMC Level: 40 (PvE & PvP)",
            "Quests: 'New Beginning (Prestige 4)'",
            "Story Chapters: Complete 'Tour' and obtain 'Ticket from Tarkov' (Kruglov's RFID keycard)",
            "Skills: Strength Lv.15, Endurance Lv.15, Charisma Lv.12",
            "Hideout: Intelligence Center Lv.1, Nutrition Unit Lv.2, Rest Space Lv.2",
            "Money: 15,000,000 RUB",
        ],
        "rewards_es": [
            "Retención permanente: 20% Skills/Maestrías (PvP)  |  40% + 100× TarCoin (PvE)",
            "Grilla de transferencia: 8x6 celdas + +1 Charisma permanente",
            "Camisa 'Green Hawaii shirt' (BEAR) y 'Blue Hawaii shirt' (USEC)",
            "Dogtag/Brazalete Prestige 4, logro 'Higher and Higher', pose 'Jomoon' y suelo Gray wood",
        ],
        "rewards_en": [
            "Permanent retention: 20% Skills/Mastery (PvP)  |  40% + 100× TarCoin (PvE)",
            "Item transfer grid: 8x6 + +1 Charisma skill level",
            "'Green Hawaii shirt' (BEAR) and 'Blue Hawaii shirt' (USEC) clothing",
            "Prestige 4 Dogtag/Armband, 'Higher and Higher' achievement, 'Jomoon' pose & Gray wood floor",
        ],
    },
    {
        "level": 5,
        "code": "PRESTIGE V",
        "icon_key": "prestige_5",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/5/55/Prestige_5_icon.png/revision/latest?cb=20261008215249",
        "title_es": "Prestige 5 — Collector & Apariencias",
        "title_en": "Prestige 5 — Collector & Appearances",
        "summary_es": (
            "Requiere completar 'Collector' (Kappa) + 'They Are Already Here', Hideout avanzado "
            "y otorga las apariencias faciales Basilevs / Shawn + cuchillo NKVD Finka."
        ),
        "summary_en": (
            "Requires completing 'Collector' (Kappa) + 'They Are Already Here', upgraded Hideout, "
            "and unlocks Basilevs / Shawn PMC appearances + NKVD Finka knife."
        ),
        "requirements_es": [
            "Nivel de PMC: 47 (PvE y PvP)",
            "Quests: 'New Beginning (Prestige 5)' + 'Collector' (Kappa)",
            "Historia: Completar 'Tour', 'They Are Already Here' y obtener Ticket from Tarkov",
            "Skills: Strength Nv. 20, Endurance Nv. 20, Charisma Nv. 20",
            "Hideout: Intelligence Center Nv. 2, Security Nv. 3, Rest Space Nv. 3",
            "Dinero: 20.000.000 ₽",
        ],
        "requirements_en": [
            "PMC Level: 47 (PvE & PvP)",
            "Quests: 'New Beginning (Prestige 5)' + 'Collector' (Kappa)",
            "Story Chapters: Complete 'Tour', 'They Are Already Here' & obtain Ticket from Tarkov",
            "Skills: Strength Lv.20, Endurance Lv.20, Charisma Lv.20",
            "Hideout: Intelligence Center Lv.2, Security Lv.3, Rest Space Lv.3",
            "Money: 20,000,000 RUB",
        ],
        "rewards_es": [
            "Retención permanente: 25% Skills/Maestrías (PvP)  |  50% + 100× TarCoin (PvE)",
            "Grilla de transferencia: 8x7 celdas + +1 Charisma permanente",
            "Apariencia BEAR 'Basilevs' y USEC 'Shawn' + Cuchillo NKVD Finka",
            "Dogtag/Brazalete Prestige 5, logro 'Five Plus', pose 'T-pose' y paredes White walls",
        ],
        "rewards_en": [
            "Permanent retention: 25% Skills/Mastery (PvP)  |  50% + 100× TarCoin (PvE)",
            "Item transfer grid: 8x7 + +1 Charisma skill level",
            "BEAR appearance 'Basilevs' & USEC 'Shawn' + NKVD Finka knife",
            "Prestige 5 Dogtag/Armband, 'Five Plus' achievement, 'T-pose' & White walls style",
        ],
    },
    {
        "level": 6,
        "code": "PRESTIGE VI",
        "icon_key": "prestige_6",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/ea/Prestige_6_icon.png/revision/latest?cb=20261008215254",
        "title_es": "Prestige 6 — Sin Límites a la Perfección",
        "title_en": "Prestige 6 — No Limit to Perfection",
        "summary_es": (
            "El rango máximo del juego: exige completar todo el capítulo final 'The Ticket' + Collector, "
            "entregando Gamma exclusivo, fondo 'Hotline Tarkov' y grilla 8x8."
        ),
        "summary_en": (
            "Maximum Endgame Prestige: requires completing the full 'The Ticket' story chapter + Collector, "
            "awarding exclusive Gamma reskins, 'Hotline Tarkov' background & 8x8 transfer grid."
        ),
        "requirements_es": [
            "Nivel de PMC: 47 (PvE y PvP)",
            "Quests: 'New Beginning (Prestige 6)' + 'Collector' (Kappa)",
            "Historia: Completar el capítulo 'The Ticket'",
            "Skills: Strength Nv. 20, Endurance Nv. 20, Charisma Nv. 20",
            "Hideout: Intelligence Center Nv. 2, Security Nv. 3, Rest Space Nv. 3",
            "Dinero: 20.000.000 ₽",
        ],
        "requirements_en": [
            "PMC Level: 47 (PvE & PvP)",
            "Quests: 'New Beginning (Prestige 6)' + 'Collector' (Kappa)",
            "Story Chapters: Complete 'The Ticket'",
            "Skills: Strength Lv.20, Endurance Lv.20, Charisma Lv.20",
            "Hideout: Intelligence Center Lv.2, Security Lv.3, Rest Space Lv.3",
            "Money: 20,000,000 RUB",
        ],
        "rewards_es": [
            "Retención permanente: 30% Skills/Maestrías (PvP)  |  50% + 200× TarCoin (PvE)",
            "Grilla de transferencia máxima: 8x8 celdas + +1 Charisma permanente",
            "Secure Container Gamma (Loui Peeton en PvP / Balesaiga en PvE) + Fondo 'Hotline Tarkov'",
            "Dogtag/Brazalete Prestige 6, logro 'No Limit to Perfection', pose 'Praise!' y techo dorado",
        ],
        "rewards_en": [
            "Permanent retention: 30% Skills/Mastery (PvP)  |  50% + 200× TarCoin (PvE)",
            "Maximum transfer grid: 8x8 + +1 Charisma skill level",
            "Secure container Gamma (Loui Peeton PvP / Balesaiga PvE) + 'Hotline Tarkov' menu background",
            "Prestige 6 Dogtag/Armband, 'No Limit to Perfection' achievement, 'Praise!' pose & Gilded ceiling",
        ],
    },
]


PRESTIGE_RESET_MATRIX: Dict[str, List[Dict[str, str]]] = {
    "kept": [
        {"es": "Todos los Achievements (Logros), medallas y recompensas de Prestige", "en": "All Achievements, Badges & unlocked Prestige rewards"},
        {"es": "Estadísticas acumuladas de carrera (Horas, K/D histórico)", "en": "Lifetime career stats (Hours, career history)"},
        {"es": "Progreso de Tarkov: Arena (ARP, presets y Armería)", "en": "Tarkov: Arena progress (ARP, presets & Armory)"},
        {"es": "5% a 30% (PvP) o 10% a 50% (PvE) de Skills y Maestrías según nivel", "en": "5%–30% (PvP) or 10%–50% (PvE) Skills & Weapon Mastery"},
        {"es": "Ítems colocados en la Grilla de Transferencia (8x3 hasta 8x8, sin FiR)", "en": "Items placed in Transfer Grid (8x3 up to 8x8, lose FiR)"},
        {"es": "Ropa comprada de Ragman, expansiones de web y Twitch Drops", "en": "Ragman clothing unlocks, web apparel expansions & Twitch Drops"},
    ],
    "reset": [
        {"es": "Nivel de PMC (vuelve a Nv. 1) y nombre/facción reelegibles", "en": "PMC Level (resets to Lv. 1) & faction re-selection"},
        {"es": "Todas las Misiones (Quests principales, Kappa, Story y Lightkeeper)", "en": "All Quests (Main, Kappa, Story & Lightkeeper chains)"},
        {"es": "Nivel de Lealtad (LL) y Reputación de todos los Traders", "en": "Trader Loyalty Levels (LL) & Standing"},
        {"es": "Todo el Alijo (Stash), dinero (RUB/USD/EUR) y contenedores", "en": "Entire Stash, currencies (RUB/USD/EUR) & cases"},
        {"es": "Todas las zonas y construcciones del Hideout (vuelve a Nv. 0)", "en": "All Hideout stations & upgrades (back to Lv. 0)"},
        {"es": "Scav Karma (Fence vuelve al valor inicial de edición)", "en": "Scav Karma (Fence resets to edition baseline)"},
    ],
}


ARENA_REF_SYNC_GUIDE: List[Dict[str, str]] = [
    {
        "topic_es": "Progresión Compartida EFT ↔ Arena",
        "topic_en": "Shared Progression EFT ↔ Arena",
        "detail_es": (
            "Tu nivel de PMC, XP ganada en partidas, subida de Skills físicas/combate y Maestrías de Armas "
            "se sincronizan automáticamente entre Escape from Tarkov y EFT: Arena."
        ),
        "detail_en": (
            "PMC Level, match XP, physical/combat Skill gains, and Weapon Masteries sync automatically "
            "between Escape from Tarkov and EFT: Arena."
        ),
    },
    {
        "topic_es": "Transferencia de Divisas & Cajas (Ref)",
        "topic_en": "Currency & Case Transfers (Ref)",
        "detail_es": (
            "Desde Arena podés transferir GP Coins, Lega Medals y Rublos (con límite diario) hacia tu alijo "
            "de Tarkov. Ref solo acepta GP Coins y Lega Medals para equipo meta, placas Clase 5/6 y cajas."
        ),
        "detail_en": (
            "From Arena you can transfer GP Coins, Lega Medals, and Roubles (subject to daily cap) to your "
            "Tarkov stash. Ref exclusively trades in GP Coins and Lega Medals for top-tier gear and cases."
        ),
    },
    {
        "topic_es": "Desbloqueo de Ref y Línea 'To Great Heights!'",
        "topic_en": "Unlocking Ref & 'To Great Heights!' Chain",
        "detail_es": (
            "Completa 'Easy Money - Part 1' (Skier) para desbloquear a Ref LL1. Luego avanza 'Balancing' y "
            "'To Great Heights!' en Arena para subir reputación, desbloquear la Caja Theta (3x3 + 1x2) y Battle Pass."
        ),
        "detail_en": (
            "Complete 'Easy Money - Part 1' (Skier) to unlock Ref LL1. Progress 'Balancing' and "
            "'To Great Heights!' in Arena to raise rep and unlock the Theta Secure Container and Battle Pass items."
        ),
    },
    {
        "topic_es": "Las 4 Llaves Exclusivas de Ref (Lega Medal)",
        "topic_en": "Ref's 4 Exclusive Keys (Lega Medal)",
        "detail_es": (
            "• Voron's Hideout Key (Shoreline - Cabina Norte de Pier/Swamp)\n"
            "• Leon's Hideout Key (Lighthouse - Zona sur/chalet)\n"
            "• Grumpy's Hideout Key (Interchange - Power Station exterior)\n"
            "• Shatun's Hideout Key (Woods - Aldea Norte / Cabaña)"
        ),
        "detail_en": (
            "• Voron's Hideout Key (Shoreline)\n"
            "• Leon's Hideout Key (Lighthouse)\n"
            "• Grumpy's Hideout Key (Interchange - Power Station)\n"
            "• Shatun's Hideout Key (Woods - Northern village)"
        ),
    },
]


ACHIEVEMENT_CATEGORIES: List[str] = [
    "Todos",
    "Bosses",
    "Combate & Progresión",
    "Secretos / Endgame",
    "Eventos",
]


ACHIEVEMENTS_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "ach_welcome_to_tarkov",
        "name": "Welcome to Tarkov",
        "category": "Combate & Progresión",
        "rarity": "Common",
        "pct_players": 78.4,
        "condition_es": "Morir por primera vez en una incursión de Tarkov.",
        "condition_en": "Die for the very first time in a Tarkov raid.",
        "tip_es": "Se obtiene de forma natural en tus primeras raids.",
        "tip_en": "Earned naturally during your earliest raids.",
        "reward": "Medalla inicial",
    },
    {
        "id": "ach_first_time_always_hurts",
        "name": "First Time Always Hurts",
        "category": "Combate & Progresión",
        "rarity": "Common",
        "pct_players": 49.2,
        "condition_es": "Sobrevivir y extraer de una raid con al menos una extremidad negra o fracturada.",
        "condition_en": "Survive and extract with a blacked-out limb or fracture.",
        "tip_es": "Usa analgésicos (Vaseline/Ibuprofen) para llegar al extract sin reparar la fractura.",
        "tip_en": "Pop painkillers and extract before splinting a fracture.",
        "reward": "Insignia de supervivencia",
    },
    {
        "id": "ach_ready_for_anything",
        "name": "Ready for Anything",
        "category": "Combate & Progresión",
        "rarity": "Common",
        "pct_players": 31.5,
        "condition_es": "Construir todas las estaciones iniciales básicas del Hideout (Nv. 1).",
        "condition_en": "Construct all basic Level 1 Hideout stations.",
        "tip_es": "Prioriza Generator, Workbench, Medstation, Lavatory y Nutrition Unit.",
        "tip_en": "Prioritize Generator, Workbench, Medstation, Lavatory, and Nutrition Unit.",
        "reward": "Progreso de perfil",
    },
    {
        "id": "ach_killer7",
        "name": "Killer7",
        "category": "Combate & Progresión",
        "rarity": "Ultra Rare",
        "pct_players": 1.8,
        "condition_es": "Eliminar a 7 PMCs distintos en una sola incursión sin morir.",
        "condition_en": "Eliminate 7 different PMCs in a single raid without dying.",
        "tip_es": "Streets of Tarkov o Lighthouse en hora pico de PvP maximizan los spawns de PMCs.",
        "tip_en": "Streets of Tarkov or Lighthouse at peak PvP hours offer enough PMC density.",
        "reward": "Trofeo de élite PvP",
    },
    {
        "id": "ach_blind_fury",
        "name": "Blind Fury",
        "category": "Combate & Progresión",
        "rarity": "Rare",
        "pct_players": 6.4,
        "condition_es": "Matar a un enemigo mientras estás completamente cegado por una granada flash.",
        "condition_en": "Kill an enemy while completely blinded by a flashbang.",
        "tip_es": "En Factory, usa una Zvezda o M7290 y pre-dispara al pasillo mientras estás flasheado.",
        "tip_en": "In Factory, pre-fire hallways immediately when flashed.",
        "reward": "Insignia de combate",
    },
    {
        "id": "ach_bear_with_me",
        "name": "Bear With Me",
        "category": "Combate & Progresión",
        "rarity": "Rare",
        "pct_players": 9.1,
        "condition_es": "Eliminar 50 PMCs de la facción BEAR.",
        "condition_en": "Eliminate 50 BEAR faction PMCs.",
        "tip_es": "Factory y Customs aceleran los conteos de kills en CQC.",
        "tip_en": "Factory and Customs accelerate CQC PMC kills.",
        "reward": "Medalla de facción",
    },
    {
        "id": "ach_usec_your_head",
        "name": "USEC Your Head",
        "category": "Combate & Progresión",
        "rarity": "Rare",
        "pct_players": 14.3,
        "condition_es": "Eliminar 50 PMCs de la facción USEC.",
        "condition_en": "Eliminate 50 USEC faction PMCs.",
        "tip_es": "Los USEC son mayoría en servidores NA/EU/LATAM; se completa jugando quests de PvP.",
        "tip_en": "USECs are the majority faction; progresses naturally during PvP quests.",
        "reward": "Medalla de facción",
    },
    {
        "id": "ach_all_wheel_drive",
        "name": "All Wheel Drive",
        "category": "Combate & Progresión",
        "rarity": "Rare",
        "pct_players": 8.7,
        "condition_es": "Extraer utilizando el BTR o extracciones vehiculares (V-Ex) en todos los mapas con vehículo.",
        "condition_en": "Extract using Vehicle Extracts across every map featuring a V-Ex.",
        "tip_es": "Lleva siempre 5.000-40.000 ₽ en el contenedor seguro (Customs, Woods, Interchange, Lighthouse, Streets, Ground Zero).",
        "tip_en": "Keep roubles in your secure container for Customs, Woods, Interchange, Lighthouse, Streets, and Ground Zero.",
        "reward": "+Scav Karma acumulado",
    },
    {
        "id": "ach_high_competition",
        "name": "High Competition",
        "category": "Combate & Progresión",
        "rarity": "Rare",
        "pct_players": 11.2,
        "condition_es": "Alcanzar el nivel de reputación 4 (King/LL4) con todos los comerciantes clásicos.",
        "condition_en": "Reach Loyalty Level 4 (LL4) with all classic traders.",
        "tip_es": "Completa misiones diarias desde nivel 35 para empujar la rep de Jaeger y Ragman.",
        "tip_en": "Use daily operational tasks after level 35 to top off Jaeger and Ragman rep.",
        "reward": "Insignia comercial",
    },
    {
        "id": "ach_reshala",
        "name": "Dorms King (Reshala)",
        "category": "Bosses",
        "rarity": "Common",
        "pct_players": 26.5,
        "condition_es": "Eliminar al Boss Reshala en Customs.",
        "condition_en": "Eliminate Boss Reshala on Customs.",
        "tip_es": "Revisa Dorms (2/3 pisos) y New Gas Station; usa granadas para hacer mover a sus 4 guardias.",
        "tip_en": "Check 2/3-story Dorms and New Gas; use grenades to displace his 4 guards.",
        "reward": "Golden TT (loot) + Logro",
    },
    {
        "id": "ach_killa_1",
        "name": "Tracksuit Enjoyer (Killa)",
        "category": "Bosses",
        "rarity": "Common",
        "pct_players": 19.4,
        "condition_es": "Eliminar a Killa en Interchange.",
        "condition_en": "Eliminate Killa on Interchange.",
        "tip_es": "Lleva munición con +45 de penetración (M80A1, M61, SNB, BP) para su casco Maska/chaleco.",
        "tip_en": "Bring 45+ pen rounds (M80A1, M61, SNB, BP) to pierce his armor.",
        "reward": "Logro de Boss",
    },
    {
        "id": "ach_master_of_ultra",
        "name": "Master of ULTRA",
        "category": "Bosses",
        "rarity": "Ultra Rare",
        "pct_players": 2.4,
        "condition_es": "Eliminar a Killa 15 veces en Interchange (versión accesible de Stylish One).",
        "condition_en": "Eliminate Killa 15 times on Interchange.",
        "tip_es": "Usa granadas flash/stuns en Goshan, IDEA, OLI y el centro del mall para forzar su línea de voz.",
        "tip_en": "Throw flashbangs in Goshan, IDEA, OLI, and mall center to trigger his voice line.",
        "reward": "Desbloqueo de chaqueta Adik Tracksuit (según temporada)",
    },
    {
        "id": "ach_stylish_one",
        "name": "The Stylish One",
        "category": "Bosses",
        "rarity": "Legendary",
        "pct_players": 0.4,
        "condition_es": "Eliminar a Killa 50 (o 100 según parche) veces y entregar sus cascos en la quest.",
        "condition_en": "Eliminate Killa 50/100 times for Ragman's Stylish One quest.",
        "tip_es": "Carga paquete ligero con SJ6 + Trimadol y SVDS/SA-58 con M61 para rutas de 4 minutos.",
        "tip_en": "Run light kit + SJ6/Trimadol and M61 rifles for fast 4-minute mall sweeps.",
        "reward": "Adik Tracksuit permanente",
    },
    {
        "id": "ach_tagilla",
        "name": "Hammer Time (Tagilla)",
        "category": "Bosses",
        "rarity": "Common",
        "pct_players": 24.8,
        "condition_es": "Eliminar a Tagilla en Factory.",
        "condition_en": "Eliminate Tagilla on Factory.",
        "tip_es": "Apunta a piernas con Flechette/RIP o usa munición AP cuando recarga o cambia a su martillo.",
        "tip_en": "Aim for legs with Flechette/RIP or burst thorax when he swaps to his sledgehammer.",
        "reward": "Logro de Boss",
    },
    {
        "id": "ach_shturman",
        "name": "Woods Keeper (Shturman)",
        "category": "Bosses",
        "rarity": "Common",
        "pct_players": 22.1,
        "condition_es": "Eliminar a Shturman en Woods.",
        "condition_en": "Eliminate Shturman on Woods.",
        "tip_es": "Flanquea Sawmill desde Dickhead Rock o Spine; evita cruzar abierto frente a las cabañas.",
        "tip_en": "Flank Sawmill from Dickhead Rock or Spine; never peek open lines from cabins.",
        "reward": "Llave Shturman + Logro",
    },
    {
        "id": "ach_glukhar",
        "name": "Reserve Commander (Glukhar)",
        "category": "Bosses",
        "rarity": "Rare",
        "pct_players": 13.7,
        "condition_es": "Eliminar a Glukhar y sobrevivir a sus 6 guardias en Reserve.",
        "condition_en": "Eliminate Glukhar and survive his 6 guards on Reserve.",
        "tip_es": "Atráelos a pasillos de Black/White Knight o edificios K; nunca pelees en campo abierto.",
        "tip_en": "Funnel his guards into Knight buildings or K-shed doors; avoid open peeks.",
        "reward": "Logro de Boss",
    },
    {
        "id": "ach_sanitar",
        "name": "No Sworn Enemy (Sanitar)",
        "category": "Bosses",
        "rarity": "Rare",
        "pct_players": 15.0,
        "condition_es": "Eliminar a Sanitar en Shoreline.",
        "condition_en": "Eliminate Sanitar on Shoreline.",
        "tip_es": "Spawnea en Cottages, Pier o Resort Ala Este/Oeste. Remátalo rápido antes de que use stims.",
        "tip_en": "Spawns at Cottages, Pier, or Resort. Burst him before he pops healing stims.",
        "reward": "Logro de Boss",
    },
    {
        "id": "ach_goons",
        "name": "Just Business (The Goons)",
        "category": "Bosses",
        "rarity": "Rare",
        "pct_players": 8.9,
        "condition_es": "Eliminar a Knight, Big Pipe y Birdeye.",
        "condition_en": "Eliminate Knight, Big Pipe, and Birdeye.",
        "tip_es": "Cúbrete detrás de puertas cerradas (Fortress/Weather Station): Knight y Big Pipe rushean primero.",
        "tip_en": "Hold a closed doorway: Knight and Big Pipe rush aggressively while Birdeye trails silently.",
        "reward": "Logro de Escuadrón",
    },
    {
        "id": "ach_kaban",
        "name": "LexOs Boss (Kaban)",
        "category": "Bosses",
        "rarity": "Rare",
        "pct_players": 9.6,
        "condition_es": "Eliminar a Kaban en el concesionario LexOs de Streets of Tarkov.",
        "condition_en": "Eliminate Kaban inside LexOs dealership on Streets of Tarkov.",
        "tip_es": "Despeja primero las minas alrededor y a los francotiradores en techos antes de entrar por el garage.",
        "tip_en": "Clear perimeter mines and roof snipers first before breaching the garage.",
        "reward": "PKP / PKM loot + Logro",
    },
    {
        "id": "ach_kollontay",
        "name": "Police Brutality (Kollontay)",
        "category": "Bosses",
        "rarity": "Rare",
        "pct_players": 8.4,
        "condition_es": "Eliminar a Kollontay en Ground Zero o Streets (Klimov Mall / MVD).",
        "condition_en": "Eliminate Kollontay on Ground Zero or Streets (Klimov Mall / MVD).",
        "tip_es": "Si saca su porra activa el debuff de arma trabada (Panic): aléjate y cámbiale el ángulo.",
        "tip_en": "When he draws his baton it induces a weapon jam debuff: keep distance and reposition.",
        "reward": "Logro de Boss",
    },
    {
        "id": "ach_partisan",
        "name": "Old School (Partisan)",
        "category": "Bosses",
        "rarity": "Rare",
        "pct_players": 12.6,
        "condition_es": "Eliminar al cazador solitario Partisan (Woods / Customs / Shoreline / Lighthouse).",
        "condition_en": "Eliminate Partisan on Woods, Customs, Shoreline, or Lighthouse.",
        "tip_es": "Cuidado con sus trampas de cable (tripwires) con granadas alrededor de arbustos.",
        "tip_en": "Watch for grenade tripwires rigged across bushes and choke points near him.",
        "reward": "Mochila Partisan + Logro",
    },
    {
        "id": "ach_zryachiy",
        "name": "Is This Legal? (Zryachiy)",
        "category": "Secretos / Endgame",
        "rarity": "Ultra Rare",
        "pct_players": 1.5,
        "condition_es": "Eliminar a Zryachiy en el faro de Lighthouse.",
        "condition_en": "Eliminate Zryachiy on Lighthouse island.",
        "tip_es": "Si tienes el transmisor DSP codificado, matarlo lo bloqueará y deberás hacer 'Make Amends'.",
        "tip_en": "Killing him disables an encoded DSP transmitter and triggers the Make Amends penalty chain.",
        "reward": "Logro secreto",
    },
    {
        "id": "ach_snowball",
        "name": "Snowball",
        "category": "Secretos / Endgame",
        "rarity": "Legendary",
        "pct_players": 0.3,
        "condition_es": "Matar a TODOS los Bosses de Tarkov en una racha consecutiva sin morir nunca.",
        "condition_en": "Kill EVERY Tarkov Boss in a single unbroken streak without dying.",
        "tip_es": "Empieza por los más impredecibles (Goons, Cultists, Killa, Glukhar) y deja Tagilla/Reshala para el final.",
        "tip_en": "Hunt high-variance bosses first (Goons, Cultists, Killa, Glukhar) and save Tagilla/Reshala last.",
        "reward": "Predator / BDU exclusiva + Logro mítico",
    },
    {
        "id": "ach_lightkeeper",
        "name": "The Lightkeeper",
        "category": "Secretos / Endgame",
        "rarity": "Ultra Rare",
        "pct_players": 2.9,
        "condition_es": "Desbloquear acceso a la isla del Farero y conocer a Lightkeeper.",
        "condition_en": "Unlock Lighthouse island and meet Lightkeeper in person.",
        "tip_es": "Completa la cadena 'Network Provider' -> 'Assessment' -> 'Knock-Knock' -> 'Getting Acquainted'.",
        "tip_en": "Follow 'Network Provider' -> 'Assessment' -> 'Knock-Knock' -> 'Getting Acquainted'.",
        "reward": "Acceso a Lightkeeper + Crafteos élite",
    },
    {
        "id": "ach_chris_heir",
        "name": "Dawn of a New Era (Collector)",
        "category": "Secretos / Endgame",
        "rarity": "Ultra Rare",
        "pct_players": 1.9,
        "condition_es": "Completar 'Collector' (Fence) y reclamar el Contenedor Seguro Kappa.",
        "condition_en": "Complete 'Collector' (Fence) and obtain the Kappa Secure Container.",
        "tip_es": "Reemplazó al logro retirado 'The Kappa Path / Chris's Heir' en el parche 1.1. Usa la pestaña Collector (Kappa) de TTC.",
        "tip_en": "Replaced the retired 'The Kappa Path / Chris's Heir' achievement in Patch 1.1. Track all 44 items in TTC's Collector tab.",
        "reward": "Contenedor Kappa + Armband DEADSKUL",
    },
    {
        "id": "ach_prestige_1",
        "name": "A New Beginning (Prestige I)",
        "category": "Secretos / Endgame",
        "rarity": "Legendary",
        "pct_players": 0.5,
        "condition_es": "Completar el primer reinicio voluntario de Prestige.",
        "condition_en": "Complete your first voluntary Prestige cycle.",
        "tip_es": "Planifica tus skills de Strength/Endurance Nv.20 y guarda 20M ₽ antes de activar Prestige.",
        "tip_en": "Level Strength/Endurance to Lv.20 and keep 20M RUB ready before prestiging.",
        "reward": "Brazalete + Dogtag + 5% Retención de Skills",
    },
    {
        "id": "ach_complete_remission",
        "name": "Complete Remission",
        "category": "Secretos / Endgame",
        "rarity": "Rare",
        "pct_players": 4.2,
        "condition_es": "Curarse del veneno mortal de Cultistas (Unknown Toxin) utilizando xTG-12 o Augmentin y extraer.",
        "condition_en": "Cure Cultist Unknown Toxin using xTG-12 or Augmentin and survive the raid.",
        "tip_es": "Lleva siempre un xTG-12 en el Injector Case durante raids nocturnas (22:00-07:00).",
        "tip_en": "Always keep an xTG-12 in your Injector Case during night raids (22:00-07:00).",
        "reward": "Logro oculto",
    },
    {
        "id": "ach_firefly",
        "name": "Firefly",
        "category": "Secretos / Endgame",
        "rarity": "Rare",
        "pct_players": 5.1,
        "condition_es": "Recoger el plano/objeto secreto y extraer por el área de pruebas de The Lab.",
        "condition_en": "Acquire the hidden Lab residential/cargo access and extract cleanly.",
        "tip_es": "Revisa la sala de oficinas nuevas de Lab (Residential Unit Keycard) y limpia Raiders.",
        "tip_en": "Check The Lab's Residential Unit area and clear nearby Raiders.",
        "reward": "Logro oculto",
    },
    {
        "id": "ach_marathon",
        "name": "Marathon",
        "category": "Eventos",
        "rarity": "Ultra Rare",
        "pct_players": 1.4,
        "condition_es": "Completar el recorrido continuo de Transits desde Ground Zero hasta Shoreline/Terminal.",
        "condition_en": "Complete the full continuous Transit chain starting from Ground Zero.",
        "tip_es": "Usa la pestaña 'BTR & Transits' para verificar los horarios (1:00/7:00 min) y lugares de cada tránsito.",
        "tip_en": "Check the 'BTR & Transits' view for exact transit locations and unlock timers.",
        "reward": "Logro especial Marathon",
    },
    {
        "id": "ach_khorovod",
        "name": "Khorovod",
        "category": "Eventos",
        "rarity": "Ultra Rare",
        "pct_players": 1.1,
        "condition_es": "Defender los generadores festivos en los mapas conectados durante el evento de invierno.",
        "condition_en": "Defend festive generators across linked maps during the Winter Event.",
        "tip_es": "Lleva comida, agua y cargadores extra; cada generador atrae oleadas de Scavs y Bosses.",
        "tip_en": "Bring extra food, water, and mags; each generator triggers scav and boss waves.",
        "reward": "Vestimenta invernal + Logro de evento",
    },
    {
        "id": "ach_zombie_outbreak",
        "name": "Patient Zero / Infected Lab",
        "category": "Eventos",
        "rarity": "Rare",
        "pct_players": 6.8,
        "condition_es": "Sobrevivir a la infección en Infected Lab / Factory durante el evento de Halloween.",
        "condition_en": "Survive the outbreak inside Infected Lab / Factory during the Halloween event.",
        "tip_es": "Usa munición de alto daño a carne (HP/RIP/Magnum) contra infectados y cuida la hidratación.",
        "tip_en": "High flesh-damage rounds shred infected; carry extra water for virus debuffs.",
        "reward": "Logro de evento Halloween",
    },
    {
        "id": "ach_cult_leader",
        "name": "Hammer of Light (Cultist Circle)",
        "category": "Combate & Progresión",
        "rarity": "Rare",
        "pct_players": 16.2,
        "condition_es": "Construir el Cultist Circle en el Hideout y completar sacrificios exitosos.",
        "condition_en": "Build the Hideout Cultist Circle and complete sacrifices.",
        "tip_es": "Usa el calculador de recetas del Cultist Circle en la pestaña 'Flea, Hideout & Barters'.",
        "tip_en": "Use the Cultist Circle recipes guide inside the 'Flea, Hideout & Barters' tab.",
        "reward": "Acceso a recetas místicas",
    },
]


CLOTHING_FACTIONS: List[str] = ["Todas", "USEC", "BEAR", "Ambos (Ref/Arena)"]
CLOTHING_SLOTS: List[str] = ["Todos", "Superior (Upper)", "Inferior (Lower)"]


TACTICAL_CLOTHING_CATALOG: List[Dict[str, Any]] = [
    # --- USEC ---
    {
        "id": "cloth_usec_pcu_ironsight",
        "icon_key": "cloth_usec_pcu_ironsight",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/ee/USEC_PCU_Ironsight.png/revision/latest?cb=20191031183212",
        "name": "USEC PCU Ironsight",
        "faction": "USEC",
        "slot": "Superior (Upper)",
        "pmc_level": 12,
        "trader_req": "Ragman LL2",
        "quest_req": "—",
        "price_text": "110.000 ₽",
        "camo_notes_es": "Chaqueta gris/oliva discreta, ideal para mapas urbanos (Streets, Interchange).",
        "camo_notes_en": "Low-profile grey/olive shell suited for urban maps (Streets, Interchange).",
    },
    {
        "id": "cloth_usec_flex_field",
        "icon_key": "cloth_usec_flex_field",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a9/USEC_Softshell_Flexion.png/revision/latest?cb=20191031183214",
        "name": "USEC Softshell Flexion",
        "faction": "USEC",
        "slot": "Superior (Upper)",
        "pmc_level": 18,
        "trader_req": "Ragman LL2",
        "quest_req": "—",
        "price_text": "150.000 ₽",
        "camo_notes_es": "Camuflaje árido ligero con mangas arremangadas; buena silueta en Lighthouse.",
        "camo_notes_en": "Lightweight arid field shirt; blends well around Lighthouse rocks.",
    },
    {
        "id": "cloth_usec_aggressor_tac",
        "icon_key": "cloth_usec_aggressor_tac",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/7d/USEC_Aggressor_TAC.png/revision/latest?cb=20191031183208",
        "name": "USEC Aggressor TAC",
        "faction": "USEC",
        "slot": "Superior (Upper)",
        "pmc_level": 24,
        "trader_req": "Ragman LL3",
        "quest_req": "—",
        "price_text": "240.000 ₽",
        "camo_notes_es": "Tono oscuro/negro táctico con coderas integradas.",
        "camo_notes_en": "Dark tactical combat shirt with integrated elbow pads.",
    },
    {
        "id": "cloth_usec_tier_2",
        "icon_key": "cloth_usec_tier_2",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/5/55/USEC_Tier2_Upper.png/revision/latest?cb=20200314015853",
        "name": "USEC Tier 2",
        "faction": "USEC",
        "slot": "Superior (Upper)",
        "pmc_level": 28,
        "trader_req": "Ragman LL3",
        "quest_req": "—",
        "price_text": "380.000 ₽",
        "camo_notes_es": "Multicam clásico con excelente camuflaje en Woods y Shoreline.",
        "camo_notes_en": "Classic Multicam top offering top concealment on Woods and Shoreline.",
    },
    {
        "id": "cloth_usec_woodland_infiltrator",
        "icon_key": "cloth_usec_woodland_infiltrator",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/d1/USEC_Woodland_Infiltrator_Upper.png/revision/latest?cb=20191031183217",
        "name": "USEC Woodland Infiltrator",
        "faction": "USEC",
        "slot": "Superior (Upper)",
        "pmc_level": 35,
        "trader_req": "Ragman LL4",
        "quest_req": "—",
        "price_text": "650.000 ₽",
        "camo_notes_es": "Verde bosque profundo (M81 Woodland); de los mejores camos para arbustos.",
        "camo_notes_en": "Deep M81 Woodland camo; top-tier concealment in foliage.",
    },
    {
        "id": "cloth_usec_night_patrol",
        "icon_key": "cloth_usec_night_patrol",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a4/USEC_Night_Patrol.png/revision/latest?cb=20201024104929",
        "name": "USEC Night Patrol",
        "faction": "USEC",
        "slot": "Superior (Upper)",
        "pmc_level": 40,
        "trader_req": "Ragman LL4",
        "quest_req": "Textile - Part 1",
        "price_text": "1.200.000 ₽",
        "camo_notes_es": "Camo negro/carbón muy buscado para raids nocturnas y Labs.",
        "camo_notes_en": "Stealth charcoal/black top favored for night raids and The Lab.",
    },
    {
        "id": "cloth_usec_predator",
        "icon_key": "cloth_usec_predator",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/73/USEC_Predator_icon.png/revision/latest?cb=20230916221654",
        "name": "USEC Predator Shirt",
        "faction": "USEC",
        "slot": "Superior (Upper)",
        "pmc_level": 50,
        "trader_req": "Ragman LL4",
        "quest_req": "Snowball / Hunter",
        "price_text": "3.500.000 ₽",
        "camo_notes_es": "Franelas rojas icónicas de estatus endgame USEC.",
        "camo_notes_en": "Iconic red plaid endgame status shirt for USEC.",
    },
    {
        "id": "cloth_usec_urban_responder",
        "icon_key": "cloth_usec_urban_responder",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/44/USEC_Urban_responder_lower.png/revision/latest?cb=20201024104927",
        "name": "USEC Urban Responder",
        "faction": "USEC",
        "slot": "Inferior (Lower)",
        "pmc_level": 12,
        "trader_req": "Ragman LL2",
        "quest_req": "—",
        "price_text": "95.000 ₽",
        "camo_notes_es": "Pantalón gris oscuro económico para combinar con PCU Ironsight.",
        "camo_notes_en": "Budget dark grey pants pairing with PCU Ironsight.",
    },
    {
        "id": "cloth_usec_commando",
        "icon_key": "cloth_usec_commando",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/3f/USEC_Commando_Lower_Icon.png/revision/latest?cb=20200314151025",
        "name": "USEC Commando",
        "faction": "USEC",
        "slot": "Inferior (Lower)",
        "pmc_level": 25,
        "trader_req": "Ragman LL3",
        "quest_req": "—",
        "price_text": "260.000 ₽",
        "camo_notes_es": "Pantalón Multicam con rodilleras integradas.",
        "camo_notes_en": "Multicam Crye-style pants with integrated knee pads.",
    },
    {
        "id": "cloth_usec_tier_3_pants",
        "icon_key": "cloth_usec_tier_3_pants",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/6/60/USEC_TIER_3_lower_Ico.png/revision/latest?cb=20210106044128",
        "name": "USEC Tier 3",
        "faction": "USEC",
        "slot": "Inferior (Lower)",
        "pmc_level": 37,
        "trader_req": "Ragman LL4",
        "quest_req": "Textile - Part 2",
        "price_text": "780.000 ₽",
        "camo_notes_es": "Pantalón táctico oscuro de alto nivel.",
        "camo_notes_en": "High-tier dark tactical combat trousers.",
    },
    {
        "id": "cloth_usec_chameleon",
        "icon_key": "cloth_usec_chameleon",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/d4/USEC_Woodland_Infiltrator_Lower.png/revision/latest?cb=20191031183215",
        "name": "USEC Woodland Infiltrator Lower",
        "faction": "USEC",
        "slot": "Inferior (Lower)",
        "pmc_level": 44,
        "trader_req": "Ragman LL4",
        "quest_req": "—",
        "price_text": "1.600.000 ₽",
        "camo_notes_es": "Pantalón M81 Woodland con perfil de camuflaje forestal.",
        "camo_notes_en": "Woodland camo trousers for dense forest maps.",
    },
    # --- BEAR ---
    {
        "id": "cloth_bear_sumrak",
        "icon_key": "cloth_bear_sumrak",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/3e/BEAR_Sumrak_Icon.png/revision/latest?cb=20211229192131",
        "name": "BEAR Sumrak",
        "faction": "BEAR",
        "slot": "Superior (Upper)",
        "pmc_level": 12,
        "trader_req": "Ragman LL2",
        "quest_req": "—",
        "price_text": "115.000 ₽",
        "camo_notes_es": "Camuflaje Berezka amarillo/verde ideal para los prados de Woods y Customs.",
        "camo_notes_en": "Berezka camo great for Woods grass and Customs foliage.",
    },
    {
        "id": "cloth_bear_tigra",
        "icon_key": "cloth_bear_tigra",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/f8/BEAR_TIGR_upper_Icon.png/revision/latest?cb=20200531205202",
        "name": "BEAR Tigr",
        "faction": "BEAR",
        "slot": "Superior (Upper)",
        "pmc_level": 20,
        "trader_req": "Ragman LL2",
        "quest_req": "—",
        "price_text": "180.000 ₽",
        "camo_notes_es": "Patrón de rayas oscuras estilo fuerzas especiales rusas.",
        "camo_notes_en": "Dark tiger-stripe top in Russian Spetsnaz style.",
    },
    {
        "id": "cloth_bear_gorka_4",
        "icon_key": "cloth_bear_gorka_4",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/17/BEAR_Gorka_SSO.png/revision/latest?cb=20191101052433",
        "name": "BEAR Gorka SSO",
        "faction": "BEAR",
        "slot": "Superior (Upper)",
        "pmc_level": 26,
        "trader_req": "Ragman LL3",
        "quest_req": "—",
        "price_text": "290.000 ₽",
        "camo_notes_es": "Chaqueta resistente color khaki/oliva muy reconocible para BEAR.",
        "camo_notes_en": "Iconic khaki/olive mountain suit anorak for BEAR.",
    },
    {
        "id": "cloth_bear_spn",
        "icon_key": "cloth_bear_spn",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/15/BEARSPNUpperIcon.png/revision/latest?cb=20230110210250",
        "name": "BEAR SPN",
        "faction": "BEAR",
        "slot": "Superior (Upper)",
        "pmc_level": 35,
        "trader_req": "Ragman LL4",
        "quest_req": "—",
        "price_text": "690.000 ₽",
        "camo_notes_es": "Manga corta táctica con tatuaje; popular para runs agresivos en Lab/Factory.",
        "camo_notes_en": "Short-sleeve tactical shirt with sleeve tattoo; popular for Lab/Factory.",
    },
    {
        "id": "cloth_bear_zaslon",
        "icon_key": "cloth_bear_zaslon",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/fb/BEAR_Zaslon_Icon.png/revision/latest?cb=20200120184413",
        "name": "BEAR Zaslon",
        "faction": "BEAR",
        "slot": "Superior (Upper)",
        "pmc_level": 42,
        "trader_req": "Ragman LL4",
        "quest_req": "Textile - Part 2",
        "price_text": "1.350.000 ₽",
        "camo_notes_es": "Conjunto oscuro de élite con diseño de fuerzas especiales SVR.",
        "camo_notes_en": "Elite dark SVR-inspired special forces top.",
    },
    {
        "id": "cloth_bear_telnik",
        "icon_key": "cloth_bear_telnik",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/fa/BEAR_Telnik.png/revision/latest?cb=20200406145319",
        "name": "BEAR Telnik",
        "faction": "BEAR",
        "slot": "Superior (Upper)",
        "pmc_level": 18,
        "trader_req": "Ragman LL2",
        "quest_req": "—",
        "price_text": "160.000 ₽",
        "camo_notes_es": "Camiseta rayada clásica Telnyashka debajo de chaqueta verde.",
        "camo_notes_en": "Classic striped Telnyashka undershirt under field jacket.",
    },
    {
        "id": "cloth_bear_oldschool_pants",
        "icon_key": "cloth_bear_oldschool_pants",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/d8/BEAR_Oldschool_Icon.png/revision/latest?cb=20200531205120",
        "name": "BEAR Oldschool",
        "faction": "BEAR",
        "slot": "Inferior (Lower)",
        "pmc_level": 14,
        "trader_req": "Ragman LL2",
        "quest_req": "—",
        "price_text": "105.000 ₽",
        "camo_notes_es": "Pantalón clásico oscuro con rodilleras reforzadas.",
        "camo_notes_en": "Classic dark trousers with reinforced knees.",
    },
    {
        "id": "cloth_bear_uragan",
        "icon_key": "cloth_bear_uragan",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/c/c1/BEAR_Recon_EMR_Icon.png/revision/latest?cb=20260519143030",
        "name": "BEAR Recon EMR",
        "faction": "BEAR",
        "slot": "Inferior (Lower)",
        "pmc_level": 32,
        "trader_req": "Ragman LL3",
        "quest_req": "—",
        "price_text": "440.000 ₽",
        "camo_notes_es": "Pantalón EMR / digital flora verde para camuflaje en bosque.",
        "camo_notes_en": "EMR digital-flora trousers suited for dense forest.",
    },
    {
        "id": "cloth_bear_rysi",
        "icon_key": "cloth_bear_rysi",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/e6/BEAR_Zaslon_lower_Icon.png/revision/latest?cb=20200531205201",
        "name": "BEAR Zaslon Lower",
        "faction": "BEAR",
        "slot": "Inferior (Lower)",
        "pmc_level": 40,
        "trader_req": "Ragman LL4",
        "quest_req": "Textile - Part 1",
        "price_text": "980.000 ₽",
        "camo_notes_es": "Pantalón táctico oscuro de alta gama para combinación nocturna.",
        "camo_notes_en": "High-end dark trousers for night stealth kits.",
    },
    # --- AMBOS / REF / KILLA ---
    {
        "id": "cloth_both_adik_tracksuit",
        "icon_key": "cloth_both_adik_tracksuit",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/aa/Adik_Tracksuit.png/revision/latest?cb=20200103094116",
        "name": "Adik Tracksuit (Upper)",
        "faction": "Ambos (Ref/Arena)",
        "slot": "Superior (Upper)",
        "pmc_level": 48,
        "trader_req": "Ragman LL4",
        "quest_req": "The Stylish One (Killa)",
        "price_text": "4.000.000 ₽",
        "camo_notes_es": "La mítica campera negra con tres rayas blancas de Killa.",
        "camo_notes_en": "Killa's iconic black three-stripe tracksuit jacket.",
    },
    {
        "id": "cloth_both_arena_operator",
        "icon_key": "cloth_both_arena_operator",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/41/Rash_guard_%28Arena_Gladiator%29_icon.png/revision/latest?cb=20260427233408",
        "name": "Rash guard (Arena Gladiator)",
        "faction": "Ambos (Ref/Arena)",
        "slot": "Superior (Upper)",
        "pmc_level": 15,
        "trader_req": "Ref LL2 / Battle Pass",
        "quest_req": "To Great Heights!",
        "price_text": "GP Coins / Arena",
        "camo_notes_es": "Cosméticos desbloqueados en Arena que se sincronizan con Tarkov PvP/PvE.",
        "camo_notes_en": "Arena Battle Pass cosmetics synced directly into EFT PvP/PvE.",
    },
    {
        "id": "cloth_both_prestige_suit",
        "icon_key": "cloth_both_prestige_suit",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/e6/Green_Hawaii_shirt_Icon.png/revision/latest?cb=20250711072617",
        "name": "Green Hawaii shirt (Prestige 4)",
        "faction": "Ambos (Ref/Arena)",
        "slot": "Superior (Upper)",
        "pmc_level": 1,
        "trader_req": "Ragman LL1 (Prestige 4)",
        "quest_req": "New Beginning",
        "price_text": "Gratis (Permanente)",
        "camo_notes_es": "Camisa exclusiva permanente desbloqueada al alcanzar Prestige 4.",
        "camo_notes_en": "Exclusive permanent Hawaiian shirt unlocked at Prestige 4.",
    },
    {
        "id": "cloth_both_winter_khorovod",
        "icon_key": "cloth_both_winter_khorovod",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/fd/BEAR_Winter_lower_icon.png/revision/latest?cb=20250101160257",
        "name": "BEAR Winter Lower (Khorovod)",
        "faction": "Ambos (Ref/Arena)",
        "slot": "Inferior (Lower)",
        "pmc_level": 1,
        "trader_req": "Evento Invierno",
        "quest_req": "Khorovod",
        "price_text": "Recompensa Evento",
        "camo_notes_es": "Camuflaje blanco invernal permanente obtenido por evento.",
        "camo_notes_en": "Permanent winter white camo unlocked via Khorovod event.",
    },
]


def _load_wiki_achievements() -> None:
    """Fusiona el catálogo oficial completo de logros de la Wiki/Steam (data/achievements_wiki.json)."""
    candidates = [
        os.path.join(BASE_DIR, "data", "achievements_wiki.json"),
        os.path.join(BUNDLE_DIR, "data", "achievements_wiki.json"),
    ]
    existing_names = {a.get("name", "").strip().lower() for a in ACHIEVEMENTS_CATALOG}
    existing_ids = {a.get("id", "") for a in ACHIEVEMENTS_CATALOG}
    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                items = json.load(fh)
            for item in items:
                aid = item.get("id")
                aname = str(item.get("name") or "").strip()
                if not aid or not aname or aid in existing_ids or aname.lower() in existing_names:
                    continue
                ACHIEVEMENTS_CATALOG.append(item)
                existing_ids.add(aid)
                existing_names.add(aname.lower())
            break
        except Exception:
            continue


_load_wiki_achievements()


def filter_achievements(
    category: str = "Todos",
    query: str = "",
    only_missing: bool = False,
    unlocked_ids: Optional[Set[str]] = None,
) -> List[Dict[str, Any]]:
    """Filtra el catálogo de Achievements por categoría, texto o estado pendiente."""
    q = (query or "").strip().lower()
    done = unlocked_ids or set()
    res: List[Dict[str, Any]] = []
    for ach in ACHIEVEMENTS_CATALOG:
        if category and category != "Todos" and ach.get("category") != category:
            continue
        if only_missing and ach["id"] in done:
            continue
        if q:
            haystack = " ".join([
                ach.get("name", ""),
                ach.get("category", ""),
                ach.get("rarity", ""),
                ach.get("condition_es", ""),
                ach.get("condition_en", ""),
                ach.get("tip_es", ""),
                ach.get("tip_en", ""),
                ach.get("reward", ""),
            ]).lower()
            if q not in haystack:
                continue
        res.append(ach)
    return res


def filter_tactical_clothing(
    faction: str = "Todas",
    slot: str = "Todos",
    query: str = "",
) -> List[Dict[str, Any]]:
    """Filtra el catálogo de Ropa Táctica por facción, ranura y texto."""
    q = (query or "").strip().lower()
    res: List[Dict[str, Any]] = []
    for item in TACTICAL_CLOTHING_CATALOG:
        if faction and faction != "Todas" and item.get("faction") != faction:
            continue
        if slot and slot != "Todos" and item.get("slot") != slot:
            continue
        if q:
            haystack = " ".join([
                item.get("name", ""),
                item.get("faction", ""),
                item.get("trader_req", ""),
                item.get("quest_req", ""),
                item.get("camo_notes_es", ""),
                item.get("camo_notes_en", ""),
            ]).lower()
            if q not in haystack:
                continue
        res.append(item)
    return res
