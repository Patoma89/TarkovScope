"""
TarkovScope - Base de Conocimiento de Armas, Builds Meta, Guías Gunsmith y Contenedor Kappa
Información estructurada de la Wiki: estadísticas de armas, configuraciones Meta/Budget,
imágenes pre-cacheadas de armas y accesorios (cache/weapons/), y checklist Collector (Kappa).
"""
from typing import List, Dict, Any

WEAPONS_ARSENAL_DATA: List[Dict[str, Any]] = [
    {
        "id": "mcx_spear",
        "name": "SIG MCX SPEAR 6.8x51",
        "category": "Rifles de Asalto",
        "caliber": "6.8x51mm (.277 Fury)",
        "rpm": 800,
        "fire_modes": "Semi / Full-Auto",
        "tier": "S+ Meta",
        "best_ammo": "6.8x51mm SIG Hybrid (Pen: 47, Daño: 72) | FMJ (Prapor/Peacekeeper)",
        "stats": {"ergo": "58 (Mod)", "recoil_v": "54 (Mod)", "range": "600m"},
        "featured_parts": [
            ("p_slx68", "Supresor SLX68-MG-QD"),
            ("p_rvg", "Grip Magpul RVG"),
            ("p_vudu", "Óptica EOTech Vudu 1-6x"),
            ("p_moe_stock", "Culata Magpul MOE"),
        ],
        "meta_build": [
            "Supresor: SIG SLX68-MG-QD 6.8x51 Sound Suppressor (Incluido de fábrica)",
            "Empuñadura delantera: Magpul RVG o TangoDown Stubby BGV-MK46K",
            "Mira: EOTech Vudu 1-6x24 o Vortex Razor HD Gen.2 + DeltaPoint inclinada",
            "Culata: Magpul PRS GEN3 o MOE SL-K con cantonera Buttpad",
            "Cargador: Cargadores Lancer L7AWM de 25 tiros (7.62x51 / 6.8x51)"
        ],
        "budget_build": [
            "Viene lista para combate de serie (incluye guardamanos M-LOK y silenciador QD)",
            "Solo requiere añadir una mira holográfica EOTech EXPS3 y un grip frontal BCM KAG"
        ],
        "notes": "El rifle más letal de Escape from Tarkov. Combina cadencia de 800 RPM con munición que destroza placas Clase 5 y 6 en ráfagas cortas."
    },
    {
        "id": "m4a1",
        "name": "Colt M4A1 5.56x45",
        "category": "Rifles de Asalto",
        "caliber": "5.56x45mm NATO",
        "rpm": 800,
        "fire_modes": "Semi / Full-Auto",
        "tier": "S+ Meta",
        "best_ammo": "SSA AP (Pen: 57) / M995 (Pen: 53) / M855A1 (Pen: 44) / M856A1 (Pen: 38)",
        "stats": {"ergo": "65 (Mod)", "recoil_v": "46 (Mod)", "range": "500m"},
        "featured_parts": [
            ("p_saker", "Supresor Saker ASR 556"),
            ("p_se5", "Grip Stark SE-5 Express"),
            ("p_pmag_d60", "Tambor PMAG D-60 (60t)"),
            ("p_moe_stock", "Culata Magpul MOE + Pad"),
        ],
        "meta_build": [
            "Cañón: 370mm o 406mm + Bloque de gas MK12 Low Profile",
            "Guardamanos: SAI QD Rail 14.5\" o Daniel Defense RIS II 12.25\"",
            "Freno/Supresor: Freno ASR + Supresor SilencerCo Saker ASR 556 (o KAC NT-4)",
            "Tubo y Culata: Tubo Advanced Receiver Extension (Rojo/Negro) + Culata MOE + Buttpad",
            "Grip y Cargador: Pistolete Stark SE-5 Express + Cargador PMAG D-60 / STANAG 60 tiros"
        ],
        "budget_build": [
            "Intercambio de Mechanic LL2 ('M4A1 SOPMOD') por 2x Prokill Medallions",
            "Guardamanos Magpul MOE SL + Freno Bulletec ST-6012 + Culata DT-PR"
        ],
        "notes": "El rey de la personalización. Con la build Saker/NT-4 se convierte en un láser sin retroceso a media distancia."
    },
    {
        "id": "rd_704",
        "name": "Rifle Dynamics RD-704 7.62x39",
        "category": "Rifles de Asalto",
        "caliber": "7.62x39mm",
        "rpm": 600,
        "fire_modes": "Semi / Full-Auto",
        "tier": "S Meta",
        "best_ammo": "MAI AP (Pen: 58) / 7.62x39 BP gzh (Pen: 47) / PP gzh (Pen: 41)",
        "stats": {"ergo": "68 (Mod)", "recoil_v": "58 (Mod)", "range": "450m"},
        "featured_parts": [
            ("p_hybrid46", "Supresor Hybrid 46"),
            ("p_bastion", "Tapa Riel Bastion"),
            ("p_se5", "Grip Stark SE-5 Express"),
            ("p_moe_stock", "Culata Magpul MOE"),
        ],
        "meta_build": [
            "Supresor: SilencerCo Hybrid 46 + Adaptador Direct Thread o Lantac Dragon + BMD",
            "Tapa superior: Bastion Dust Cover o TWS Dog Leg Rail",
            "Empuñadura: Magpul RVG / SE-5 Express sobre el guardamanos SLR de serie",
            "Culata: Tubo AR integrado + Culata Magpul MOE con goma RBP",
            "Cargador: Tambor ProMag AK-A-16 de 73 tiros o polimérico de 30 tiros"
        ],
        "budget_build": [
            "Mantener guardamanos SLR original + añadir freno JMac RRD-4C 7.62",
            "Mira holográfica EOTech EXPS3 / Holosun y munición 7.62x39 PP"
        ],
        "notes": "Superior al AKM tradicional gracias a su excelente ergonomía base y su tubo de culata AR-15 integrado de fábrica."
    },
    {
        "id": "mk47_mutant",
        "name": "CMMG Mk47 Mutant 7.62x39",
        "category": "Rifles de Asalto",
        "caliber": "7.62x39mm",
        "rpm": 650,
        "fire_modes": "Semi / Full-Auto",
        "tier": "S Meta",
        "best_ammo": "7.62x39 BP gzh (Pen: 47) / PP gzh (Pen: 41) / PS gzh (Pen: 35)",
        "stats": {"ergo": "56 (Mod)", "recoil_v": "56 (Mod)", "range": "450m"},
        "featured_parts": [
            ("p_hybrid46", "Boquilla BMD / Hybrid 46"),
            ("p_se5", "Grip Stark SE-5 Express"),
            ("p_exps3", "Mira EOTech EXPS3"),
            ("p_moe_stock", "Culata Magpul MOE"),
        ],
        "meta_build": [
            "Cañón: 409mm + Guardamanos CMMG Ripstock / RSASS Handguard",
            "Boquilla: Freno Lantac Dragon 7.62x39 + Blast Mitigation Device (BMD) A3",
            "Culata: Tubo ARE + Culata KRISS Defiance DS150 o MOE + Buttpad",
            "Grip frontal: Stark SE-5 Express o RK-1 sobre montura B-25U"
        ],
        "budget_build": [
            "Cañón corto de 254mm CQC + Freno JMac RRD-4C + Culata SBA3",
            "Cargadores de aluminio de 30 tiros con munición PP"
        ],
        "notes": "Combina la pegada brutal del calibre 7.62x39 con una cadencia superior (650 RPM) y controles de plataforma AR-15."
    },
    {
        "id": "ak_74n",
        "name": "Kalashnikov AK-74N / AK-12 5.45x39",
        "category": "Rifles de Asalto",
        "caliber": "5.45x39mm",
        "rpm": 650,
        "fire_modes": "Semi / Full-Auto",
        "tier": "Budget Rey",
        "best_ammo": "7N40 (Pen: 44) / BS gs (Pen: 51) / Igolnik (Pen: 62) / BT (Pen: 37) / PP (Pen: 34)",
        "stats": {"ergo": "64 (Mod)", "recoil_v": "49 (Mod)", "range": "500m"},
        "featured_parts": [
            ("p_b10m", "Guardamanos Zenit B-10M"),
            ("p_pt3", "Culata Zenit PT-3"),
            ("p_6l31", "Cargador 6L31 (60t)"),
            ("p_rk3", "Pistolete Zenit RK-3"),
        ],
        "meta_build": [
            "Guardamanos: CAA RS47 o Zenit B-30 + B-31S o B-10M",
            "Freno: JMac RRD-4C o Silenciador Waffle Maker (Hexagon / Zenit DTK-4M)",
            "Culata: Culata plegable Zenit PT-3 Klassika o adaptador AR + MOE",
            "Cargador: Cargador de 60 tiros 6L31 (Crafteable en Lavatory Nv. 2)"
        ],
        "budget_build": [
            "Culata de polímero con cantonera GP-25 (Prapor LL2)",
            "Guardamanos Magpul MOE AK + Freno DTK-1 (Skier LL2)"
        ],
        "notes": "El rifle más confiable y abundante de Tarkov. Las cajas de balas BS, BT y PP abundan gratis en Reserve y Streets."
    },
    {
        "id": "sr_25",
        "name": "Knight's Armament SR-25 7.62x51",
        "category": "DMR / Precisión",
        "caliber": "7.62x51mm NATO",
        "rpm": 700,
        "fire_modes": "Semi-Auto",
        "tier": "S+ Meta",
        "best_ammo": "M993 (Pen: 70) / M61 (Pen: 64) / M62 Tracer (Pen: 54) / M80 (Pen: 41)",
        "stats": {"ergo": "62 (Mod)", "recoil_v": "68 (Mod)", "range": "800m"},
        "featured_parts": [
            ("p_prs_qdc", "Supresor KAC PRS/QDC"),
            ("p_vudu", "Óptica EOTech Vudu 1-6x"),
            ("p_rvg", "Grip Magpul RVG"),
            ("p_moe_stock", "Culata Magpul MOE"),
        ],
        "meta_build": [
            "Supresor: KAC PRS/QDC 7.62x51 Sound Suppressor sobre freno KAC QDC",
            "Óptica: EOTech Vudu 1-6x24 o Schmidt & Bender PM II 1-8x24",
            "Empuñadura: Magpul RVG o AFG M-LOK para maximizar velocidad de apuntado",
            "Pistolete: Ergo PSG-1 Style o GRAL-S"
        ],
        "budget_build": [
            "Usar cañón de 16\" de serie con freno Lantac Dragon 7.62x51",
            "Mira TAC30 1-4x24 (Jaeger) y munición M80 (Peacekeeper)"
        ],
        "notes": "DMR semiautomático de respuesta instantánea. Dos disparos de M80 o M62 al tórax derriban a casi cualquier objetivo."
    },
    {
        "id": "mp7a2",
        "name": "HK MP7A2 4.6x30",
        "category": "Subfusiles (SMG)",
        "caliber": "4.6x30mm HK",
        "rpm": 950,
        "fire_modes": "Semi / Full-Auto",
        "tier": "S+ Meta",
        "best_ammo": "AP SX (Pen: 53) / FMJ SX (Pen: 40) / Subsonic SX (Pen: 36, -Retroceso)",
        "stats": {"ergo": "78 (Mod)", "recoil_v": "36 (Mod)", "range": "200m"},
        "featured_parts": [
            ("p_rotex2", "Supresor B&T Rotex-2"),
            ("p_rvg", "Grip Frontal RVG / RK-0"),
            ("p_micro_t1", "Mira Aimpoint Micro T-1"),
            ("p_klesch2p", "Láser/Linterna Klesch-2P"),
        ],
        "meta_build": [
            "Supresor: B&T Rotex-2 4.6x30 sobre apagallamas HK A2",
            "Grip frontal: TangoDown Stubby o RK-0 en el riel Picatinny integrado",
            "Cargador: Cargadores de 40 tiros (Mechanic LL4) o 30 tiros (Peacekeeper LL3)",
            "Mira: Aimpoint Micro T-1 o Leupold DeltaPoint"
        ],
        "budget_build": [
            "Versión MP7A1 (con grip plegable integrado gratis) + cargadores de 30 tiros con Subsonic SX / JSP SX"
        ],
        "notes": "Reina absoluta de Factory, Labs y Dorms. A 950 RPM con FMJ SX derrite blindajes Clase 5 en menos de medio segundo."
    },
    {
        "id": "vss_val",
        "name": "VSS Vintorez / AS VAL 9x39",
        "category": "Rifles de Asalto",
        "caliber": "9x39mm Subsónico",
        "rpm": 900,
        "fire_modes": "Semi / Full-Auto",
        "tier": "S Meta",
        "best_ammo": "9x39 BP (Pen: 55) / PAB-9 (Pen: 48) / SP-6 (Pen: 46) / SPP (Pen: 35)",
        "stats": {"ergo": "60 (Mod)", "recoil_v": "42 (Mod)", "range": "250m"},
        "featured_parts": [
            ("p_sr3m_mag", "Cargador SR3M.130 (30t)"),
            ("p_rvg", "Grip Magpul RVG"),
            ("p_exps3", "Mira EOTech EXPS3"),
            ("p_klesch2p", "Láser Klesch-2P"),
        ],
        "meta_build": [
            "Montura en cañón: Abrazadera TOZ 6P29M o B-3 para colocar grip frontal y láser",
            "Culata (AS VAL): Adaptador Rotor 43 + Tubo AR + Culata MOE",
            "Cargador: Cargadores SR3M.130 de 30 tiros (¡Imprescindibles por su cadencia de 900 RPM!)",
            "Mira: Riel lateral OKP-7 Dovetail o montura B-13 + EOTech"
        ],
        "budget_build": [
            "VSS Vintorez (Intercambio de Prapor por 2x Filtros de Aire) + montura B-13 + cargadores de 20 tiros con SP-6"
        ],
        "notes": "El arma con menor tiempo para matar (TTK) en corta distancia. Silenciada de fábrica; ten en cuenta la caída de bala a más de 100m."
    },
    {
        "id": "saiga_12",
        "name": "Saiga-12K / MP-153 calibre 12/70",
        "category": "Escopetas & CQC",
        "caliber": "12/70 Gauge",
        "rpm": 450,
        "fire_modes": "Semi-Auto",
        "tier": "A Tier",
        "best_ammo": "12/70 Flechette (Destruye armaduras) / .50 BMG / AP-20 Slug (Pen: 37) / 8.5mm Magnum Buckshot (Leg Meta)",
        "stats": {"ergo": "55 (Mod)", "recoil_v": "115 (Mod)", "range": "75m"},
        "featured_parts": [
            ("p_salvo12", "Supresor Salvo 12"),
            ("p_rk3", "Pistolete Zenit RK-3"),
            ("p_klesch2p", "Linterna Klesch-2P"),
            ("p_micro_t1", "Mira Punto Rojo Micro T-1"),
        ],
        "meta_build": [
            "Freno/Supresor: Freno Monster Claw (Máxima reducción de retroceso) o Supresor Salvo 12",
            "Guardamanos: SOK-12 Custom Guns o Bravo-18 con riel superior",
            "Cargador (Saiga): Tambor ProMag de 20 cartuchos o cargador de 10 cartuchos",
            "Linterna: 2x o 3x linternas Klesch-2U/2P para cegar en pasillos cerrados"
        ],
        "budget_build": [
            "MP-153 con cañón de 610mm, tubo de 8 cartuchos y balas 8.5mm Magnum o Flechette"
        ],
        "notes": "Dos impactos de Flechette dejan en cero cualquier placa balística del juego; Magnum Buckshot mata de un disparo a las piernas."
    },
    {
        "id": "dvl_10",
        "name": "Lobaev Arms DVL-10 'Saboteur' 7.62x51",
        "category": "Francotiradores",
        "caliber": "7.62x51mm NATO",
        "rpm": 30,
        "fire_modes": "Cerrojo (Bolt-Action)",
        "tier": "S Meta",
        "best_ammo": "M61 (Pen: 64) / M62 Tracer (Pen: 54) / M80 (Pen: 41)",
        "stats": {"ergo": "62 (Mod)", "recoil_v": "52 (Mod)", "range": "1000m"},
        "featured_parts": [
            ("p_vudu", "Óptica EOTech Vudu 1-6x24"),
            ("p_micro_t1", "Mira Auxiliar Micro T-1"),
        ],
        "meta_build": [
            "Cañón: Cañón silenciado integralmente de 500mm DVL-10 M2 (Inaudible a más de 40 metros)",
            "Óptica: Vudu 1-6x24, Razor HD 1-6x24 o Schmidt & Bender PM II 3-12x50",
            "Cargador: Cargadores de 10 tiros DVL-10"
        ],
        "budget_build": [
            "Mosin Infantry / SV-98 con bala 7.62x54R LPS gzh o SNB / M700 con M80"
        ],
        "notes": "El rifle de cerrojo más silencioso de Tarkov. Perfecto para completar 'A Shooter Born in Heaven' y 'Tarkov Shooter' sin revelar tu posición."
    }
]


