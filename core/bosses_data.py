"""
TarkovScope - Base de Conocimiento Exhaustiva de Bosses de Escape from Tarkov
Información oficial sincronizada con https://eftboss.com/pve (y modo PvP Regular):
salud, armas, guardias, probabilidades exactas de spawn por mapa y por zona,
coordenadas calibradas visualmente (x, y) sobre cada plano 2D real de cache/maps/ y tácticas.
Incluye Reshala, Killa, Tagilla, Shturman, Glukhar, Sanitar, Kaban, Kollontay,
The Goons, Partisan, Zryachiy, Cultistas (Cultist Priest) y The Wedge (Black Division).
"""
import requests
from typing import List, Dict, Any, Tuple

BOSSES_DATA: List[Dict[str, Any]] = [
    {
        "id": "reshala",
        "name": "Reshala (The Dealmaker)",
        "russian_name": "Решала",
        "maps": ["Customs"],
        "spawn_chance": "75% (PvE)  |  60% (PvP)",
        "pve_chance": "75%",
        "pvp_chance": "60%",
        "map_spawn_chances": {
            "Customs": {"pve": "75%", "pvp": "60%"}
        },
        "map_spawns": {
            "Customs": [
                {"zone": "Dormitorios de 2 y 3 pisos (Dorms) [33%]", "details": "Probabilidad de zona: 33% — Habitaciones del 1er y 2do piso; se atrinchera con sus guardias.", "x": 0.47, "y": 0.72, "chance": "33%"},
                {"zone": "Nueva Estación de Gasolina (New Gas) [33%]", "details": "Probabilidad de zona: 33% — Interior de la tienda o detrás de los tanques de combustible.", "x": 0.58, "y": 0.52, "chance": "33%"},
                {"zone": "Fortaleza / Stronghold (ZB-013) [33%]", "details": "Probabilidad de zona: 33% — Piso intermedio con vistas a la zona de construcción militar.", "x": 0.48, "y": 0.38, "chance": "33%"}
            ]
        },
        "total_hp": 752,
        "hp_breakdown": {
            "Head": 62, "Thorax": 145, "Stomach": 125, "Arms": 100, "Legs": 110
        },
        "weapons": [
            "Pistola Dorada TT-33 7.62x25 (Ítem icónico de quest)",
            "AK-101 (5.56x45) / AK-102 / DT MDR 5.56",
            "Granadas F-1 y Zarya"
        ],
        "followers": {
            "count": 4,
            "name": "Hermanos Zavodskoy (Guardias de Élite)",
            "gear": "Cascos Altyn/ZSh, chalecos clase 4/5, AK-74N con munición BT/BS.",
            "behavior": "Muy agresivos. Cargarán en grupo hacia el jugador mientras Reshala se repliega."
        },
        "tactics": [
            "Reshala tiene poca salud y no suele llevar armadura; su peligro real son los 4 guardias armados.",
            "Lanza granadas hacia las puertas para forzarlos a gritar y romper su formación.",
            "En Dorms, usa siempre asomado por la derecha ('right-hand peek') desde las escaleras.",
            "Guarda su Pistola Dorada para la quest 'The Huntsman Path - Trophy' de Jaeger."
        ],
        "notable_loot": [
            "Golden TT-33 Pistol (Necesario para Quest)",
            "Bitcoin (0.2 BTC)",
            "Tarjetas de acceso Labs (Keycards)",
            "Llaves de Dorms raras (Marked Key)"
        ]
    },
    {
        "id": "killa",
        "name": "Killa",
        "russian_name": "Килла",
        "maps": ["Interchange"],
        "spawn_chance": "75% (PvE)  |  60% (PvP)",
        "pve_chance": "75%",
        "pvp_chance": "60%",
        "map_spawn_chances": {
            "Interchange": {"pve": "75%", "pvp": "60%"}
        },
        "map_spawns": {
            "Interchange": [
                {"zone": "1F Centro del Mall: Brutal, KIBA y Generic [40%]", "details": "Probabilidad de zona: 40% — En el plano 'FIRST FLOOR' (derecha), frente a Kiba Arms, Brutal y Adik.", "x": 0.80, "y": 0.49, "chance": "40%"},
                {"zone": "1F Supermercado Goshan y Depósitos [20%]", "details": "Probabilidad de zona: 20% — En el plano 'FIRST FLOOR', sector central-derecho (Goshan).", "x": 0.84, "y": 0.40, "chance": "20%"},
                {"zone": "1F Supermercados OLI (Sur) e IDEA (Norte) [40%]", "details": "Probabilidad de zona: 20% OLI + 20% IDEA — Extremos norte (IDEA) y sur (OLI) del centro comercial.", "x": 0.80, "y": 0.67, "chance": "40%"},
                {"zone": "Estacionamiento Subterráneo (Parking B/C)", "details": "En el plano 'PARKING', bajo las rampas centrales de OLI/Goshan.", "x": 0.66, "y": 0.49, "chance": "Subsuelo"}
            ]
        },
        "total_hp": 890,
        "hp_breakdown": {
            "Head": 70, "Thorax": 210, "Stomach": 170, "Arms": 100, "Legs": 120
        },
        "weapons": [
            "RPK-16 (5.45x39) con tambor de 95 tiros (Igolnik / BS / PPBS)",
            "PP-19-01 Vityaz (9x19 PBP) / AKMS (7.62x39 BP)",
            "Granadas RGD-5 y F-1 de detonación instantánea"
        ],
        "followers": {
            "count": 0,
            "name": "Solitario (Sin guardias)",
            "gear": "Casco Maska 1Sch con visera de acero (Nivel 4 + Visera Nivel 6) y armadura 6B13 M 'Killa' (Nivel 5).",
            "behavior": "Cazador implacable. Te rastrea por sonido y rushea en sprint continuo disparando ráfagas sin retroceso."
        },
        "tactics": [
            "NUNCA dispares a su visera sin munición de penetración extrema (penetración > 55 requerida).",
            "Aplica 'Leg Meta': usa balas de alto daño a la carne (como RIP, QuakeMaker o Flechette) directo a sus piernas.",
            "Hazlo correr: mientras sprintea hacia vos tarda medio segundo en levantar el arma; ese es tu momento de fuego.",
            "Si te impacta, retírate a cobertura dura; no intercambies fuego estático."
        ],
        "notable_loot": [
            "Casco Maska 1Sch con rayas Adidas",
            "Armadura corporal 6B13 M Killa",
            "Tambor de 95 balas 5.45x39",
            "Keycards de Laboratorio Labs",
            "Llave de Kiba Arms"
        ]
    },
    {
        "id": "tagilla",
        "name": "Tagilla",
        "russian_name": "Тагилла",
        "maps": ["Factory", "Interchange"],
        "spawn_chance": "50% Factory Día / 75% Factory Noche & Interchange (PvE/PvP)",
        "pve_chance": "50% (Día) / 75% (Noche)",
        "pvp_chance": "50% (Día) / 75% (Noche)",
        "map_spawn_chances": {
            "Factory": {"pve": "50% (Día) / 75% (Noche)", "pvp": "50% (Día) / 75% (Noche)"},
            "Interchange": {"pve": "75%", "pvp": "75%"}
        },
        "map_spawns": {
            "Factory": [
                {"zone": "Oficinas del 3er Piso (TOP FLOOR) [100% BotZone]", "details": "Panel izquierdo ('TOP FLOOR'): pasillo de oficinas y caja fuerte.", "x": 0.09, "y": 0.38, "chance": "33%"},
                {"zone": "Planta Baja y Silos (GROUND FLOOR) [100% BotZone]", "details": "Panel central ('GROUND FLOOR'): entre los tanques y carpa médica.", "x": 0.60, "y": 0.38, "chance": "34%"},
                {"zone": "Túneles Subterráneos (TUNNELS) [100% BotZone]", "details": "Panel derecho ('TUNNELS'): red de cañerías bajo planta baja.", "x": 0.84, "y": 0.36, "chance": "33%"}
            ],
            "Interchange": [
                {"zone": "Zona Tagilla / Subsuelo y Galerías de Interchange [100%]", "details": "Probabilidad en Interchange: 75% (ZoneTagilla 100%). Patrulla sectores internos y estacionamiento.", "x": 0.72, "y": 0.52, "chance": "100%"}
            ]
        },
        "total_hp": 1220,
        "hp_breakdown": {
            "Head": 100, "Thorax": 320, "Stomach": 280, "Arms": 130, "Legs": 130
        },
        "weapons": [
            "Maza de demolición (Sledgehammer) cuerpo a cuerpo",
            "Saiga-12K con tambor de 20 tiros (Flechette / AP-20)",
            "AKS-74U con munición 5.45 BS / Igolnik"
        ],
        "followers": {
            "count": 0,
            "name": "Solitario (En The Labyrinth aparece como Shadow of Tagilla al 100%)",
            "gear": "Máscara de soldador 'Gorilla' / 'UBEY' (Nivel 5/6) y portaplacas Crye AVS MBAV (Nivel 6).",
            "behavior": "Alterna entre cazarte a martillazos o vaciar su tambor de escopeta a corta distancia."
        },
        "tactics": [
            "Si saca el mazo, puedes kitearlo (retroceder disparando) o saltar sobre cajas para confundir su pathfinding.",
            "Su nuca no está blindada: un disparo en la parte trasera de la cabeza lo mata en el acto.",
            "Sus piernas están 100% desprotegidas; escopetazos a las piernas son su punto débil absoluto.",
            "Escucha sus pasos pesados y resoplidos en los túneles subterráneos."
        ],
        "notable_loot": [
            "Máscara de soldador Gorilla / UBEY (Nivel 5)",
            "Maza de demolición",
            "Portaplacas Crye Precision AVS MBAV (Nivel 6)",
            "Llaves de Factory y Labs Keycards"
        ]
    },
    {
        "id": "shturman",
        "name": "Shturman (The Woods Sniper)",
        "russian_name": "Штурман",
        "maps": ["Woods"],
        "spawn_chance": "75% (PvE)  |  60% (PvP)",
        "pve_chance": "75%",
        "pvp_chance": "60%",
        "map_spawn_chances": {
            "Woods": {"pve": "75%", "pvp": "60%"}
        },
        "map_spawns": {
            "Woods": [
                {"zone": "Aserradero Central (Lumber Mill / Sawmill) [100%]", "details": "Probabilidad de zona: 100% — Entre el galpón metálico gris, el almacén rojo y las pilas de madera junto al lago.", "x": 0.43, "y": 0.64, "chance": "100%"},
                {"zone": "Cabañas de obreros del Aserradero", "details": "Claro superior del mismo Aserradero junto a las 3 cabañas de madera y el cofre de Shturman.", "x": 0.46, "y": 0.60, "chance": "Aserradero"}
            ]
        },
        "total_hp": 812,
        "hp_breakdown": {
            "Head": 62, "Thorax": 180, "Stomach": 150, "Arms": 100, "Legs": 110
        },
        "weapons": [
            "SVDS Dragunov 7.62x54R (SNB / PS / BT)",
            "AK-105 compacto (5.45x39)",
            "Red Rebel Ice Pick (Piolet en su funda)"
        ],
        "followers": {
            "count": 2,
            "name": "Hermanos Svetloozerskiy (Francotiradores)",
            "gear": "Mosin / SVDS / Vepr Hunter con miras ópticas y munición de alta penetración.",
            "behavior": "Disparan ráfagas triples sincronizadas ('BAM-BAM-BAM') a distancias de hasta 200m."
        },
        "tactics": [
            "NO compitas en duelos de francotirador en campo abierto; su puntería a 200m es letal.",
            "Acércate con cobertura dura por las cabañas de madera o las pilas de troncos.",
            "Shturman NO usa casco: un disparo certero en su cabeza lo elimina instantáneamente.",
            "Cuidado con su triple disparo rápido: suele disparar tres tiros en menos de un segundo con el SVD."
        ],
        "notable_loot": [
            "Shturman's Stash Key (Abre el cofre del aserradero)",
            "Red Rebel Ice Pick (Piolet para extracciones de montaña)",
            "SVDS Dragunov con mira telescópica",
            "Posible Green o Violet Keycard de Labs"
        ]
    },
    {
        "id": "glukhar",
        "name": "Glukhar",
        "russian_name": "Глухарь",
        "maps": ["Reserve"],
        "spawn_chance": "60% (PvE)  |  60% (PvP)",
        "pve_chance": "60%",
        "pvp_chance": "60%",
        "map_spawn_chances": {
            "Reserve": {"pve": "60%", "pvp": "60%"}
        },
        "map_spawns": {
            "Reserve": [
                {"zone": "Cuarteles del Helicóptero (Barracks: Pawn / School) [25%]", "details": "Probabilidad de zona: 25% — Edificios Black/White Pawn y Black Bishop alrededor del helicóptero.", "x": 0.42, "y": 0.50, "chance": "25%"},
                {"zone": "Estación de Trenes y Hangares K (K Buildings) [25%]", "details": "Probabilidad de zona: 25% — Plataformas de carga K y galpón del tren blindado.", "x": 0.25, "y": 0.34, "chance": "25%"},
                {"zone": "Garajes Caballo (White & Black Knight) [25%]", "details": "Probabilidad de zona: 25% — Patios de vehículos militares y talleres Knight frente a King.", "x": 0.31, "y": 0.49, "chance": "25%"},
                {"zone": "Búnker de Almacenamiento Subterráneo (Storage Bunker) [25%]", "details": "Probabilidad de zona: 25% — Almacenes subterráneos bajo los hangares K (hermetic bunker).", "x": 0.74, "y": 0.25, "chance": "25%"}
            ]
        },
        "total_hp": 1010,
        "hp_breakdown": {
            "Head": 70, "Thorax": 220, "Stomach": 140, "Arms": 145, "Legs": 145
        },
        "weapons": [
            "ASh-12 (12.7x55mm bala pesada PS12B)",
            "M1A (7.62x51mm tambor de 50)",
            "PP-19-01 o revólver MP-412"
        ],
        "followers": {
            "count": 6,
            "name": "Batallón Táctico de 6 Guardias (Scouts, Asalto y Seguridad)",
            "gear": "Armaduras pesadas Nivel 5/6, cascos Vulkan / Altyn y armas automáticas pesadas.",
            "behavior": "Altamente coordinados: los scouts flanquean, los defensores forman un muro y Glukhar dispara desde atrás."
        },
        "tactics": [
            "Oblígalos a entrar por un embudo estrecho como escaleras o pasillos donde no puedan rodearte.",
            "El calibre 12.7x55 de Glukhar atraviesa cualquier blindaje de un solo disparo en el tórax.",
            "Usa granadas para forzar a los scouts a replegarse y despacharlos uno por uno.",
            "Nunca asomes la cabeza al mismo ángulo dos veces seguidas."
        ],
        "notable_loot": [
            "ASh-12 modificada con munición PS12B",
            "M1A con tambor de 50 tiros",
            "Llaves militares de Reserve y Labs Keycards",
            "Chalecos blindados clase 5 y 6"
        ]
    },
    {
        "id": "sanitar",
        "name": "Sanitar",
        "russian_name": "Санитар",
        "maps": ["Shoreline"],
        "spawn_chance": "75% (PvE)  |  60% (PvP)",
        "pve_chance": "75%",
        "pvp_chance": "60%",
        "map_spawn_chances": {
            "Shoreline": {"pve": "75%", "pvp": "60%"}
        },
        "map_spawns": {
            "Shoreline": [
                {"zone": "El Muelle y Oficinas (Pier Boat) [50%]", "details": "Probabilidad de zona: 50% — Edificio administrativo costero y muelle en el extremo sur.", "x": 0.43, "y": 0.90, "chance": "50%"},
                {"zone": "Villas, Cabañas e Invernaderos (Cottages / Greenhouses) [50%]", "details": "Probabilidad de zona: 50% — Casas de campo cerradas y patios en el sector oeste.", "x": 0.21, "y": 0.61, "chance": "50%"},
                {"zone": "Resort de Salud (WEST / EAST Wing)", "details": "Planta baja del complejo central y patio de la ambulancia.", "x": 0.40, "y": 0.47, "chance": "Resort"}
            ]
        },
        "total_hp": 1270,
        "hp_breakdown": {
            "Head": 70, "Thorax": 360, "Stomach": 300, "Arms": 100, "Legs": 170
        },
        "weapons": [
            "VSS Vintorez (9x39 SP-6 / BP / SPP)",
            "Saiga-12K / Kedr-B / OP-SKS",
            "Inyectores y cócteles químicos (Meldonin, Obdolbos, Propital)"
        ],
        "followers": {
            "count": 2,
            "name": "Ex-médicos fuertemente armados (Khirurg & Anatom)",
            "gear": "Vepr Hunter, AKM con BP, cascos Altyn/LShZ y chalecos nivel 5.",
            "behavior": "Sanitar se cura constantemente en combate y aplica estimulantes regenerativos a sus aliados."
        },
        "tactics": [
            "Sanitar NO lleva casco: un disparo certero en la cabeza con penetración media es letal.",
            "Si lo hieres y no lo rematas, se esconderá e inyectará propital, regenerando toda su vida en segundos.",
            "En el Pier, atácalos desde la colina con rifle de francotirador.",
            "Lleva siempre torniquetes; sus guardias usan balas con probabilidad extrema de sangrado."
        ],
        "notable_loot": [
            "Sanitar's Bag y estimulantes raros (AHF1-M, 3-(b-TG), MULE, Propital, Obdolbos)",
            "Llave con cinta azul de Sanitar (Sanitar's Key - Resort 110)",
            "Tarjetas de acceso Labs (Blue / Green Keycard)",
            "VSS Vintorez con mira óptica"
        ]
    },
    {
        "id": "kaban",
        "name": "Kaban",
        "russian_name": "Кабан",
        "maps": ["Streets of Tarkov"],
        "spawn_chance": "75% (PvE)  |  60% (PvP)",
        "pve_chance": "75%",
        "pvp_chance": "60%",
        "map_spawn_chances": {
            "Streets of Tarkov": {"pve": "75%", "pvp": "60%"}
        },
        "map_spawns": {
            "Streets of Tarkov": [
                {"zone": "Concesionaria LexOs (Car Dealership) [100%]", "details": "Probabilidad de zona: 100% — Complejo fortificado en el centro-sur, junto a Sparja y Primorsky Ave.", "x": 0.49, "y": 0.65, "chance": "100%"}
            ]
        },
        "total_hp": 1295,
        "hp_breakdown": {
            "Head": 85, "Thorax": 355, "Stomach": 260, "Arms": 150, "Legs": 150
        },
        "weapons": [
            "Ametralladora ligera PKM / PKP Pecheneg (7.62x54R)",
            "RPK-16 con tambor de 95 tiros",
            "Pistola automática Stechkin APS / APB"
        ],
        "followers": {
            "count": 8,
            "name": "Guardias de LexOs (Basmach, Gus, Escoltas y Francotiradores)",
            "gear": "Armaduras pesadas, ametralladoras fijas AGS-30 y NSV Kord, rifles de precisión.",
            "behavior": "Zona minada y vigilada por nidos de ametralladoras pesadas fijas."
        },
        "tactics": [
            "¡Cuidado con las minas! El perímetro de LexOs tiene campos minados marcados con carteles.",
            "Neutraliza primero a los francotiradores en los techos antes de entrar al patio interior.",
            "Kaban no se mueve mucho, pero el fuego sostenido de su PKM/PKP no perdona.",
            "Lanza granadas desde el exterior para desarticular los nidos de ametralladora fija."
        ],
        "notable_loot": [
            "Ametralladora PKP Pecheneg (Necesaria para Gunsmith - Part 25)",
            "Llaves de la concesionaria LexOs y Chekannaya 15",
            "Cajas de munición pesada 7.62x54R SNB/BT"
        ]
    },
    {
        "id": "kollontay",
        "name": "Kollontay",
        "russian_name": "Коллонтай",
        "maps": ["Streets of Tarkov", "Ground Zero"],
        "spawn_chance": "75% en Streets (PvE)  |  60% en Streets (PvP)",
        "pve_chance": "75%",
        "pvp_chance": "60%",
        "map_spawn_chances": {
            "Streets of Tarkov": {"pve": "75%", "pvp": "60%"},
            "Ground Zero": {"pve": "0% (Inactivo)", "pvp": "0% (Inactivo)"}
        },
        "map_spawns": {
            "Streets of Tarkov": [
                {"zone": "Centro Comercial Klimov (Klimov Shopping Mall) [50%]", "details": "Probabilidad de zona: 50% — Galerías comerciales y Stylobate Building frente a Klimov Street (planta alta y patio de comidas).", "x": 0.672, "y": 0.324, "chance": "50%"},
                {"zone": "Academia MVD (Ministry of the Interior Academy) [50%]", "details": "Probabilidad de zona: 50% — Complejo de la Academia del Ministerio del Interior al sur de Klimov Street.", "x": 0.755, "y": 0.496, "chance": "50%"}
            ],
            "Ground Zero": [
                {"zone": "Plaza Central y Edificios TerraGroup / Empire [0% actual]", "details": "Actualmente desactivado en Ground Zero 21+ según eftboss.com/pve (aparece en Streets of Tarkov al 75% en PvE).", "x": 0.50, "y": 0.38, "chance": "0%"}
            ]
        },
        "total_hp": 1055,
        "hp_breakdown": {
            "Head": 65, "Thorax": 300, "Stomach": 150, "Arms": 150, "Legs": 120
        },
        "weapons": [
            "Porra policial PR-Taran (provoca pánico y encasquillamiento del arma)",
            "RPK-16 / AK-104 / KS-23M con munición Shrapnel-10 y Barrikada"
        ],
        "followers": {
            "count": 4,
            "name": "Guardias expolicías OMON (Asalto y Seguridad)",
            "gear": "Cascos antidisturbios, chalecos policiales pesados y rifles automáticos.",
            "behavior": "Si Kollontay saca su porra y te carga, tu arma sufre encasquillamiento forzado por efecto de pánico."
        },
        "tactics": [
            "Mantén la distancia en todo momento; si se acerca cuerpo a cuerpo con su porra, tu arma se encasquillará ('weapon jam').",
            "Apunta a la cabeza desde media distancia antes de que cierre la brecha.",
            "Limpia a sus guardias desde las ventanas superiores del centro comercial Klimov o del patio de la Academia MVD."
        ],
        "notable_loot": [
            "Porra táctica policial PR-Taran de Kollontay",
            "Armaduras policiales y placas balísticas nivel 5/6",
            "Llaves raras del complejo MVD y tarjetas Labs"
        ]
    },
    {
        "id": "the_goons",
        "name": "The Goons (Knight, Big Pipe, Birdeye)",
        "russian_name": "Отступники",
        "maps": ["Lighthouse", "Shoreline", "Customs", "Woods"],
        "spawn_chance": "30% Lighthouse/Shoreline, 25% Customs/Woods (PvE)  |  20% (PvP)",
        "pve_chance": "30% / 25%",
        "pvp_chance": "20%",
        "map_spawn_chances": {
            "Lighthouse": {"pve": "30%", "pvp": "20%"},
            "Shoreline": {"pve": "30%", "pvp": "20%"},
            "Customs": {"pve": "25%", "pvp": "20%"},
            "Woods": {"pve": "25%", "pvp": "20%"}
        },
        "map_spawns": {
            "Lighthouse": [
                {"zone": "USEC Cottage / Chalet Azul (Zone_Chalet) [100%]", "details": "Probabilidad en Lighthouse: 30% PvE / 20% PvP (100% en Chalet y Planta de Tratamiento).", "x": 0.56, "y": 0.59, "chance": "100%"},
                {"zone": "Planta de Tratamiento de Agua (Water Treatment)", "details": "Entre los estanques circulares y los Edificios 1 y 2 de Rogues.", "x": 0.54, "y": 0.31, "chance": "Planta"}
            ],
            "Shoreline": [
                {"zone": "Estación Meteorológica (Weather Station) [100%]", "details": "Probabilidad en Shoreline: 30% PvE / 20% PvP (100% en la colina del radar meteorológico).", "x": 0.52, "y": 0.73, "chance": "100%"}
            ],
            "Customs": [
                {"zone": "Fortress / Stronghold (ZB-013) [100%]", "details": "Probabilidad en Customs: 25% PvE / 20% PvP (100% en Stronghold).", "x": 0.47, "y": 0.37, "chance": "100%"}
            ],
            "Woods": [
                {"zone": "Scav Bunker Noroeste y Antena de Radio [100%]", "details": "Probabilidad en Woods: 25% PvE / 20% PvP (100% en Northwest Scav Bunker).", "x": 0.31, "y": 0.17, "chance": "100%"}
            ]
        },
        "total_hp": 3120,
        "hp_breakdown": {
            "Knight": 1120, "Big Pipe": 1050, "Birdeye": 950
        },
        "weapons": [
            "Knight: FN SCAR-H (7.62x51 M61/M80) / MDR / MCX .300 Blackout",
            "Big Pipe: Lanzagranadas rotatorio M32A1 de 40mm / MCX .300 Blackout",
            "Birdeye: SR-25 / RSASS / Remington M700 (Pasos 100% silenciosos)"
        ],
        "followers": {
            "count": 3,
            "name": "Trío de contratistas militares renegados USEC (Knight, Big Pipe y Birdeye)",
            "gear": "Equipamiento militar nivel 5/6, máscara Death Knight, chalecos CPC y mochilas de patrulla.",
            "behavior": "Súper agresivos. Knight y Big Pipe cargan de frente mientras Birdeye flanquea sin hacer ruido de pisadas."
        },
        "tactics": [
            "Nunca los pelees en campo abierto; su rango de detección supera los 250 metros.",
            "Encerrate en una habitación y déjalos empujar uno por uno por una puerta angosta.",
            "Cuidado absoluto con el lanzagranadas de 40mm de Big Pipe; un impacto directo es muerte instantánea.",
            "Después de eliminar a Knight y Big Pipe, espera pacientemente: Birdeye tardará más en acercarse en silencio."
        ],
        "notable_loot": [
            "Máscara balística Death Shadow / Death Knight",
            "Lanzagranadas rotatorio de 40mm Milkor M32A1 MSGL",
            "Rifles SCAR-H, RSASS y SR-25 modificados al máximo",
            "Chalecos portaplacas Crye Precision CPC y Keycards raras"
        ]
    },
    {
        "id": "partisan",
        "name": "Partisan (The Hunter)",
        "russian_name": "Партизан",
        "maps": ["Woods", "Customs", "Shoreline", "Lighthouse"],
        "spawn_chance": "25% en todos los mapas (PvE)  |  25% (PvP)",
        "pve_chance": "25%",
        "pvp_chance": "25%",
        "map_spawn_chances": {
            "Woods": {"pve": "25%", "pvp": "25%"},
            "Customs": {"pve": "25%", "pvp": "25%"},
            "Shoreline": {"pve": "25%", "pvp": "25%"},
            "Lighthouse": {"pve": "25%", "pvp": "25%"}
        },
        "map_spawns": {
            "Woods": [
                {"zone": "Bosques de Woods (Aserradero, Cabañas y Sunken Village) [25%]", "details": "Probabilidad en Woods: 25% PvE y PvP — Acecha silenciosamente colocando cables trampa en senderos.", "x": 0.52, "y": 0.54, "chance": "25%"}
            ],
            "Customs": [
                {"zone": "Colinas de Dorms, New Gas y Stronghold [25%]", "details": "Probabilidad en Customs: 25% PvE y PvP — Coloca cables trampa con granadas VOG en accesos y arbustos.", "x": 0.38, "y": 0.62, "chance": "25%"}
            ],
            "Shoreline": [
                {"zone": "Bosques entre Resort, Villas (Cottages) y Muelle [25%]", "details": "Probabilidad en Shoreline: 25% PvE y PvP — Arbustos densos cerca de las rutas de tránsito.", "x": 0.30, "y": 0.52, "chance": "25%"}
            ],
            "Lighthouse": [
                {"zone": "Ladera entre Chalet Azul, Resort Chalet y Aldea [25%]", "details": "Probabilidad en Lighthouse: 25% PvE y PvP — Senderos rocosos y jardines de los Chalets.", "x": 0.57, "y": 0.64, "chance": "25%"}
            ]
        },
        "total_hp": 950,
        "hp_breakdown": {
            "Head": 70, "Thorax": 200, "Stomach": 180, "Arms": 120, "Legs": 130
        },
        "weapons": [
            "AKMN / AKS-74UB con silenciador y lanzagranadas GP-25 bajo cañón",
            "AVT-40 (7.62x54R SNB/BT)",
            "Cables trampa con granadas F-1 / VOG-17 (Tripwires)"
        ],
        "followers": {
            "count": 0,
            "name": "Cazador solitario del bosque (Sin guardias)",
            "gear": "Sin casco ni chaleco blindado pesado, mochila Partisan llena de granadas y kits de trampas.",
            "behavior": "Sus pasos son 100% silenciosos. Coloca decenas de cables trampa alrededor de jugadores que acampan o tienen bajo Karma PMC."
        },
        "tactics": [
            "Mira con atención al suelo cuando entres o salgas de edificios; sus cables trampa en puertas son mortales.",
            "Si escuchas el chasquido metálico de una trampa, corre hacia adelante o salta fuera del radio en menos de 2 segundos.",
            "No lleva casco ni blindaje: cualquier ráfaga al tórax o cabeza lo abate muy rápido si lo ves primero.",
            "Cuidado con su lanzagranadas GP-25 bajo el cañón del AK."
        ],
        "notable_loot": [
            "Lanzagranadas GP-25 y munición VOG-25",
            "Bolso táctico de Partisan (espacio interno ampliado)",
            "Red Rebel Ice Pick y tarjetas de acceso raras",
            "Kits de cables trampa (Tripwire installation kits)"
        ]
    },
    {
        "id": "zryachiy",
        "name": "Zryachiy (The Lighthouse Sniper)",
        "russian_name": "Зрячий",
        "maps": ["Lighthouse"],
        "spawn_chance": "100% (PvE)  |  100% (PvP)",
        "pve_chance": "100%",
        "pvp_chance": "100%",
        "map_spawn_chances": {
            "Lighthouse": {"pve": "100%", "pvp": "100%"}
        },
        "map_spawns": {
            "Lighthouse": [
                {"zone": "Isla del Faro (Lighthouse Island) [100%]", "details": "Probabilidad de spawn: 100% garantizado en PvE y PvP — Colinas rocosas de la península del Faro protegiendo a Lightkeeper.", "x": 0.33, "y": 0.86, "chance": "100%"}
            ]
        },
        "total_hp": 1655,
        "hp_breakdown": {
            "Head": 175, "Thorax": 450, "Stomach": 270, "Arms": 190, "Legs": 190
        },
        "weapons": [
            "SVDS (7.62x54R SNB / BT) con visor térmico o nocturno",
            "Rifle de francotirador AXMC .338 Lapua Magnum (AP / FMJ)",
            "TRG M10 .338 Lapua Magnum"
        ],
        "followers": {
            "count": 2,
            "name": "2 Francotiradores Cultistas de Élite (Zryachiy Guards)",
            "gear": "Camuflaje ghillie blanco/rocoso, visores térmicos y munición perforante extrema.",
            "behavior": "Vigilan el puente hacia el Faro las 24 hs. No atacan si llevas el transmisor DSP codificado activo (salvo que les dispares o te acerques demasiado)."
        },
        "tactics": [
            "Si tienes el transmisor Digital Secure DSP codificado, NO le dispares: perderás el acceso a Lightkeeper.",
            "Para farmearlo desde el continente, necesitas un rifle calibrado a 350–450 metros con bala capaz de superar sus 175 HP de cabeza (como .338 Lapua Magnum).",
            "El puente hacia la isla está cubierto de minas Claymore invisibles si no llevas el transmisor DSP activo."
        ],
        "notable_loot": [
            "Rifles AXMC / TRG M10 .338 Lapua Magnum",
            "Pasamontañas exclusivo de Zryachiy",
            "Munición .338 Lapua Magnum AP y 7.62x54R SNB"
        ]
    },
    {
        "id": "cultists",
        "name": "Cultistas (Cultist Priest & Warriors)",
        "russian_name": "Жрец и Сектанты",
        "maps": ["Customs", "Woods", "Shoreline", "Factory", "Ground Zero"],
        "spawn_chance": "30% Customs/Woods, 25% Shoreline, 20% Factory, 15% GZ 21+ (PvE Noche)",
        "pve_chance": "15% – 30% (Noche)",
        "pvp_chance": "15% – 30% (Noche)",
        "map_spawn_chances": {
            "Customs": {"pve": "30% (Noche)", "pvp": "30% (Noche)"},
            "Woods": {"pve": "30% (Noche)", "pvp": "30% (Noche)"},
            "Shoreline": {"pve": "25% (Noche)", "pvp": "25% (Noche)"},
            "Factory": {"pve": "20% (Night Factory)", "pvp": "15% (Night Factory)"},
            "Ground Zero": {"pve": "15% (GZ 21+ Noche)", "pvp": "15% (GZ 21+ Noche)"}
        },
        "map_spawns": {
            "Customs": [
                {"zone": "Fortress / Stronghold (ZB-013) [100%]", "details": "Probabilidad en Customs: 30% PvE y PvP (22:00 a 07:00 hs) — 100% alrededor de Stronghold / ZB-013.", "x": 0.47, "y": 0.37, "chance": "100%"}
            ],
            "Woods": [
                {"zone": "Oeste del Aserradero y Círculo Ritual [50%]", "details": "Probabilidad en Woods: 30% PvE y PvP (22:00 a 07:00 hs) — 50% al oeste del Lumber Mill (ZoneMiniHouse).", "x": 0.23, "y": 0.72, "chance": "50%"},
                {"zone": "Sunken / Rundown Village (Aldea Hundida Norte) [50%]", "details": "Probabilidad de zona: 50% — Alrededor del círculo marcado en la aldea norte (ZoneBrokenVill).", "x": 0.45, "y": 0.19, "chance": "50%"}
            ],
            "Shoreline": [
                {"zone": "Bosque al Noreste de Sunken Village / Pantano [60%]", "details": "Probabilidad en Shoreline: 25% PvE y PvP (22:00 a 07:00 hs) — 60% en el bosque al noreste del pantano.", "x": 0.15, "y": 0.38, "chance": "60%"},
                {"zone": "Resort de Salud: Ala Oeste (20%) y Ala Este (20%) [40%]", "details": "Probabilidad de zona: 20% West Wing + 20% East Wing — Jardines oscuros del Resort.", "x": 0.39, "y": 0.46, "chance": "40%"}
            ],
            "Factory": [
                {"zone": "Night Factory (Planta Baja Oscura) [100%]", "details": "Probabilidad en Night Factory: 20% en PvE / 15% en PvP — Escondidos en rincones sin luz durante incursiones nocturnas.", "x": 0.59, "y": 0.44, "chance": "100%"}
            ],
            "Ground Zero": [
                {"zone": "Ground Zero 21+ Nocturno [100%]", "details": "Probabilidad en Ground Zero 21+: 15% en PvE y PvP (22:00 a 07:00 hs).", "x": 0.50, "y": 0.45, "chance": "100%"}
            ]
        },
        "total_hp": 850,
        "hp_breakdown": {
            "Head": 50, "Thorax": 200, "Stomach": 200, "Arms": 100, "Legs": 100
        },
        "weapons": [
            "Cultist Knife (Cuchillo con toxina letal por tiempo)",
            "PP-91-01 Kedr-B silenciado / VAL / SR-25 silenciado",
            "AK-74N / АКМN con munición BP/BS/Igolnik y supresor",
            "Granadas VOG-25 de impacto"
        ],
        "followers": {
            "count": 4,
            "name": "Cultist Warriors (Guerreros Sektants)",
            "gear": "Chalecos clase 5/6 (Hexgrid / Korund), armas silenciadas con munición tope de gama.",
            "behavior": "Movimiento 100% silencioso y sin huella térmica fuerte. Se arrastran en la maleza y emboscan con el cuchillo envenenado."
        },
        "tactics": [
            "¡LLEVA ANTÍDOTO xTG-12 o Augmentin! Si te apuñalan con el Cultist Knife recibirás daño continuo mortal.",
            "Sólo aparecen en incursiones nocturnas entre las 22:00 y las 07:00 hs.",
            "Si los escuchas susurrar o ves sombras arrastrándose, no entres a los arbustos; usa granadas para forzarlos a ponerse de pie.",
            "Dispara a la cabeza del Priest: solo tiene 50 HP y nunca lleva casco."
        ],
        "notable_loot": [
            "Cultist Knife (Necesario para la misión Night Sweep)",
            "Llaves Marcadas (Dorm Room 314 Marked Key, RB-BK, RB-VO, Chekannaya 13)",
            "Tarjetas de acceso Labs (Keycards) y Taiga-1 Machete",
            "Inyectores xTG-12 y estimulantes raros"
        ]
    },
    {
        "id": "wedge",
        "name": "The Wedge (Black Division Commander)",
        "russian_name": "Командир Wedge",
        "maps": ["Icebreaker"],
        "spawn_chance": "100% (PvE)  |  100% (PvP)",
        "pve_chance": "100%",
        "pvp_chance": "100%",
        "map_spawn_chances": {
            "Icebreaker": {"pve": "100%", "pvp": "100%"}
        },
        "map_spawns": {
            "Icebreaker": [
                {"zone": "Deck -2: Engine Room", "details": "Zona principal de The Wedge y su escuadrón Black Division, en las entrañas del buque (requiere Engine Room Keycard).", "x": 0.89, "y": 0.30},
                {"zone": "Deck 9: Bridge", "details": "Zona alternativa: puente de mando y sistemas de navegación en la parte alta del buque.", "x": 0.105, "y": 0.43}
            ]
        },
        "total_hp": 880,
        "hp_breakdown": {
            "Head": 70, "Thorax": 170, "Stomach": 140, "Arms": 120, "Legs": 130
        },
        "weapons": [
            "SIG MCX SPEAR (6.8x51mm Hybrid)",
            "HK 416A5 / M4A1 customizada al máximo (M995 / SSA AP)",
            "Granadas tácticas de impacto y humo"
        ],
        "followers": {
            "count": 5,
            "name": "Escuadrón Black Division (Operadores de Élite)",
            "gear": "Blindaje corporal Nivel 5/6, visores nocturnos cuádruples GPNVG-18 y armas con supresor.",
            "behavior": "Doctrina CQC militar de alta precisión. Coordinan fuego cruzado y granadas."
        },
        "tactics": [
            "Es el combate militar más táctico del juego: no expongas líneas largas en los pasillos.",
            "El calibre 6.8x51 del MCX SPEAR de Wedge pulveriza blindajes de clase 5 y 6 en dos impactos.",
            "Usa granadas de fragmentación para limpiar los ángulos muertos del centro de mando.",
            "Combátelo en ángulos cerrados usando rifles con balas de máximo poder perforante."
        ],
        "notable_loot": [
            "Llaves y tarjetas de acceso del Boreas (Icebreaker)",
            "Rifle SIG MCX SPEAR 6.8x51 y visores GPNVG-18",
            "Placas de blindaje compuestas Black Division",
            "Suministros médicos y estimulantes militares avanzados"
        ]
    }
]


