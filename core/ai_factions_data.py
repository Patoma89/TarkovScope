"""
TarkovScope - Datos Puros de Facciones Hostiles de IA (Rogues, Raiders, Cultists, Black Division, RUAF, Scavs)
Fuente: Escape from Tarkov Wiki. Cero dependencias de UI / Tkinter.
"""
from typing import Any, Dict, List


AI_FACTIONS_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "faction_rogues",
        "name": "Rogues (Ex-USEC)",
        "subtitle_es": "Operadores renegados de la Planta de Tratamiento de Agua",
        "subtitle_en": "Renegade ex-USEC operators guarding Water Treatment Plant",
        "danger_level": "EXTREMO (Rango >300m con ametralladoras fijas)",
        "maps": ["Lighthouse"],
        "aggro_rules_es": (
            "• BEAR: Hostiles inmediatamente a larga distancia (>250-300m).\n"
            "• USEC: Tolerantes si no entras a los edificios ni disparas; si matas o te acercas a un Rogue, "
            "quedan hostiles hacia ti durante las próximas 3 raids.\n"
            "• Scavs Jugadores: Tolerantes fuera del perímetro de los edificios/techos hasta que entras al patio interior."
        ),
        "aggro_rules_en": (
            "• BEAR: Immediately hostile at long range (>250-300m).\n"
            "• USEC: Neutral unless you trespass inside the plant or attack them; killing a Rogue marks you hostile for 3 raids.\n"
            "• Player Scavs: Neutral outside building interiors unless provoked."
        ),
        "spawn_triggers_es": (
            "Spawnean al inicio de cada raid en las torres frontales, techos de los Edificios 1, 2 y 3, "
            "y patrullan el patio central (helicóptero). Pueden aparecer refuerzos en el patio."
        ),
        "spawn_triggers_en": (
            "Spawn at raid start on front guard towers, roofs of Buildings 1, 2, and 3, plus ground patrols "
            "around the helicopter courtyard."
        ),
        "top_loot": [
            "Armas M4A1 / SCAR-L / SR-25 / AK-104 modificadas con ópticas LPVO/EOTech",
            "Munición M855A1, M856A1, BP 7.62x39 y M80",
            "Chalecos Hexatac / Plate Carriers Clase 4-5 y mochilas grandes",
            "Llaves de Lighthouse e ítems electrónicos militares en los almacenes",
        ],
        "farming_guide_steps_es": [
            "1. Acércate por el flanco ESTE (montañas sobre la carretera) o de noche (su rango visual cae drásticamente tras 22:00).",
            "2. Limpia primero las dos torretas frontales (AGS-30 y NSV) desde >150m con mira 4x-6x.",
            "3. Rodea por detrás del Edificio 3 (Este) y limpia los techos del Edificio 3 y Edificio 2 antes de bajar.",
            "4. Entra al Edificio 2 o 1 por puerta lateral haciendo 'slow lean' (Alt+A/D o peek derecho): nunca repeekes el mismo ángulo dos veces.",
            "5. Revisa el patio central antes de lootear el techo del Edificio 1 para no ser snipeado desde las montañas.",
        ],
        "farming_guide_steps_en": [
            "1. Approach via the EAST hillside overlooking the plant, or raid at night (after 22:00 their aggro range drops sharply).",
            "2. Snipe the two front mounted gunners (AGS-30 & NSV) first from 150m+ using a 4x-6x scope.",
            "3. Rotate behind Building 3 (East) and clear Building 3 & Building 2 roofs before pushing inside.",
            "4. Clear ground Rogues inside buildings using right-hand peeks; never re-peek the exact same angle.",
            "5. Verify the central courtyard is clear before looting Building 1 roof.",
        ],
    },
    {
        "id": "faction_raiders",
        "name": "Scav Raiders",
        "subtitle_es": "Ex-operadores PMC & mercenarios tácticos en Reserve y The Lab",
        "subtitle_en": "Tactical ex-PMC mercenaries on Reserve and The Lab",
        "danger_level": "ALTO (Granadas precisas y ráfagas láser)",
        "maps": ["Reserve", "The Lab"],
        "aggro_rules_es": (
            "• Hostiles contra TODOS los PMCs.\n"
            "• Con Scavs Jugadores: primero dan una advertencia verbal y gestos; si te acercas demasiado o apuntas, disparan.\n"
            "• Usan granadas VOG/F-1 muy precisas y se mueven en escuadrones de 3 a 4 unidades."
        ),
        "aggro_rules_en": (
            "• Hostile to all PMCs on sight.\n"
            "• Player Scavs: issue a verbal warning first, then engage if you linger too close or aim at them.\n"
            "• Throw accurate grenades and push in squads of 3-4."
        ),
        "spawn_triggers_es": (
            "• Reserve: (1) Al activar la palanca de Hermetic Door Bunker, (2) Al activar D-2 Power en el subsuelo, "
            "(3) Al llegar el Tren Blindado (~35% prob).\n"
            "• The Lab: Al activar las compuertas (Parking Gate, Hangar Gate), ascensores (Medical/Cargo) o botones de extracción."
        ),
        "spawn_triggers_en": (
            "• Reserve: (1) Hermetic Door bunker switch, (2) Underground D-2 Power switch, (3) Armored Train arrival.\n"
            "• The Lab: Triggered by activating Parking/Hangar gates or Medical/Cargo extraction elevators."
        ),
        "top_loot": [
            "Cascos Bastion/ULACH/Airframe y placas Clase 4-5 (Korund / TV-110 / Ana Tactical)",
            "Rifles AK-105, MPX, HK 416A5, MDR, SR-25 y munición 5.45 BT/BP, 9x19 AP 6.3, 5.56 M856A1",
            "Granadas VOG-25, M67 y botiquines IFAK/AFAK",
        ],
        "farming_guide_steps_es": [
            "1. En Reserve, activa la palanca del bunker subterráneo (D-2) y espera detrás de una puerta cerrada.",
            "2. Atrae a los Raiders haciendo ruido o lanzando una granada; al abrir la puerta son vulnerables durante la animación.",
            "3. En The Lab, activa el botón de Hangar o Parking y quédate en posición elevada o pasillo cerrado con cobertura sólida.",
            "4. Nunca te quedes quieto si gritan 'Granata!': muévete de cobertura al instante.",
        ],
        "farming_guide_steps_en": [
            "1. On Reserve, flip the underground D-2 power switch and hold behind a closed metal door.",
            "2. Bait Raiders with gunfire/grenades; eliminate them as they breach doors.",
            "3. On The Lab, activate Hangar or Parking Gate and hold hard cover angles from above or closed hallways.",
            "4. Always reposition immediately when they call out a grenade.",
        ],
    },
    {
        "id": "faction_cultists",
        "name": "Cultists (Sectarians)",
        "subtitle_es": "Secta nocturna silenciosa (Zhrec + Sektants) con cuchillos envenenados",
        "subtitle_en": "Silent nocturnal sect (Priest + Warriors) wielding poisoned blades",
        "danger_level": "CRÍTICO (Sin sonido de pasos, invisibles en térmica y veneno)",
        "maps": ["Customs", "Woods", "Shoreline", "Factory (Night)"],
        "aggro_rules_es": (
            "• Ventana horaria ESTRICTA: solo aparecen entre las 22:00 y las 07:00.\n"
            "• Sus pasos son casi 100% silenciosos y NO brillan intensamente en miras térmicas (T-7 / REAP-IR / FLIR).\n"
            "• Suelen ocultarse tumbados en arbustos; intentan apuñalarte por la espalda con veneno mortal (Unknown Toxin)."
        ),
        "aggro_rules_en": (
            "• STRICT Time Window: only spawn between 22:00 and 07:00.\n"
            "• Nearly silent footsteps and cold body signature on thermal scopes.\n"
            "• Ambush from prone bush positions using poisoned knives (Unknown Toxin)."
        ),
        "spawn_triggers_es": (
            "• Customs: Alrededor de Stronghold (Fortress), Crackhouse y Mechanic garage.\n"
            "• Woods: Cerca de los dos Círculos Marcados (Sunken Village y Sawmill/Cultist Circle).\n"
            "• Shoreline: Espina central (Spine), Resort patio y Swamp village.\n"
            "• Factory (Noche): Baja probabilidad (~2-10%) entre contenedores y oficinas."
        ),
        "spawn_triggers_en": (
            "• Customs: Fortress / Stronghold & Crackhouse area.\n"
            "• Woods: Marked Circle near Sunken Village & Woods Marked Circle.\n"
            "• Shoreline: Central Spine, Health Resort yard & Swamp.\n"
            "• Night Factory: Low chance across main floor & tunnels."
        ),
        "top_loot": [
            "Llaves Marked (Dorm Room 314, RB-BK, Mysterious Room) y tarjetas Lab (Black/Yellow/Green/Red)",
            "Munición meta: 7.62x39 BP, 9x39 BP/SP-6, 7.62x54R SNB/BS, 5.45 Igolnik",
            "Armaduras Hexgrid / Slick / Zhuk-6a y el Cultist Knife (requerido por Peacekeeper/Lightkeeper)",
        ],
        "farming_guide_steps_es": [
            "1. Lleva SIEMPRE un antídoto xTG-12 o Augmentin en el Injector Case antes de entrar de noche.",
            "2. Usa NVG (GPNVG-18 o PNV-10T) y linterna para comprobar arbustos sospechosos.",
            "3. El Priest (Zhrec) no suele apuñalar sino disparar en ráfagas; sus guerreros (Sektants) corren a apuñalar si te acercas.",
            "4. En Customs, lánzales una granada hacia Stronghold o dispara desde ventanas de Crackhouse: si están vivos te devolverán fuego o correrán hacia una esquina.",
        ],
        "farming_guide_steps_en": [
            "1. ALWAYS pack an xTG-12 antidote or Augmentin in your Injector Case for night raids.",
            "2. Use NVGs + tactical flashlight to spot prone figures inside dark bushes.",
            "3. Once spotted, hold a doorway inside Crackhouse/Fortress and let the knife-rushers funnel into you.",
            "4. Probe Fortress/Marked areas with a grenade to force movement.",
        ],
    },
    {
        "id": "faction_black_division",
        "name": "Black Division (TerraGroup Spec-Ops)",
        "subtitle_es": "Fuerza especial secreta de TerraGroup (790 HP · Bolsillos de 24 celdas)",
        "subtitle_en": "TerraGroup's covert special operations force (790 HP · 24-slot pockets)",
        "danger_level": "EXTREMO (790 HP y munición M993 / M995 / SSA AP)",
        "maps": ["The Lab", "Terminal", "Icebreaker", "Ground Zero (Nv.21+)", "Streets of Tarkov", "Shoreline", "Woods"],
        "aggro_rules_es": (
            "• Fuerza de operaciones especiales interna de TerraGroup: hostiles al instante y ultra agresivos.\n"
            "• Salud oficial: 790 HP totales (Cabeza: 40, Tórax: 170, Estómago: 140, Brazos: 110 c/u, Piernas: 110 c/u).\n"
            "• Cuentan con bolsillos especiales de 24 espacios totales (3x 2x3 + 2x 1x3, idénticos a Kaban).\n"
            "• Matarlos como Scav Jugador NO conlleva penalización de Scav Karma."
        ),
        "aggro_rules_en": (
            "• TerraGroup internal spec-ops unit: instantly hostile and highly tactical.\n"
            "• Official Health Pool: 790 total HP (Head: 40, Thorax: 170, Stomach: 140, Arms: 110 each, Legs: 110 each).\n"
            "• Carry 24-slot mega pockets (3x 2x3 + 2x 1x3, same layout as Kaban).\n"
            "• Killing Black Division operatives as a Player Scav causes ZERO Scav Karma penalty."
        ),
        "spawn_triggers_es": (
            "Spawns permanentes en The Lab, Terminal e Icebreaker, y patrullas de temporada/rotación "
            "en Ground Zero (Nv.21+), Shoreline, Streets of Tarkov y Woods."
        ),
        "spawn_triggers_en": (
            "Permanently present in The Lab, Terminal, and Icebreaker; seasonal roaming patrols on "
            "Ground Zero (Lv.21+), Shoreline, Streets of Tarkov, and Woods."
        ),
        "top_loot": [
            "Rifles 7.62x51 (MDR, SCAR-H, SR-25, RSASS, M1A, M60E6) cargados con M993 y M80",
            "Rifles 5.56x45 (HK 416A5, M4A1, SCAR-L, Howa Type 20, AUG A3) con M995 / SSA AP",
            "Subfusiles MP9-N / MP5 / MPX con AP 6.3 y chalecos/placas de máximo nivel",
            "Bolsillos de 24 slots repletos de cargadores extra, granadas e ítems de alto valor",
        ],
        "farming_guide_steps_es": [
            "1. Nunca subestimes su HP de cabeza/tórax (40/170 HP): usa munición de alto daño o ráfagas precisas a la cara.",
            "2. En The Lab y pasillos estrechos, atráelos a puertas cerradas para anular su fuego cruzado de escuadra.",
            "3. Evita quedarte en ángulo abierto contra rifles MDR/SCAR-H cargados con M993 (perforan Clase 6).",
            "4. Al lootearlos, recuerda revisar sus 5 bolsillos enormes de 24 slots totales.",
        ],
        "farming_guide_steps_en": [
            "1. Respect their 40 Head / 170 Thorax HP pool: land clean headshots or sustained AP bursts.",
            "2. In The Lab corridors, hold closed doorways to break their squad crossfire.",
            "3. Never wide-peek their 7.62x51 M993 rifles (they shred Class 6 plates).",
            "4. Remember to search all 5 oversized pocket slots (24 total cells).",
        ],
    },
    {
        "id": "faction_ruaf_pmc",
        "name": "RUAF ('AF') & PMCs IA (PvE)",
        "subtitle_es": "Fuerzas Armadas Rusas del cordón de Terminal (675 HP) & Escuadras PMC PvE",
        "subtitle_en": "Russian Armed Forces at Terminal blockade (675 HP) & PvE AI PMC squads",
        "danger_level": "ALTO (Neutrales en Shoreline salvo provocación · Escuadras con munición AP)",
        "maps": ["Shoreline", "Terminal", "Customs", "Woods", "Interchange", "Lighthouse", "Reserve", "Streets of Tarkov", "Factory", "Ground Zero"],
        "aggro_rules_es": (
            "• RUAF ('AF'): 675 HP totales (Cabeza: 35, Tórax: 120, Estómago: 120, Brazos/Piernas: 100 c/u).\n"
            "  - En Shoreline custodian el puerto Terminal: son neutrales salvo que les dispares o te acerques sin acceso.\n"
            "  - En Terminal son ALIADOS del jugador frente a Scavs y Black Division (salvo fuego amigo). Matarlos como Scav no quita Karma.\n"
            "• PMCs IA (USEC / BEAR en PvE): Patrullan en grupos de 1 a 4 operadores hacia POIs y extracciones; atacan a tu PMC y a Scavs."
        ),
        "aggro_rules_en": (
            "• RUAF ('AF'): 675 total HP (Head: 35, Thorax: 120, Stomach: 120, Limbs: 100 each).\n"
            "  - On Shoreline they guard Terminal port (neutral unless fired upon or trespassing without intercom access).\n"
            "  - Inside Terminal they are FRIENDLY allies fighting Scavs & Black Division unless provoked. Zero Scav Karma loss.\n"
            "• AI PMCs (USEC / BEAR in PvE): Squads of 1-4 operators rotating between POIs and extracts."
        ),
        "spawn_triggers_es": (
            "• RUAF: Guarnición del puerto Terminal en Shoreline y en toda la zona de Terminal.\n"
            "• PMCs IA: Spawns dinámicos en puntos clásicos de PMC en todos los mapas PvE desde el segundo 0."
        ),
        "spawn_triggers_en": (
            "• RUAF: Terminal port garrison on Shoreline and across Terminal.\n"
            "• AI PMCs: Classic PMC spawn points across all PvE maps at raid start."
        ),
        "top_loot": [
            "RUAF: Equipamiento militar ruso, lanzagranadas, AK-74M / AK-12 y armaduras reglamentarias",
            "PMCs IA: Dogtags USEC/BEAR (necesarias para quests como Punisher / Friend from the West)",
            "Rifles modificados, miras holográficas/telescópicas, botiquines AFAK y placas Clase 4-5",
        ],
        "farming_guide_steps_es": [
            "1. En Shoreline junto al puerto Terminal, no apuntes ni te acerques a la puerta sin presentar el ítem de acceso en el intercomunicador.",
            "2. En PvE, para farmear kills de PMC rápidas (Punisher / Setup / Shooter Born), corre hacia zonas de loot de alto tráfico (Dorms, Resort, LexOs, Sawmill).",
            "3. Cuando mates a un PMC IA, espera 5 segundos antes de lootear por si su compañero de escuadra viene a cubrirlo.",
        ],
        "farming_guide_steps_en": [
            "1. Near Shoreline's Terminal gate, present the access item at the intercom rather than trespassing.",
            "2. In PvE, rush high-traffic POIs (Dorms, Resort, LexOs, Sawmill) for fast AI PMC dogtag/quest kills.",
            "3. Wait a few seconds after dropping one AI PMC in case a squadmate flanks you.",
        ],
    },
    {
        "id": "faction_scavs_snipers",
        "name": "Scavs & Sniper Scavs",
        "subtitle_es": "Habitantes armados locales y tiradores en techos/rocas",
        "subtitle_en": "Local armed scavengers and elevated rooftop/cliff snipers",
        "danger_level": "BAJO–MEDIO (Peligro en extremidades / cabeza si se ignoran)",
        "maps": ["Customs", "Woods", "Shoreline", "Streets", "Lighthouse", "Interchange", "Ground Zero", "Factory", "Reserve"],
        "aggro_rules_es": (
            "• Hostiles contra PMCs.\n"
            "• Neutrales hacia Player Scavs mientras tu Scav Karma sea >= -5.0 (salvo que dispares a un Scav o Boss).\n"
            "• Los Sniper Scavs dominan puntos altos y pueden disparar a >180m con SKS/SVD/Mosin."
        ),
        "aggro_rules_en": (
            "• Hostile to PMCs.\n"
            "• Friendly to Player Scavs unless karma < -5.0 or you shoot a Scav/Boss.\n"
            "• Sniper Scavs guard rooftops/cliffs with SKS/Mosin/SVD rifles up to 180m+."
        ),
        "spawn_triggers_es": (
            "• Customs Sniper Scavs: Checkpoint tower, Power Warehouse roof, Construction silo, Old Construction.\n"
            "• Woods: Sniper Rock (Mountain Stash).\n"
            "• Shoreline: Hydroelectric Power roof & Rock Passage bunker.\n"
            "• Streets: Múltiples balcones/techos alrededor de Klimov & Concordia."
        ),
        "spawn_triggers_en": (
            "• Customs: Checkpoint tower, Power roof, Silo, Old Construction.\n"
            "• Woods: Sniper Rock (Mountain Stash).\n"
            "• Shoreline: Power Station roof & Northern bunker rocks.\n"
            "• Streets: Balconies along Klimov St & Concordia."
        ),
        "top_loot": [
            "Llaves de quests, ítems FiR de Hideout, comida y placas Clase 2-4 en mochilas",
            "Tarjetas de Acceso Labs (spawnean ocasionalmente en bolsillos de Scavs)",
            "Mochilas Pilgrim / Berkut y chalecos Scav Vest",
        ],
        "farming_guide_steps_es": [
            "1. Si juegas como Player Scav, revisa SIEMPRE bolsillos y mochilas de Scavs muertos (nunca los mates si tienes Karma positivo).",
            "2. En raids nocturnas o abiertas, chequea los techos clásicos de Sniper Scav antes de cruzar calles.",
            "3. Usa extracciones Co-Op (PMC + Scav) para ganar +0.25 Scav Karma y un paquete de loot de Fence.",
        ],
        "farming_guide_steps_en": [
            "1. Always loot pockets and backpacks of dead Scavs (Labs keycards & quest keys spawn there).",
            "2. Check known Sniper Scav roofs before crossing open streets.",
            "3. Use Co-Op extracts (PMC + Scav) for +0.25 Karma and a Fence gift package.",
        ],
    },
]