GUNSMITH_GUIDES_DATA: List[Dict[str, Any]] = [
    {
        "part": 1,
        "image_key": "gs_1",
        "title": "Gunsmith - Part 1 (MP-133)",
        "weapon": "Escopeta MP-133 12ga",
        "level": 2,
        "reqs": "Ergonomía ≥ 47  |  Retroceso (Suma) ≤ 850  |  4 Celdas máximo  |  Láser equipado",
        "parts_detailed": [
            ("p_mp133_forestock", "Guardamanos con rieles: MP-133 Custom Plastic Forestock (Mechanic LL1 - Trueque 1 HDD)"),
            ("p_mp133_grip", "Empuñadura de pistola (reemplaza culata): MP-133/153 Plastic Pistol Grip (Jaeger LL1)"),
            ("p_remington_choke", "Boquilla: Remington Tactical Choke 12ga (Jaeger LL1) o ME Adapter + GK-02"),
            ("p_ncstar_laser", "Láser táctico: NcSTAR Tactical Blue Laser LAM-module (Skier LL1)"),
            ("p_kac_vfg", "Empuñadura delantera: KAC Vertical Foregrip o Zenit RK-6 (Peacekeeper LL1 / Skier LL1)"),
        ]
    },
    {
        "part": 2,
        "image_key": "gs_2",
        "title": "Gunsmith - Part 2 (AKS-74U)",
        "weapon": "Kalashnikov AKS-74U 5.45x39",
        "level": 5,
        "reqs": "Ergonomía ≥ 58  |  Retroceso ≤ 500  |  Cargador de 60 tiros  |  6 Celdas máx (¡Plegar culata!)",
        "parts_detailed": [
            ("p_b11", "Guardamanos con riel: AKS-74U Zenit B-11 Handguard (Skier LL1)"),
            ("p_uvg", "Empuñadura delantera: Viking Tactics UVG o Zenit RK-0 (Peacekeeper / Skier)"),
            ("p_6l31", "Cargador: 5.45x39 6L31 60-round Magazine (Lavatory Nv. 2 o trueque Prapor LL2)"),
            ("p_rk3", "Pistolete: Zenit RK-3 o Magpul MOE AK Pistol Grip"),
            ("gs_2", "⚠️ IMPORTANTE: Plegar la culata (Clic central del ratón) antes de entregar para que ocupe 3x2 (6 celdas)."),
        ]
    },
    {
        "part": 3,
        "image_key": "gs_3",
        "title": "Gunsmith - Part 3 (MP5SD)",
        "weapon": "HK MP5 9x19 (Convertida a MP5SD)",
        "level": 7,
        "reqs": "Ergonomía ≥ 45  |  Retroceso ≤ 200  |  Alcance mira ≥ 200m  |  Cargador 50 tiros  |  Silenciador SD",
        "parts_detailed": [
            ("p_mp5sd_supp", "Conversión SD: Receptor superior MP5SD + Guardamanos polímero MP5SD + Silenciador MP5SD (Peacekeeper LL2)"),
            ("p_tl99", "Montura riel: HK MP5 B&T TL-99 Aluminum Handguard + Mira trasera de tambor"),
            ("p_ncstar_laser", "Láser: NcSTAR Tactical Blue Laser sobre el riel lateral B&T TL-99"),
            ("p_x5_drum", "Cargador de tambor: X Products X-5 MP5 50-round Drum Magazine (Mechanic LL2 trueque)"),
        ]
    },
    {
        "part": 4,
        "image_key": "gs_4",
        "title": "Gunsmith - Part 4 (OP-SKS)",
        "weapon": "Molot Arms Simonov OP-SKS 7.62x39",
        "level": 8,
        "reqs": "Ergonomía ≥ 35  |  Retroceso ≤ 350  |  Alcance mira ≥ 600m  |  Cargador 20+ tiros  |  Silenciada",
        "parts_detailed": [
            ("p_tapco_sks", "Chasis táctico: SKS TAPCO Intrafuse Stock System (Mechanic LL1) + Tubo + Culata MOE + Grip SAW"),
            ("p_hexagon_sks", "Silenciador: Hexagon SKS 7.62x39 Sound Suppressor (Skier LL2)"),
            ("p_pso1", "Montura y Óptica: Montura Dovetail OP-SKS + Mira BelOMO PSO-1M2-1 4x24 (Prapor LL2)"),
            ("p_promag_sks", "Cargador: ProMag SKS-A5 20-round Magazine (Peacekeeper LL2)"),
        ]
    },
    {
        "part": 5,
        "image_key": "gs_5",
        "title": "Gunsmith - Part 5 (Remington M870)",
        "weapon": "Remington Model 870 12ga",
        "level": 10,
        "reqs": "Ergonomía ≥ 60  |  Retroceso ≤ 500  |  Láser equipado",
        "parts_detailed": [
            ("p_m870_moe", "Guardamanos: M870 Magpul MOE Handguard (Mechanic LL1) + Riel M-LOK 4.1\""),
            ("p_rvg", "Empuñadura delantera: Magpul RVG Foregrip (Peacekeeper LL2)"),
            ("p_m870_sga", "Culata: M870 Magpul SGA Polymer Stock (Mechanic LL2)"),
            ("p_remington_choke", "Boquilla: Cañón de 508mm con mira fija + Remington Tactical Choke 12ga (Jaeger LL1)"),
            ("p_ncstar_laser", "Riel y Láser: Riel superior XS SHOTRAIL con Ghost Ring + Láser NcSTAR Blue"),
        ]
    },
    {
        "part": 6,
        "image_key": "gs_6",
        "title": "Gunsmith - Part 6 (AKM)",
        "weapon": "Kalashnikov AKM 7.62x39",
        "level": 12,
        "reqs": "Ergonomía ≥ 40  |  Retroceso ≤ 400  |  Alcance mira ≥ 800m  |  Silenciador equipado",
        "parts_detailed": [
            ("p_dtk4m", "Silenciador: Zenit DTK-4M 7.62x39 o Rotor 43"),
            ("p_moe_ak", "Guardamanos: Magpul MOE AK Handguard + Grip Magpul M-LOK AFG"),
            ("p_vudu", "Tapa y Óptica 800m: Tapa Bastion / PDC + Mira EOTech Vudu 1-6x24 o PSO"),
            ("p_gp25", "Culata: Culata de polímero AK-74M con cantonera de goma GP-25 (Prapor LL2)"),
            ("p_rk3", "Pistolete: Zenit RK-3 o US Palm AK Grip"),
        ]
    },
    {
        "part": 7,
        "image_key": "gs_7",
        "title": "Gunsmith - Part 7 (M4A1)",
        "weapon": "Colt M4A1 5.56x45",
        "level": 14,
        "reqs": "Ergonomía ≥ 47  |  Retroceso ≤ 300  |  Peso ≤ 3.8 kg  |  Cargador de 60 tiros  |  Silenciada",
        "parts_detailed": [
            ("p_mini_monster", "Silenciador: SureFire SOCOM556-MINI MONSTER sobre freno SF3P"),
            ("p_urx31", "Cañón y Guardamanos: Cañón 260mm + Bloque MK12 Low Profile + KAC URX 3.1 10.75\""),
            ("p_pmag_d60", "Cargador 60 tiros: Magpul PMAG D-60 5.56x45 60-round (Peacekeeper LL3) o STANAG 60"),
            ("p_moe_stock", "Culata: Magpul MOE Carbine Stock + Rubber Buttpad"),
        ]
    },
    {
        "part": 8,
        "image_key": "gs_8",
        "title": "Gunsmith - Part 8 (AKS-74N)",
        "weapon": "Kalashnikov AKS-74N 5.45x39",
        "level": 15,
        "reqs": "Ergonomía ≥ 65  |  Retroceso ≤ 275  |  10 Celdas máx  |  Piezas Zenit y Klesch-2P",
        "parts_detailed": [
            ("p_b10m", "Guardamanos y riel: Zenit B-10M + Zenit B-19 (Skier LL2)"),
            ("p_pt3", "Culata: Zenit PT-3 Klassika Stock + Adaptador PT-74S Lock"),
            ("p_rk3", "Pistolete y Grip: Zenit RK-3 Pistol Grip + Grip frontal Zenit RK-0"),
            ("p_dtk1", "Freno de boca: Zenit DTK-1 Muzzle Brake"),
            ("p_klesch2p", "Dispositivo táctico: Linterna/Láser Zenit Klesch-2P + Cargador AK-12 30 tiros"),
        ]
    },
    {
        "part": 9,
        "image_key": "gs_9",
        "title": "Gunsmith - Part 9 (P226R)",
        "weapon": "SIG Sauer P226R 9x19",
        "level": 17,
        "reqs": "Ergonomía ≥ 80  |  Corredera y cañón roscado Stainless Elite  |  Supresor y Láser",
        "parts_detailed": [
            ("p_p226_slide", "Corredera: P226 Stainless Elite Pistol Slide + Cañón roscado P226"),
            ("p_p226_grip", "Empuñadura: P226 Stainless Elite Wooden Pistol Grip"),
            ("p_micro_t1", "Montura y Óptica: Bridge Sight Mount + Mira punto rojo Aimpoint Micro T-1"),
            ("p_xc1", "Láser / Linterna: SureFire XC1 Tactical Flashlight"),
        ]
    },
    {
        "part": 10,
        "image_key": "gs_10",
        "title": "Gunsmith - Part 10 (AK-105)",
        "weapon": "Kalashnikov AK-105 5.45x39",
        "level": 18,
        "reqs": "Ergonomía ≥ 38  |  Retroceso ≤ 500  |  Alcance ≥ 800m  |  Cargador 60 tiros  |  8 Celdas máx (Plegada)",
        "parts_detailed": [
            ("p_pbs4", "Silenciador: PBS-4 5.45x39 Sound Suppressor o DTK-4M"),
            ("p_bastion", "Tapa con riel: AKademia Bastion Dust Cover + Mira con alcance 800m (Vudu / PS-320)"),
            ("p_6l31", "Cargador: 5.45x39 6L31 de 60 tiros"),
            ("p_gp25", "⚠️ IMPORTANTE: Plegar la culata para que ocupe 4x2 (8 celdas) antes de entregar a Mechanic."),
        ]
    },
    {
        "part": 11,
        "image_key": "gs_11",
        "title": "Gunsmith - Part 11 (Vector 9x19)",
        "weapon": "KRISS Vector Gen.2 9x19",
        "level": 20,
        "reqs": "Ergonomía ≥ 50  |  Retroceso ≤ 200  |  Silenciador Osprey 9  |  Grip Skeletonized  |  Cargador 33t",
        "parts_detailed": [
            ("p_osprey9", "Silenciador: SilencerCo Osprey 9 Sound Suppressor (Peacekeeper LL3)"),
            ("p_vector_rail", "Guardamanos: KRISS Vector Mk.5 Modular Rail (Skier LL3)"),
            ("p_skeleton_grip", "Empuñadura delantera: Tactical Dynamics Skeletonized Foregrip (Skier LL3)"),
            ("p_glock33", "Cargador extendido: Glock 9x19 33-round 'Big Stick' Magazine (Peacekeeper LL2)"),
            ("p_micro_t1", "Óptica táctica: Mira réflex compacta sobre riel superior"),
        ]
    },
    {
        "part": 12,
        "image_key": "gs_12",
        "title": "Gunsmith - Part 12 (AK-102)",
        "weapon": "Kalashnikov AK-102 5.56x45",
        "level": 23,
        "reqs": "Ergonomía ≥ 52  |  Retroceso ≤ 450  |  Alcance ≥ 500m  |  Silenciador Rotor 43  |  Linterna Klesch-2U",
        "parts_detailed": [
            ("p_rotor43", "Silenciador: Rotor 43 5.56x45 Sound Suppressor (Skier LL3)"),
            ("p_moe_ak", "Guardamanos: Magpul MOE AK Handguard + Magpul AFG tactical grip (FDE/Black)"),
            ("p_klesch2u", "Linterna táctica: Zenit 2U Klesch Tactical Flashlight"),
            ("p_ps320", "Óptica y Tapa: Tapa Bastion / PDC + Visor táctico Valday PS-320 1x/6x Scope"),
        ]
    },
    {
        "part": 13,
        "image_key": "gs_13",
        "title": "Gunsmith - Part 13 (SIG MPX)",
        "weapon": "SIG MPX 9x19",
        "level": 24,
        "reqs": "Ergonomía ≥ 52  |  Retroceso ≤ 180  |  Peso ≤ 4.0 kg  |  Boca Annihilator  |  Láser / Linterna",
        "parts_detailed": [
            ("p_mpx_rail", "Guardamanos: SIG MPX Midwest Industries 6.5\" M-LOK Rail"),
            ("p_annihilator", "Boca compensadora: Annihilator 9x19 Flash Hider (Peacekeeper LL2)"),
            ("p_skeleton_grip", "Grip: Fortis Shift vertical grip o Magpul RVG"),
            ("p_holosun", "Mira réflex: Holosun HS401G5 reflex sight (Peacekeeper LL2) con láser integrado"),
        ]
    },
    {
        "part": 14,
        "image_key": "gs_14",
        "title": "Gunsmith - Part 14 (HK 416A5)",
        "weapon": "HK 416A5 5.56x45",
        "level": 27,
        "reqs": "Ergonomía ≥ 60  |  Retroceso ≤ 250  |  Peso ≤ 4.0 kg  |  ¡TODAS las piezas en color FDE/TAN obligatorias!",
        "parts_detailed": [
            ("p_socom_rc2_tan", "Silenciador Tan: SureFire SOCOM556-RC2 Sound Suppressor (FDE / Tan) sobre freno SF3P"),
            ("p_rvg_fde", "Empuñadura delantera: Magpul RVG Tactical Foregrip (FDE / Tan)"),
            ("p_exps3_tan", "Óptica holográfica: EOTech EXPS3 Holographic Sight (Tan)"),
            ("p_ubr_fde", "Culata y Pistolete: Magpul UBR GEN2 Stock (FDE) + Pistolete Magpul MOE (FDE)"),
            ("p_peq15_tan", "Dispositivo láser: L3Harris LA-5B/PEQ Tactical Device (Tan)"),
            ("gs_14", "⚠️ IMPORTANTE: Vaciar completamente el cargador y la recámara para no sobrepasar los 4.0 kg."),
        ]
    },
    {
        "part": 15,
        "image_key": "gs_15",
        "title": "Gunsmith - Part 15 (AS VAL)",
        "weapon": "TsNIITochMash AS VAL 9x39",
        "level": 29,
        "reqs": "Ergonomía ≥ 42  |  Retroceso ≤ 200  |  Cargador 30 tiros  |  Montura y Óptica nocturna NSPU-M",
        "parts_detailed": [
            ("p_val_rotor", "Montura con rieles: Montura Rotor 43 AS VAL / VSS clamp mount + Grip Magpul RVG"),
            ("p_val_stock", "Culata: Tubo de amortiguador AS VAL + Culata Magpul CTR con cantonera Buttpad"),
            ("p_nspum", "Visor nocturno: Visor de visión nocturna NSPU-M 3.5x sobre riel lateral Dovetail"),
            ("p_val30", "Cargador 30 tiros: Cargador 9x39 6P30 30-round para AS VAL / VSS (Prapor LL3)"),
        ]
    },
    {
        "part": 16,
        "image_key": "gs_16",
        "title": "Gunsmith - Part 16 (DVL-10)",
        "weapon": "Lobaev Arms DVL-10 Urbana 7.62x51",
        "level": 30,
        "reqs": "Ergonomía ≥ 40  |  Retroceso ≤ 300  |  Peso ≤ 6.6 kg  |  Alcance mira ≥ 1000m  |  Silenciada",
        "parts_detailed": [
            ("p_dvl_barrel", "Cañón y Silenciador: Cañón DVL-10 660mm o Silenciador integrado DVL-10 Urbana"),
            ("p_schmidt", "Óptica 1000m: Mira Schmidt & Bender PM II 1-8x24 sobre anillas de 30mm"),
            ("p_ncstar_laser", "Dispositivo táctico: Módulo láser táctico NcSTAR Blue o AN/PEQ-15"),
        ]
    },
    {
        "part": 17,
        "image_key": "gs_17",
        "title": "Gunsmith - Part 17 (AK-102 Mod)",
        "weapon": "Kalashnikov AK-102 5.56x45",
        "level": 32,
        "reqs": "Ergonomía ≥ 58  |  Retroceso ≤ 380  |  Alcance ≥ 500m  |  Guardamanos Zenit B-30  |  Culata PT-3",
        "parts_detailed": [
            ("p_b30", "Guardamanos completo: Zenit B-30 con cubierta superior Zenit B-31C (Skier LL3)"),
            ("p_pt3", "Culata: Culata plegable Zenit PT-3 Klassika + Cerradura PT Lock"),
            ("p_rk2", "Grip y Freno: Zenit RK-2 Foregrip + Freno Zenit DTK-1 o Silenciador Rotor 43"),
            ("p_pdc", "Tapa y Óptica: Tapa con riel Texas Weapon Systems Dog Leg Rail Gen.3 + EOTech EXPS3"),
        ]
    },
    {
        "part": 18,
        "image_key": "gs_18",
        "title": "Gunsmith - Part 18 (AKMN)",
        "weapon": "Kalashnikov AKMN 7.62x39",
        "level": 33,
        "reqs": "Ergonomía ≥ 46  |  Retroceso ≤ 350  |  Silenciador PBS-1  |  Cargador PMAG 30  |  Rotor / Troy",
        "parts_detailed": [
            ("p_pbs1", "Silenciador: PBS-1 7.62x39 Sound Suppressor (Prapor LL3)"),
            ("p_moe_ak", "Guardamanos: Magpul MOE AK Handguard + Grip Magpul AFG Black"),
            ("p_pmag30", "Cargador: Magpul PMAG 30 AK/AKM 7.62x39 polymer magazine"),
            ("p_vudu", "Montura y Óptica: Montura Dovetail Axion Kobra + Mira óptica táctica 500m+"),
        ]
    },
    {
        "part": 19,
        "image_key": "gs_19",
        "title": "Gunsmith - Part 19 (SVDS)",
        "weapon": "Degtyarev SVDS 7.62x54R",
        "level": 35,
        "reqs": "Ergonomía ≥ 32  |  Retroceso ≤ 400  |  Chasis SAG SVDS MK.1  |  Silenciador SVDS Rotor 43",
        "parts_detailed": [
            ("p_sag_svds", "Chasis táctico: Chasis SAG SVDS MK.1 con guardamanos M-LOK de aluminio"),
            ("p_rotor_svds", "Silenciador: Rotor 43 7.62x54R Sound Suppressor (Skier LL3)"),
            ("p_rvg", "Grip frontal: Magpul RVG o Stark SE-5 Express"),
            ("p_march", "Óptica telescópica: Schmidt & Bender PM II 1-8x24 o March Tactical 3-24x42"),
        ]
    },
    {
        "part": 20,
        "image_key": "gs_20",
        "title": "Gunsmith - Part 20 (M1A SASS)",
        "weapon": "Springfield Armory M1A 7.62x51",
        "level": 36,
        "reqs": "Ergonomía ≥ 36  |  Retroceso ≤ 350  |  Chasis Troy S.A.S.S.  |  Silenciador Hybrid 46  |  Cargador 20t",
        "parts_detailed": [
            ("p_troy_sass", "Chasis: Troy M14 S.A.S.S. Stock System (Peacekeeper LL3)"),
            ("p_hybrid46", "Silenciador: SilencerCo Hybrid 46 Multi-caliber Suppressor sobre freno ASR"),
            ("p_m1a_20", "Cargador: Cargador Springfield M1A 20 tiros de acero"),
            ("p_hamr", "Óptica táctica: Leupold Mark 4 HAMR 4x24 con DeltaPoint superior (Peacekeeper LL3)"),
        ]
    },
    {
        "part": 21,
        "image_key": "gs_21",
        "title": "Gunsmith - Part 21 (Remington M700)",
        "weapon": "Remington Model 700 .308",
        "level": 37,
        "reqs": "Ergonomía ≥ 35  |  Retroceso ≤ 200  |  Chasis ProMag Archangel  |  Alcance ≥ 1000m  |  Silenciador",
        "parts_detailed": [
            ("p_archangel", "Chasis de francotirador: ProMag Archangel M700 Precision Stock (Jaeger LL3)"),
            ("p_ultra5", "Silenciador: Thunder Beast Ultra 5 Suppressor o SilencerCo Hybrid 46"),
            ("p_atacr", "Óptica 1000m+: Nightforce ATACR 7-35x56 o Schmidt & Bender PM II"),
            ("p_harris", "Bípode: Bípode Harris HBR montado en anclaje delantero"),
        ]
    },
    {
        "part": 22,
        "image_key": "gs_22",
        "title": "Gunsmith - Part 22 (M4A1 High-End)",
        "weapon": "Colt M4A1 5.56x45",
        "level": 38,
        "reqs": "Ergonomía ≥ 56  |  Retroceso ≤ 210  |  Guardamanos SAI QD Rail 14.5\"  |  Silenciador KAC NT-4",
        "parts_detailed": [
            ("p_sai_rail", "Guardamanos: SAI QD Rail 14.5\" M-LOK + Cañón 406mm (16\")"),
            ("p_kac_nt4", "Silenciador: KAC QD Muzzle Brake + Silenciador KAC NT-4 Black (Peacekeeper LL3)"),
            ("p_se5", "Empuñadura: Stark SE-5 Express Forward Grip"),
            ("p_razor", "Óptica de combate: Vortex Razor HD Gen.2 1-6x24 sobre montura Geissele Super Precision"),
            ("p_ctr", "Culata: Magpul CTR Carbine Stock + Rubber Buttpad"),
        ]
    },
    {
        "part": 23,
        "image_key": "gs_23",
        "title": "Gunsmith - Part 23 (Mk47 Mutant)",
        "weapon": "CMMG Mk47 Mutant 7.62x39",
        "level": 39,
        "reqs": "Ergonomía ≥ 52  |  Retroceso ≤ 230  |  Silenciador CMMG SV Brake + Suppressor  |  Cargador 30t",
        "parts_detailed": [
            ("p_cmmg_brake", "Boca y Silenciador: CMMG SV Brake + SilencerCo Saker ASR o Hybrid 46"),
            ("p_cmmg_rail", "Guardamanos: CMMG RML15 15\" M-LOK Handguard"),
            ("p_se5", "Grip frontal: Stark SE-5 Express o Magpul RVG"),
            ("p_moe_slk", "Culata y Tubo: Advanced Buffer Tube + Culata Magpul MOE SL-K"),
            ("p_pmag30", "Cargador: Magpul PMAG 30 AK/AKM 7.62x39"),
        ]
    },
    {
        "part": 24,
        "image_key": "gs_24",
        "title": "Gunsmith - Part 24 (KAC SR-25)",
        "weapon": "Knight's Armament Company SR-25 7.62x51",
        "level": 40,
        "reqs": "Ergonomía ≥ 42  |  Retroceso ≤ 240  |  Peso ≤ 5.8 kg  |  Silenciador KAC PRS QDC  |  Cargador 20t",
        "parts_detailed": [
            ("p_sr25_barrel", "Cañón y Guardamanos: Cañón 406mm SR-25 + Guardamanos KAC URX 4 M-LOK 14.5\""),
            ("p_kac_prs", "Silenciador: Freno KAC MAMS 7.62x51 + Silenciador KAC PRS QDC"),
            ("p_bcm_kag", "Grip frontal: BCM Gunfighter KAG o Magpul RVG"),
            ("p_sr25_mag", "Cargador: Cargador de acero KAC SR-25 20 tiros 7.62x51"),
            ("p_vudu", "Óptica de francotirador: EOTech Vudu 1-6x24 o Nightforce ATACR"),
        ]
    },
    {
        "part": 25,
        "image_key": "gs_25",
        "title": "Gunsmith - Part 25 (PKP Pecheneg)",
        "weapon": "Kalashnikov PKP Pecheneg 7.62x54R",
        "level": 42,
        "reqs": "Misión final de Mechanic: Ametralladora ligera PKP del Boss Kaban modificada con Zenit B-50 y Grip RK-2",
        "parts_detailed": [
            ("p_pkp_base", "Arma base legendaria: Ametralladora pesada PKP (Recompensa al abatir al Boss Kaban en el Concesionario Lexos de Streets of Tarkov)"),
            ("p_zenit_b50", "Montura con rieles: Riel y guardamanos táctico Zenit B-50 para PKP / PKM"),
            ("p_rk2", "Empuñadura delantera: Zenit RK-2 Heavy Vertical Foregrip (Skier LL4)"),
            ("p_exps3", "Óptica táctica: Mira holográfica EOTech EXPS3 o Holosun montada en riel Picatinny"),
            ("p_pkp_box", "Caja contenedora: Cinta de munición de 100 tiros 7.62x54R en caja metálica de transporte"),
        ]
    },
]