def get_all_bosses() -> List[Dict[str, Any]]:
    """Retorna todos los bosses registrados."""
    return BOSSES_DATA


def get_boss_by_id(boss_id: str) -> Dict[str, Any]:
    """Busca un boss específico por su ID."""
    for b in BOSSES_DATA:
        if b["id"] == boss_id:
            return b
    return BOSSES_DATA[0]


def get_boss_map_spawn_chance(boss: Dict[str, Any], map_name: str, mode: str = "pve") -> str:
    """Retorna la probabilidad de spawn de un boss para un mapa y modo específico ('pve' o 'pvp')."""
    m_chances = boss.get("map_spawn_chances", {})
    if map_name in m_chances:
        val = m_chances[map_name].get(mode.lower())
        if val:
            return val
    return boss.get("pve_chance" if mode.lower() == "pve" else "pvp_chance") or boss.get("spawn_chance", "")


def sync_live_boss_spawns_from_eftboss() -> Tuple[bool, str]:
    """
    Sincroniza en vivo las probabilidades de spawn de todos los bosses desde la API de eftboss.com
    (https://json.tarkov.dev/pve/maps y https://json.tarkov.dev/regular/maps).
    Retorna (exito, mensaje).
    """
    headers = {
        "Accept": "application/json",
        "Origin": "https://eftboss.com",
        "Referer": "https://eftboss.com/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
    }
    mob_to_id = {
        "bossBully": "reshala",
        "bossKilla": "killa",
        "bossTagilla": "tagilla",
        "infectedTagilla": "tagilla",
        "bossKojaniy": "shturman",
        "bossGluhar": "glukhar",
        "bossSanitar": "sanitar",
        "bossBoar": "kaban",
        "bossKolontay": "kollontay",
        "bossKnight": "the_goons",
        "bossPartisan": "partisan",
        "bossZryachiy": "zryachiy",
        "sectantPriest": "cultists",
        "bossWedge": "wedge",
    }
    norm_map_to_app_map = {
        "customs": "Customs",
        "interchange": "Interchange",
        "factory": "Factory",
        "woods": "Woods",
        "reserve": "Reserve",
        "shoreline": "Shoreline",
        "streets-of-tarkov": "Streets of Tarkov",
        "lighthouse": "Lighthouse",
        "ground-zero": "Ground Zero",
        "ground-zero-21": "Ground Zero",
        "the-lab": "The Lab",
        "the-lab-dark": "The Lab",
        "icebreaker": "Icebreaker",
    }

    try:
        live_rates: Dict[str, Dict[str, Dict[str, int]]] = {}
        for mode_key, api_mode in [("pve", "pve"), ("pvp", "regular")]:
            resp = requests.get(f"https://json.tarkov.dev/{api_mode}/maps", headers=headers, timeout=12)
            if resp.status_code != 200:
                continue
            maps_dict = resp.json().get("data", {}).get("maps", {})
            for m_obj in maps_dict.values():
                norm_m = m_obj.get("normalizedName", "")
                app_map = norm_map_to_app_map.get(norm_m)
                if not app_map:
                    continue
                for b_entry in m_obj.get("bosses", []):
                    mob = b_entry.get("mob", "")
                    b_id = mob_to_id.get(mob)
                    if not b_id:
                        continue
                    pct = int(round(float(b_entry.get("spawnChance", 0)) * 100))
                    live_rates.setdefault(b_id, {}).setdefault(app_map, {})
                    prev = live_rates[b_id][app_map].get(mode_key, 0)
                    if pct > prev:
                        live_rates[b_id][app_map][mode_key] = pct

        if not live_rates:
            return False, "No se recibieron datos nuevos del servidor."

        updated_count = 0
        for boss in BOSSES_DATA:
            b_id = boss["id"]
            if b_id not in live_rates:
                continue
            b_maps = live_rates[b_id]
            map_chances = boss.setdefault("map_spawn_chances", {})
            pve_vals = []
            pvp_vals = []
            for m_name in boss.get("maps", []):
                if m_name in b_maps:
                    pve_v = b_maps[m_name].get("pve")
                    pvp_v = b_maps[m_name].get("pvp")
                    if pve_v is not None and pvp_v is not None:
                        if b_id == "tagilla" and m_name == "Factory":
                            map_chances[m_name] = {"pve": f"{pve_v}% (Día) / 75% (Noche)", "pvp": f"{pvp_v}% (Día) / 75% (Noche)"}
                        elif b_id == "cultists":
                            map_chances[m_name] = {"pve": f"{pve_v}% (Noche)", "pvp": f"{pvp_v}% (Noche)"}
                        else:
                            map_chances[m_name] = {"pve": f"{pve_v}%", "pvp": f"{pvp_v}%"}
                        pve_vals.append(f"{pve_v}%")
                        pvp_vals.append(f"{pvp_v}%")
                        updated_count += 1
            if len(boss.get("maps", [])) == 1 and pve_vals and pvp_vals:
                boss["pve_chance"] = pve_vals[0]
                boss["pvp_chance"] = pvp_vals[0]
                boss["spawn_chance"] = f"{pve_vals[0]} (PvE)  |  {pvp_vals[0]} (PvP)"

        return True, f"Spawns sincronizados en vivo con eftboss.com ({updated_count} mapas actualizados)."
    except Exception as exc:
        return False, f"Modo offline activo ({exc})"