KAPPA_COLLECTOR_ITEMS: List[Dict[str, str]] = [
    {
        "name": "42 Signature Blend English Tea",
        "boss_or_spot": "Cajas de raciones, Villas de Shoreline y Campamento USEC",
        "icon_key": "kappa_42_signature_blend_english_tea",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/e6/EnglishTeaIcon.png/revision/latest?cb=20250110174041",
    },
    {
        "name": "Antique axe",
        "boss_or_spot": "Cuerpo a cuerpo en Scavs / Raiders y Cajas de Armas",
        "icon_key": "kappa_antique_axe",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/bc/Antique_Axe_icon.png/revision/latest?cb=20220421195230",
    },
    {
        "name": "Axel parrot figurine",
        "boss_or_spot": "Cajas Fuertes, Tiendas de lujo en Streets y Dorms",
        "icon_key": "kappa_axel_parrot_figurine",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/b3/Axel_parrot_icon.png/revision/latest?cb=20250109192410",
    },
    {
        "name": "BEAR Buddy plush toy",
        "boss_or_spot": "Estanterías, Cajas Fuertes y Bolsas de deporte",
        "icon_key": "kappa_bear_buddy_plush_toy",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/c/c2/Buddy_icon.png/revision/latest?cb=20250110174202",
    },
    {
        "name": "Baddie's red beard",
        "boss_or_spot": "Scavs, Chaquetas, Maniquíes y Bolsas de deporte",
        "icon_key": "kappa_baddie_s_red_beard",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/21/Baddie_icon.png/revision/latest?cb=20220706012932",
    },
    {
        "name": "BakeEzy cook book",
        "boss_or_spot": "Archivadores, Cajas Fuertes y Cocinas de Streets/Reserve",
        "icon_key": "kappa_bakeezy_cook_book",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/d2/BakeEzy_Cook_Book_icon.png/revision/latest?cb=20220704161413",
    },
    {
        "name": "Battered antique book",
        "boss_or_spot": "Archivadores, Cajas Fuertes y Estanterías de Dorms / Streets",
        "icon_key": "kappa_battered_antique_book",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/6/63/BatteredBookIcon.png/revision/latest?cb=20250109192447",
    },
    {
        "name": "Bottle of YMXC water",
        "boss_or_spot": "Cajas de raciones, Goshan y Alijo de Woods",
        "icon_key": "kappa_bottle_of_ymxc_water",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/18/Bottle_of_YMXC_water_icon.png/revision/latest?cb=20260825151948",
    },
    {
        "name": "Can of Dr. Lupo's coffee beans",
        "boss_or_spot": "Cajas de suministros de ración y cocinas de Streets / Woods",
        "icon_key": "kappa_can_of_dr_lupo_s_coffee_beans",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/e8/Lupo_Icon.png/revision/latest?cb=20260126004308",
    },
    {
        "name": "Can of GigaBeef meat",
        "boss_or_spot": "Cajas de raciones, Goshan (Interchange) y Shturman's Stash",
        "icon_key": "kappa_can_of_gigabeef_meat",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/ae/Can_of_GigaBeef_meat_icon.png/revision/latest?cb=20260825152001",
    },
    {
        "name": "Can of RatCola soda",
        "boss_or_spot": "Cajas de raciones, Goshan y Máquinas expendedoras",
        "icon_key": "kappa_can_of_ratcola_soda",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/4b/RatCola_Icon.png/revision/latest?cb=20250117123752",
    },
    {
        "name": "Deadlyslob's beard oil",
        "boss_or_spot": "Oficinas de Interchange (Power Station / IDEA) y Streets",
        "icon_key": "kappa_deadlyslob_s_beard_oil",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/6/6b/Deadlyslobs_beard_oil_icon.png/revision/latest?cb=20250308190103",
    },
    {
        "name": "DesmondPilak CD",
        "boss_or_spot": "Estantes técnicos, Tiendas de electrónica y PCs",
        "icon_key": "kappa_desmondpilak_cd",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/5/55/DesmondPilak_CD_icon.png/revision/latest?cb=20260526155950",
    },
    {
        "name": "Domontovich ushanka hat",
        "boss_or_spot": "Scavs, Cajas de ropa y Bolsas de deporte",
        "icon_key": "kappa_domontovich_ushanka_hat",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/37/Domontovich_ushanka_hat_icon.png/revision/latest?cb=20260210145545",
    },
    {
        "name": "DRD body armor",
        "boss_or_spot": "Scavs, Cajas de armas y Alijos ocultos (Hidden Stashes)",
        "icon_key": "kappa_drd_body_armor",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/22/DRD_body_armor.png/revision/latest?cb=20240103163643",
    },
    {
        "name": "Dunduk floppy disk",
        "boss_or_spot": "PCs, Archivadores y Oficinas técnicas en Labs / Streets",
        "icon_key": "kappa_dunduk_floppy_disk",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/04/Dunduk_floppy_disk_icon.png/revision/latest?cb=20260526160824",
    },
    {
        "name": "Fake mustache",
        "boss_or_spot": "Scavs, Chaquetas y Bolsas de deporte",
        "icon_key": "kappa_fake_mustache",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/72/Fake_Mustache_icon.png/revision/latest?cb=20190319185801",
    },
    {
        "name": "FireKlean gun lube",
        "boss_or_spot": "Mesas de trabajo en Labs, Streets y Scav Case (Moonshine)",
        "icon_key": "kappa_fireklean_gun_lube",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/09/FireKlean_icon.png/revision/latest?cb=20250313193047",
    },
    {
        "name": "French bakery baguette",
        "boss_or_spot": "Mesas de cafeterías en Streets, Interchange y Cajas de raciones",
        "icon_key": "kappa_french_bakery_baguette",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/dc/French_bakery_baguette_icon.png/revision/latest?cb=20260825152033",
    },
    {
        "name": "Gingy keychain",
        "boss_or_spot": "Habitaciones Marcadas y bolsillos de Scavs",
        "icon_key": "kappa_gingy_keychain",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/b7/Gingy-keychain-icon.png/revision/latest?cb=20250107081049",
    },
    {
        "name": "Glorious E mask",
        "boss_or_spot": "Cajas de armas grandes, Raiders y Kaban's Guards",
        "icon_key": "kappa_glorious_e_mask",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/af/Glori_mask.png/revision/latest?cb=20260908171812",
    },
    {
        "name": "Golden 1GPhone smartphone",
        "boss_or_spot": "Tiendas Techlight, Texho y Rasmussen (Interchange)",
        "icon_key": "kappa_golden_1gphone_smartphone",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/fe/1gphone_icon.png/revision/latest?cb=20250126235525",
    },
    {
        "name": "Golden egg",
        "boss_or_spot": "Cajas Fuertes, Resort de Shoreline y Habitaciones Marcadas",
        "icon_key": "kappa_golden_egg",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/f2/Golden_egg_icon.png/revision/latest?cb=20250109195802",
    },
    {
        "name": "Inseq gas pipe wrench",
        "boss_or_spot": "Cajas de herramientas (Toolboxes) y Almacenes técnicos",
        "icon_key": "kappa_inseq_gas_pipe_wrench",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/b2/Inseq_icon.png/revision/latest?cb=20250907201911",
    },
    {
        "name": "JohnB Liquid DNB glasses",
        "boss_or_spot": "Scavs, Chaquetas y Cajas de suministros",
        "icon_key": "kappa_johnb_liquid_dnb_glasses",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/e6/JohnB_icon.png/revision/latest?cb=20230711185232",
    },
    {
        "name": "LM KC-130 model aircraft",
        "boss_or_spot": "Cajas Fuertes, Escritorios ejecutivos y Resort",
        "icon_key": "kappa_lm_kc_130_model_aircraft",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/bf/LM_KC-130_model_aircraft_icon.png/revision/latest?cb=20260825152055",
    },
    {
        "name": "Loot Lord plushie",
        "boss_or_spot": "Cajas Fuertes, Estanterías de lujo y Streets",
        "icon_key": "kappa_loot_lord_plushie",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/3c/Loot_Lord_plushie_icon.png/revision/latest?cb=20250109195949",
    },
    {
        "name": "LVNDMARK's rat poison",
        "boss_or_spot": "Bolsas médicas, Cajas técnicas y Streets of Tarkov",
        "icon_key": "kappa_lvndmark_s_rat_poison",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/1c/Lvndmark_rat_poison_icon.png/revision/latest?cb=20211207021843",
    },
    {
        "name": "Mazoni golden dumbbell",
        "boss_or_spot": "Gimnasios, Bolsas de deporte y Resort de Shoreline",
        "icon_key": "kappa_mazoni_golden_dumbbell",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/5/5c/Mazoni_golden_dumbbell_icon.png/revision/latest?cb=20251224172957",
    },
    {
        "name": "Missam forklift key",
        "boss_or_spot": "Chaquetas, Archivadores y Bolsas de deporte",
        "icon_key": "kappa_missam_forklift_key",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/b8/Missamkey.png/revision/latest?cb=20250318223231",
    },
    {
        "name": "Nut Sack balaclava",
        "boss_or_spot": "Scavs, Chaquetas y Cajas de ropa",
        "icon_key": "kappa_nut_sack_balaclava",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/e6/Nut_Sack_balaclava_icon.png/revision/latest?cb=20251224172422",
    },
    {
        "name": "Pestily plague mask",
        "boss_or_spot": "Cultistas, Scavs de noche y Scav Case (Moonshine)",
        "icon_key": "kappa_pestily_plague_mask",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/9/9b/Plague_mask_icon.png/revision/latest?cb=20250906224230",
    },
    {
        "name": "Press pass (issued for NoiceGuy)",
        "boss_or_spot": "Archivadores, Cajas Fuertes y Oficinas de Streets",
        "icon_key": "kappa_press_pass_issued_for_noiceguy",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/9/91/NoiceguyPass_Icon.png/revision/latest?cb=20250110174616",
    },
    {
        "name": "Raven figurine",
        "boss_or_spot": "Cajas Fuertes, Resort de Shoreline y Chekannaya 15",
        "icon_key": "kappa_raven_figurine",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/c/c0/Raven_figurine_icon.png/revision/latest?cb=20250109200058",
    },
    {
        "name": "SheefGG piggy bank",
        "boss_or_spot": "Cajas Fuertes, Escritorios y Alijos ocultos",
        "icon_key": "kappa_sheefgg_piggy_bank",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/5/55/SheefGG_piggy_bank_icon.png/revision/latest?cb=20260526161647",
    },
    {
        "name": "Shroud half-mask",
        "boss_or_spot": "Scavs, Chaquetas y Bolsas de deporte",
        "icon_key": "kappa_shroud_half_mask",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/8/81/Shroud_Icon.png/revision/latest?cb=20260909212827",
    },
    {
        "name": "Silver Badge",
        "boss_or_spot": "Cajas Fuertes, Habitaciones Marcadas y Shturman's Stash",
        "icon_key": "kappa_silver_badge",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/41/Silver_Badge_icon.png/revision/latest?cb=20250109200250",
    },
    {
        "name": "Smoke balaclava",
        "boss_or_spot": "Scavs, Rogues y Bolsas de deporte",
        "icon_key": "kappa_smoke_balaclava",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/45/Smoke_icon.png/revision/latest?cb=20241013180039",
    },
    {
        "name": "Tamatthi kunai knife replica",
        "boss_or_spot": "Cajas de armas, Habitaciones Marcadas y Cultistas",
        "icon_key": "kappa_tamatthi_kunai_knife_replica",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/be/Kunai_icon.png/revision/latest?cb=20250907201929",
    },
    {
        "name": "Tigzresq splint",
        "boss_or_spot": "Bolsas médicas, Cajas de suministros médicos y Resort",
        "icon_key": "kappa_tigzresq_splint",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/0e/Tigzresq_splint_icon.png/revision/latest?cb=20261103152533",
    },
    {
        "name": "Veritas guitar pick",
        "boss_or_spot": "Cajas Fuertes, Chaquetas y Habitaciones de lujo",
        "icon_key": "kappa_veritas_guitar_pick",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/ae/VeritasGuitarPickIcon.png/revision/latest?cb=20250109200429",
    },
    {
        "name": "Video cassette with the Cyborg Killer movie",
        "boss_or_spot": "Cajas Fuertes, Dorms y Mesas de Streets",
        "icon_key": "kappa_video_cassette_with_the_cyborg_killer_movie",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a5/Video_cassette_with_the_Cyborg_Killer_movie_icon.png/revision/latest?cb=20240310014051",
    },
    {
        "name": "Viibiin sneaker",
        "boss_or_spot": "Bolsas de deporte, Tiendas de Interchange y Streets",
        "icon_key": "kappa_viibiin_sneaker",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/b3/ViibiinSneaker_Icon.png/revision/latest?cb=20250827234545",
    },
    {
        "name": "WZ Wallet",
        "boss_or_spot": "Habitaciones Marcadas (Dorms 314, RB-BK, Chekannaya)",
        "icon_key": "kappa_wz_wallet",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/b2/WZ_Wallet_icon.png/revision/latest?cb=20250131152839",
    },
]
