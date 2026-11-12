"""
TarkovScope - Base de Conocimiento Táctica de Mapas de Escape from Tarkov
Incluye datos completos para los 10 mapas principales (incluyendo Ground Zero y Streets of Tarkov)
y Icebreaker: duración real, jugadores, descripción táctica en español, extracciones (PMC, Scav,
Co-Op, Vehículo, Bengala), Transits, jefes y llaves críticas recomendadas.
"""
from typing import Dict, Any, List, Tuple

MAPS_TACTICAL_DATA: Dict[str, Dict[str, Any]] = {
    "groundzero": {
        "key": "groundzero",
        "name": "Ground Zero",
        "aliases": ["groundzero", "ground zero", "sandbox", "zona cero"],
        "raid_duration": "35 min",
        "players": "10 - 12 PMCs",
        "level_note": "Colas separadas: Nv. 1-20 (Principiantes) | Nv. 21+ (Veteranos con Boss Kollontay y Cultistas)",
        "description": (
            "Centro financiero de Tarkov y sede corporativa de TerraGroup, donde estalló el "
            "conflicto inicial. Es un mapa urbano compacto de dos niveles: una calle principal "
            "rodeada de rascacielos (TerraGroup, Empire, Fusion, Skyside, Capital Insight, Nakatani) "
            "y una red subterránea de estacionamientos que conecta todos los edificios sin exponerse "
            "a los francotiradores de las ventanas superiores."
        ),
        "bosses": [
            "Kollontay (Inactivo actualmente en cola 21+ / 0% — Plaza TerraGroup)",
            "Cultist Priest & Sectarios (15% Noche en cola Nivel 21+ — Calles perimetrales)"
        ],
        "extractions": [
            {"name": "Emercom Checkpoint", "faction": "PMC / Scav", "req": "Siempre abierto (Extremo Norte, detrás de Elemental Global)"},
            {"name": "Nakatani Basement Stairs", "faction": "PMC / Scav", "req": "Siempre abierto (Extremo Sur, sótano del edificio Nakatani)"},
            {"name": "Police Cordon V-Ex", "faction": "PMC (Vehículo)", "req": "5,000 Rublos por jugador (Máx. 4 PMCs — frente a TerraGroup)"},
            {"name": "Mira Ave (Bengala Verde)", "faction": "PMC / Scav", "req": "Disparar bengala verde (Green Flare) en la zona de señal antes de avanzar"},
            {"name": "Scav Checkpoint (Co-Op)", "faction": "Co-Op", "req": "Requiere 1 PMC + 1 Scav juntos (Noreste de TerraGroup)"},
            {"name": "Tartowers Sales Office", "faction": "PMC / Scav", "req": "Requiere encontrar la nota con el código 'Adaptation' dentro de la raid"}
        ],
        "transits": [
            "Transit a Streets of Tarkov (Calle lateral al oeste de Skyside / Fusion)"
        ],
        "keys": [
            "TerraGroup Science Office Key (Misión 'Saving the Mole' + PC y loot científico)",
            "Underground Parking Utility Room Key (Suministros técnicos y armas)",
            "United Credit Bank Cash Register Key (Cajas fuertes y rublos)"
        ],
        "hotspots": [
            "Edificio TerraGroup (Oficina del científico, garaje de patrulleros y plaza central)",
            "Edificio Empire & Bar (Posición elevada con ametralladora pesada NSV y lanzagranadas AGS)",
            "Complejo Skyside & Restaurante Fusion (Cajas médicas y misiones iniciales)",
            "Banco Capital Insight & Edificio Nakatani (Oficinas financieras y acceso subterráneo)"
        ]
    },
    "customs": {
        "key": "customs",
        "name": "Customs",
        "aliases": ["customs", "aduanas", "bigmap"],
        "raid_duration": "40 min",
        "players": "10 - 12 PMCs",
        "level_note": "Abierto a todos los niveles — Mapa troncal de progresión temprana y media",
        "description": (
            "Parque industrial y terminal aduanera adyacente a la fábrica Polikhim. "
            "Presenta un diseño lineal de este a oeste dividido por un río, con embudos tácticos "
            "críticos en los puentes, el complejo de Dormitorios (Dorms de 2 y 3 pisos), "
            "la Fortaleza (Stronghold / ZB-013) y los galpones industriales."
        ),
        "bosses": [
            "Reshala y 4 Guardias Zavodskoy (75% PvE / 60% PvP — Dorms, New Gas o Stronghold)",
            "The Goons: Knight, Big Pipe y Birdeye (25% PvE / 20% PvP — Fortaleza / Stronghold)",
            "Partisan (25% PvE / 25% PvP — Bosques traseros de Dorms y colinas de New Gas)",
            "Cultistas (30% Noche 22:00-06:00 — Stronghold y bosque de Dorms)"
        ],
        "extractions": [
            {"name": "ZB-1011", "faction": "PMC", "req": "Siempre abierto para spawns del lado Oeste (Big Red)"},
            {"name": "Crossroads / Trailer Park", "faction": "PMC", "req": "Siempre abierto para spawns del lado Este (Boiler)"},
            {"name": "Dorms V-Ex (Vehículo)", "faction": "PMC (Vehículo)", "req": "5,000 Rublos por jugador (Portón trasero de Dorms 3 pisos)"},
            {"name": "ZB-1013 (Stronghold Basement)", "faction": "PMC", "req": "Encender electricidad en Galpón #4 + usar Factory Emergency Exit Key"},
            {"name": "Old Gas Station / ZB-1012", "faction": "PMC", "req": "Abierto si el humo verde / reflector exterior está encendido"},
            {"name": "Smuggler's Boat", "faction": "PMC", "req": "Disponible si la fogata junto al río está encendida"},
            {"name": "Railroad Passage (Bengala)", "faction": "PMC / Scav", "req": "Disparar bengala verde sobre las vías al norte de Old Gas"},
            {"name": "Boiler Room Basement (Co-Op)", "faction": "Co-Op", "req": "Requiere 1 PMC + 1 Scav"},
            {"name": "Admin Gate / Factory Far Corner / Shacks", "faction": "Scav", "req": "Extracciones estándar de Player Scav"}
        ],
        "transits": [
            "Transit a Factory (Portón norte de Old Gas Station)",
            "Transit a Reserve (Vías férreas al suroeste de Big Red)",
            "Transit a Interchange (Portón de la autopista en el extremo Este)",
            "Transit a Shoreline (Camino bloqueado al sur del puente principal)"
        ],
        "keys": [
            "Dorm Room 314 Marked Key (Habitación ritual con el mejor loot de armas/casos)",
            "Factory Emergency Exit Key (Abre ZB-013 en Stronghold y atajo de New Gas)",
            "Dorm Room 114, 206, 214, 220 y 303 (Esenciales para Quests de Therapist y Skier)",
            "Customs Office Key / Director's Office Key (Oficina de Big Red — múltiples Quests)"
        ],
        "hotspots": [
            "Dormitorios de 3 y 2 pisos (Dorms — Cajas fuertes, Habitación Marcada 314 y Reshala)",
            "Fortaleza / Stronghold (Alijo médico, ametralladoras pesadas, Reshala y The Goons)",
            "Galpón #4 y Edificio Crackhouse (Inteligencia militar, Morfina y Salewas)",
            "Big Red (Galpón de Aduanas del lado oeste y oficinas de dirección)"
        ]
    },
    "woods": {
        "key": "woods",
        "name": "Woods",
        "aliases": ["woods", "bosque"],
        "raid_duration": "40 min",
        "players": "10 - 12 PMCs",
        "level_note": "Abierto a todos los niveles — Especializado en combate a media y larga distancia",
        "description": (
            "Reserva natural boscosa de Priozersk rodeando un gran lago y el aserradero central. "
            "Combina líneas de tiro de más de 300 metros ideales para francotiradores con campamentos "
            "médicos, aldeas abandonadas y búnkeres subterráneos. ¡Precaución con los campos minados "
            "en el borde oeste y alrededor del campamento USEC!"
        ),
        "bosses": [
            "Shturman y 2 Guardias (75% PvE / 60% PvP — Aserradero Central / Sawmill)",
            "The Goons (25% PvE / 20% PvP — Scav Bunker y Antena de Radio)",
            "Partisan (25% PvE / 25% PvP — Bosques densos alrededor del Aserradero y Checkpoint)",
            "Cultistas (30% Noche — Sunken Village y Círculo Ritual cerca de Scav House)"
        ],
        "extractions": [
            {"name": "Outskirts (Afueras)", "faction": "PMC / Scav", "req": "Siempre abierto para spawns del lado Este/Norte"},
            {"name": "UN Roadblock / Northern UN Roadblock", "faction": "PMC / Scav", "req": "Siempre abierto para spawns del lado Oeste"},
            {"name": "ZB-014", "faction": "PMC", "req": "Requiere llave ZB-014 si sale humo verde en el búnker"},
            {"name": "ZB-016", "faction": "PMC", "req": "Disponible si la bengala verde exterior está encendida"},
            {"name": "Bridge V-Ex (Puente Norte)", "faction": "PMC (Vehículo)", "req": "5,000 Rublos por jugador en el pueblo del norte"},
            {"name": "Factory Gate (Co-Op)", "faction": "Co-Op", "req": "Requiere 1 PMC + 1 Scav en el portón sureste"}
        ],
        "transits": [
            "Transit a Factory (Portón Factory Gate al sureste)",
            "Transit a Reserve (Camino sureste hacia la base militar)",
            "Transit a Lighthouse (Sendero suroeste pasando Outskirts)"
        ],
        "keys": [
            "Shturman's Stash Key (Abre el cofre común del jefe en el centro del Aserradero)",
            "ZB-014 Key (Extracción segura + spawns de cargadores de 60 balas de 5.45)",
            "Yotota Car Key (Camioneta de Shturman)"
        ],
        "hotspots": [
            "Aserradero Central / Sawmill (Shturman, 3 cabañas con cajas fuertes y archivos)",
            "Campamento USEC (Mesas médicas con Salewas/LEDX y cajas de armas M4 — ojo a las minas)",
            "Campamento Médico EMERCOM (Abundantes suministros médicos, stims y comida)",
            "Pueblo Inundado (Sunken Village) y Aldea del Puente Norte (Objetos de valor y oro)"
        ]
    },
    "factory": {
        "key": "factory",
        "name": "Factory",
        "aliases": ["factory", "fabrica", "factory4_day", "factory4_night"],
        "raid_duration": "20 min (Día) / 25 min (Noche)",
        "players": "5 - 6 PMCs",
        "level_note": "Mapa CQC más pequeño e intenso del juego — Acción inmediata en los primeros 15 segundos",
        "description": (
            "Planta química #16 de Polikhim. Un complejo cerrado de tres niveles con pasarelas "
            "metálicas superiores, oficinas centrales en el tercer piso, vestuarios en el segundo "
            "y una red de túneles subterráneos ampliada. Ideal para completar misiones de combate "
            "cuerpo a cuerpo de Prapor y Jaeger."
        ),
        "bosses": [
            "Tagilla (50% Día / 75% Noche en PvE/PvP — Túneles subterráneos, Silos y Oficinas)",
            "Cultistas (20% Noche — Zonas oscuras de planta baja)"
        ],
        "extractions": [
            {"name": "Gate 3 (Portón 3)", "faction": "PMC / Scav", "req": "Siempre abierto (Sin llave — cuidado con campers)"},
            {"name": "Gate 0 (Portón 0)", "faction": "PMC / Scav", "req": "Requiere Factory Emergency Exit Key (Lado oeste)"},
            {"name": "Cellars (Sótanos)", "faction": "PMC", "req": "Requiere Factory Emergency Exit Key (Rampa subterránea)"},
            {"name": "Courtyard Gate", "faction": "PMC", "req": "Salida exterior en el patio ampliado"},
            {"name": "Med Tent Gate", "faction": "PMC / Scav", "req": "Requiere Factory Emergency Exit Key"},
            {"name": "Camera Bunker Door / Office Window", "faction": "Scav", "req": "Extracciones exclusivas para Player Scav"}
        ],
        "transits": [
            "Transit a Customs (Portón exterior hacia la zona industrial)",
            "Transit a Woods (Portón exterior secundario)",
            "Transit a The Lab (Acceso oculto subterráneo)"
        ],
        "keys": [
            "Factory Emergency Exit Key (Imprescindible: abre 3 extracciones seguras y la habitación cerrada del 3er piso)",
            "Pumping Station Front / Back Door Key (Para misión 'Sanitary Standards')"
        ],
        "hotspots": [
            "Oficinas del 3er Piso (Caja fuerte, archivadores, chaquetas y peleas constantes de PMCs)",
            "Carpa Médica (Med Tent) y Laboratorio Subterráneo (Estimulantes y botiquines)",
            "Vestuarios del 2do piso y Sala de Bombeo (Spawns de objetos raros en estanterías)"
        ]
    },
    "interchange": {
        "key": "interchange",
        "name": "Interchange",
        "aliases": ["interchange", "intercambio", "ultra"],
        "raid_duration": "40 min",
        "players": "10 - 14 PMCs",
        "level_note": "Centro comercial gigante — Mejor mapa para electrónica, GPUs, comida y suministros de Hideout",
        "description": (
            "El megacentro comercial ULTRA en el cruce de autopistas al sur de Tarkov. "
            "Cuenta con estacionamiento subterráneo completo, dos plantas comerciales con más de "
            "80 locales (incluyendo las supertiendas OLI, IDEA y Goshan) y una central eléctrica "
            "exterior que alimenta los sistemas de seguridad y alarmas del complejo."
        ),
        "bosses": [
            "Killa (75% PvE / 60% PvP — Pasillos centrales frente a Kiba/Brutal, OLI, IDEA, Goshan y estacionamiento)",
            "Tagilla (75% PvE/PvP — Patrullas interiores y zonas de carga del centro comercial)"
        ],
        "extractions": [
            {"name": "Emercom Checkpoint", "faction": "PMC / Scav", "req": "Siempre abierto para spawns del Noroeste (Rampa sureste)"},
            {"name": "Railway Exfil (Vías del Tren)", "faction": "PMC / Scav", "req": "Siempre abierto para spawns del Sureste (Extremo noroeste)"},
            {"name": "Power Station V-Ex (Vehículo)", "faction": "PMC (Vehículo)", "req": "5,000 Rublos por jugador detrás de la Central Eléctrica"},
            {"name": "Hole in the Fence", "faction": "PMC", "req": "Siempre abierto PERO requiere desequiparse la mochila (Sin Backpack)"},
            {"name": "Saferoom Exfil (#11SR)", "faction": "PMC", "req": "Encender electricidad + deslizar tarjeta #11SR en el baño de Burger Spot"},
            {"name": "Scav Camp (Co-Op)", "faction": "Co-Op", "req": "Requiere 1 PMC + 1 Scav en el campamento lateral"}
        ],
        "transits": [
            "Transit a Customs (Final de la autopista norte)",
            "Transit a Streets of Tarkov (Cruce de autopista hacia el centro urbano)"
        ],
        "keys": [
            "ULTRA Medical Storage Key (Sala médica frente a Techlight — alta probabilidad de LEDX y Defibrillator)",
            "KIBA Arms Outer Door Key + Grate Door Key (Armería blindada central con armas modificadas y placas)",
            "Object #11SR Keycard (Habitación segura en el estacionamiento con extracción propia y loot de electrónica)",
            "Emercom Medical Unit Key y Pharmacy Key (Salas médicas de planta baja)"
        ],
        "hotspots": [
            "Tiendas de Electrónica: Techlight, Rasmussen, Texho y German (Tarjetas gráficas GPU y Tetriz)",
            "Goshan (Pasillo izquierdo lleno de conservas Tushonka para Jaeger y depósitos traseros)",
            "OLI e IDEA (Motores, filtros de agua, mangueras, taladros y estatuillas de león/gato)",
            "Central Eléctrica (Power Station — Cajas de computadoras, interruptor del mapa y extracción en auto)"
        ]
    },
    "shoreline": {
        "key": "shoreline",
        "name": "Shoreline",
        "aliases": ["shoreline", "costa"],
        "raid_duration": "45 min",
        "players": "10 - 13 PMCs",
        "level_note": "El Resort de Salud ('Azure Coast') concentra el combate más lucrativo de llaves del juego",
        "description": (
            "Franja costera que conecta el puerto con la zona residencial y el famoso complejo "
            "balneario 'Azure Coast Health Resort' (dividido en Ala Oeste, Ala Este y Edificio "
            "Administrativo). Fuera del Resort incluye la Estación Meteorológica, la Planta Hidroeléctrica, "
            "el Muelle (Pier), la Aldea, el Pantano y la nueva Granja de Contrabandistas al noreste."
        ),
        "bosses": [
            "Sanitar y 2 Guardias Médicos (75% PvE / 60% PvP — Health Resort, Muelle/Pier o Villas/Cottages)",
            "The Goons (30% PvE / 20% PvP — Estación Meteorológica / Weather Station)",
            "Partisan (25% PvE / 25% PvP — Colinas boscosas y rutas hacia extracciones)",
            "Cultistas (25% Noche — Pantano / Swamp y jardines del Resort)"
        ],
        "extractions": [
            {"name": "Tunnel (Túnel)", "faction": "PMC", "req": "Siempre abierto para spawns del lado Este"},
            {"name": "Road to Customs", "faction": "PMC / Scav", "req": "Siempre abierto para spawns del lado Oeste"},
            {"name": "Path to Lighthouse", "faction": "PMC / Scav", "req": "Siempre abierto para TODOS los PMCs (Noroeste detrás del pantano)"},
            {"name": "Climber's Trail (Red Rebel)", "faction": "PMC", "req": "Requiere Red Rebel Ice Pick + Paracord y sin chaleco blindado (Norte del Resort)"},
            {"name": "Road to North V-Ex (Vehículo)", "faction": "PMC (Vehículo)", "req": "5,000 Rublos en el extremo norte de la carretera"},
            {"name": "Pier Boat (Barco del Muelle)", "faction": "PMC", "req": "Disponible en la punta del muelle si el faro pequeño titila"}
        ],
        "transits": [
            "Transit a Lighthouse (Sendero noroeste en Path to Lighthouse)",
            "Transit a Customs (Carretera este en Road to Customs)"
        ],
        "keys": [
            "Health Resort East Wing 226/222, 110 (Sanitar's Office) y 310 (LEDX, estimulantes, oro y bitcoins)",
            "Health Resort West Wing 301, 216, 205 y 104 (Mejores habitaciones de LEDX y armamento del Ala Oeste)",
            "Cottage Back Door Key + Cottage Safe Key (4 cajas fuertes en las Villas)",
            "HEPS Storage Key (Depósito de armas de la Planta Hidroeléctrica)"
        ],
        "hotspots": [
            "Health Resort (Ala Este y Ala Oeste — más de 30 habitaciones con llave, LEDX y Red Keycard spawns)",
            "Granja de Contrabandistas (Smuggler's Base — Noreste del mapa, abundante loot técnico y militar)",
            "Villas (Cottages) y Pueblo Abandonado (Chaquetas con llaves raras y cajas fuertes)",
            "Muelle (Pier) y Estación Meteorológica (Cajas fuertes, archivadores y Bosses)"
        ]
    },
    "reserve": {
        "key": "reserve",
        "name": "Reserve",
        "aliases": ["reserve", "rezervbase", "base militar"],
        "raid_duration": "40 min",
        "players": "9 - 12 PMCs",
        "level_note": "Extracciones de PMC con condiciones especiales — Excelente para tecnología militar, munición y Raiders",
        "description": (
            "Base secreta de la Reserva Estatal Federal. Cuenta con cuarteles identificados por piezas "
            "de ajedrez (King, Queen/Dome, Black/White Bishop, Black/White Pawn, Black/White Knight), "
            "una estación de tren blindado y un vasto complejo de búnkeres subterráneos interconectados "
            "donde patrullan Raiders al accionar el interruptor de corriente D-2."
        ),
        "bosses": [
            "Glukhar y 6 Guardias Tácticos (60% PvE / 60% PvP — Edificios Pawn, Bishop, Caballos o Estación de Trenes)",
            "Raiders (Aparecen en el Búnker Subterráneo y al sonar la sirena del Búnker Hermético / Tren)"
        ],
        "extractions": [
            {"name": "D-2 (Búnker Subterráneo)", "faction": "PMC", "req": "Activar electricidad en la sala de mando subterránea y abrir la compuerta D-2"},
            {"name": "Cliff Descent (Bajo el Domo)", "faction": "PMC", "req": "Requiere Red Rebel Ice Pick + Paracord y NO llevar chaleco blindado (Sí permite rig blindado)"},
            {"name": "Sewer Manhole (Alcantarilla)", "faction": "PMC", "req": "Siempre abierto PERO requiere desequiparse la mochila (Sin Backpack)"},
            {"name": "Bunker Hermetic Door", "faction": "PMC / Scav", "req": "Activar la palanca de la Sirena cerca de White Pawn y extraer antes de que pare"},
            {"name": "Armored Train (Tren Blindado)", "faction": "PMC / Scav", "req": "Llega entre el min 25 y 30, toca bocina y parte 7 minutos después"},
            {"name": "Scav Lands (Co-Op)", "faction": "Co-Op", "req": "Requiere 1 PMC + 1 Scav"},
            {"name": "Heating Pipe / Checkpoint Fence / Hole in Wall", "faction": "Scav", "req": "Extracciones rápidas y abiertas para Player Scav"}
        ],
        "transits": [
            "Transit a Woods (Noroeste detrás del Domo / bunkers)",
            "Transit a Customs (Noreste cerca de las vías del tren)",
            "Transit a Lighthouse (Oeste detrás de la estación del Tren Blindado)"
        ],
        "keys": [
            "RB-BK, RB-VO y RB-PKPM Marked Keys (Las 3 habitaciones marcadas de Reserve)",
            "RB-ST (Tanque y arsenal en el garaje — requerido para misiones de Prapor/Peacekeeper y muestras AESA)",
            "RB-KSM y RB-SMP (Habitaciones médicas en White Bishop)",
            "RB-PSP1, RB-PSP2, RB-PSV1 y RB-PSV2 (Jaulas de suministros subterráneas bajo los hangares)"
        ],
        "hotspots": [
            "Búnker de Mando Subterráneo (Peleas de PMCs, Raiders, carpetas de Inteligencia y salida D-2)",
            "Edificio Queen / Domo Radar (Cajas fuertes, servidores con Virtex/VPX y punto de francotirador)",
            "Edificio White Bishop / Drop-Down Room (Tecnología militar y suministros médicos)",
            "Cuarteles Black/White Pawn y Black/White Knight (Armeros, munición BS/Igolnik y Glukhar)"
        ]
    },
    "lighthouse": {
        "key": "lighthouse",
        "name": "Lighthouse",
        "aliases": ["lighthouse", "faro"],
        "raid_duration": "40 min",
        "players": "9 - 12 PMCs",
        "level_note": "Hogar de los Rogues (Ex-USEC) al norte y del comerciante in-raid Lightkeeper en la isla del Faro",
        "description": (
            "Carretera costera montañosa flanqueada por mansiones de lujo (Chalets) en el centro, "
            "la Isla del Faro vigilada por Zryachiy al sur y la fortificada Planta de Tratamiento "
            "de Agua (Water Treatment Plant) al norte, defendida por Rogues armados con ametralladoras "
            "calibre .50 y lanzagranadas automáticos en los techos de los 3 edificios."
        ),
        "bosses": [
            "Zryachiy y Cultistas Francotiradores (100% PvE / 100% PvP — Isla del Faro, hostiles si no tienes el DSP codificado)",
            "Rogues / Ex-USEC (100% — Planta de Tratamiento de Agua y techos de los edificios 1, 2 y 3)",
            "The Goons (30% PvE / 20% PvP — Planta de Tratamiento de Agua o Chalet Azul)",
            "Partisan (25% PvE / 25% PvP — Ladera montañosa entre los Chalets)"
        ],
        "extractions": [
            {"name": "Path to Shoreline", "faction": "PMC / Scav", "req": "Siempre abierto en el extremo Sur/Sureste"},
            {"name": "Southern Road", "faction": "PMC / Scav", "req": "Siempre abierto en el extremo Suroeste de la carretera"},
            {"name": "Northern Checkpoint", "faction": "PMC", "req": "Abierto para spawns del Sur (Extremo norte pasando la planta)"},
            {"name": "Road to Military Base V-Ex", "faction": "PMC (Vehículo)", "req": "5,000 Rublos al norte de la Planta de Agua"},
            {"name": "Mountain Pass (Red Rebel)", "faction": "PMC", "req": "Requiere Red Rebel Ice Pick + Paracord y sin chaleco blindado (Detrás de los Chalets)"},
            {"name": "Armored Train (Tren Blindado)", "faction": "PMC / Scav", "req": "Estación ferroviaria al norte de la Planta de Agua"},
            {"name": "Side Tunnel (Co-Op)", "faction": "Co-Op", "req": "Requiere 1 PMC + 1 Scav"}
        ],
        "transits": [
            "Transit a Shoreline (Extremo sur en Path to Shoreline)",
            "Transit a Woods (Sendero montañoso al este)",
            "Transit a Reserve (Estación de tren al noreste)"
        ],
        "keys": [
            "Merin Car Trunk Key (Baúl del auto rojo en el estacionamiento de la playa — Bitcoin, Virtex y stims)",
            "Hillside House Key (Casa de la aldea con spawns de electrónica militar y objetos de valor)",
            "Usek First / Second Safe Key (Cajas fuertes en el Chalet Azul)",
            "Rogue Usec Stash Key y Water Treatment Plant Storage Room Key (Planta de Tratamiento)"
        ],
        "hotspots": [
            "Planta de Tratamiento de Agua (3 edificios con Rogues, Virtex, COFDMs, AESA y múltiples misiones)",
            "Chalet Azul y Chalet Marrón (Spawns de Bitcoin, Virtex, VPX, cajas fuertes y estimulantes raros)",
            "Isla del Faro (Lightkeeper — Requiere transmisor digital DSP codificado para cruzar el puente sin minas)"
        ]
    },
    "streetsoftarkov": {
        "key": "streetsoftarkov",
        "name": "Streets of Tarkov",
        "aliases": ["streetsoftarkov", "streets of tarkov", "streets", "tarkovstreets", "calles de tarkov"],
        "raid_duration": "50 min",
        "players": "12 - 16 PMCs",
        "level_note": "El mapa urbano más denso y rico en botín del juego — Cuenta con servicio de transporte blindado BTR",
        "description": (
            "El corazón metropolitano de Tarkov. Una cuadrícula urbana masiva con bancos, hoteles (Pinewood), "
            "la concesionaria fortificada LexOs, la fábrica abandonada Chekannaya, el centro comercial "
            "Klimov, la Academia Policial MVD y edificios de departamentos de varios pisos. "
            "El vehículo blindado BTR-82A recorre las avenidas ofreciendo transporte y extracción de botín."
        ),
        "bosses": [
            "Kaban y 6 Guardias / Francotiradores (75% PvE / 60% PvP — Concesionaria LexOs con perímetro minado)",
            "Kollontay y Guardias Antidisturbios (75% PvE / 60% PvP — Centro Comercial Klimov o Academia del MVD)",
            "Killa y Glukhar (Pueden aparecer ocasionalmente en eventos o zonas residenciales)"
        ],
        "extractions": [
            {"name": "Klimov Street (Bengala Verde)", "faction": "PMC / Scav", "req": "Disparar bengala verde en la zona de señal frente a Klimov antes de cruzar la calle"},
            {"name": "Primorsky Ave Taxi V-Ex", "faction": "PMC (Vehículo)", "req": "5,000 Rublos por jugador en el extremo norte de la avenida"},
            {"name": "Courtyard / Evacuation Zone / Ruined House", "faction": "PMC", "req": "Extracciones condicionales en las esquinas opuestas a tu spawn"},
            {"name": "Sewer River / Damaged House / Expo Checkpoint", "faction": "PMC", "req": "Extracciones estándar del perímetro"},
            {"name": "Pinewood Basement (Co-Op)", "faction": "Co-Op", "req": "Requiere 1 PMC + 1 Scav en el sótano del hotel Pinewood"},
            {"name": "Ventilation Shaft / Entrance to Catacombs", "faction": "Scav", "req": "Extracciones rápidas de Player Scav"}
        ],
        "transits": [
            "Transit a Ground Zero (Calle comercial al sureste)",
            "Transit a Interchange (Avenida sur)",
            "Transit a The Lab (Entrada subterránea secreta bajo el complejo urbano)"
        ],
        "keys": [
            "Abandoned Factory Marked Key y Chekannaya 13 Marked Key (Habitaciones marcadas con Keycards y Cases)",
            "Chekannaya 15 Apartment Key (Uno de los apartamentos más ricos en oro, Bitcoins y objetos de valor)",
            "LexOs Car Dealership Director's Office Key + Aspect Key (Botín exclusivo tras derrotar a Kaban)",
            "Relaxation Room Key (Llave con spawn 100% garantizado en raid — sala repleta de Moonshine y Bitcoins)"
        ],
        "hotspots": [
            "Concesionaria LexOs (Base de Kaban, contenedores de armas, oficina cerrada y garajes)",
            "Edificio Chekannaya 15 y Fábrica Abandonada (Múltiples habitaciones de alto valor y oficina de correos)",
            "Oficina de Desarrolladores y Sala Relaxation (Loot garantizado de bebidas alcohólicas y figuritas)",
            "Centro Comercial Klimov, Hotel Pinewood y Banco Tarbank (Cajas fuertes, registradoras y Kollontay)"
        ]
    },
    "lab": {
        "key": "lab",
        "name": "The Lab",
        "aliases": ["lab", "the lab", "thelab", "labs", "laboratory"],
        "raid_duration": "35 min",
        "players": "6 - 10 PMCs",
        "level_note": "Requiere 1x TerraGroup Labs Access Keycard por entrada — No existen Player Scavs ni Seguro (Insurance)",
        "description": (
            "Complejo de investigación subterráneo ultrasecreto de TerraGroup Labs bajo el centro de Tarkov. "
            "Dividido en Nivel Técnico (Sótanos y conductos), Nivel 1 (Hangares de carga y estacionamiento, "
            "laboratorios médicos) y Nivel 2 (Oficinas gerenciales, Domo central y salas de servidores). "
            "Al accionar los interruptores de extracción, escuadrones de Raiders de élite entran al mapa."
        ),
        "bosses": [
            "Raiders de TerraGroup Labs (Aparecen en oleadas al activar portones, ascensores o alarmas)"
        ],
        "extractions": [
            {"name": "Cargo Elevator / Main Elevator / Medical Block Elevator", "faction": "PMC", "req": "Encender el generador del ascensor respectivo en el sótano técnico y llamar al ascensor"},
            {"name": "Parking Gate / Hangar Gate", "faction": "PMC", "req": "Presionar el botón de apertura del portón en las salas de control (Spawnea Raiders)"},
            {"name": "Ventilation Shaft (Conducto)", "faction": "PMC", "req": "Siempre abierto PERO requiere desequiparse la mochila (Sin Backpack)"},
            {"name": "Sewage Conduit (Alcantarillado)", "faction": "PMC", "req": "Abrir válvula en el sótano inundado y esperar a que baje el nivel del agua"}
        ],
        "transits": [
            "Acceso desde Streets of Tarkov o Factory"
        ],
        "keys": [
            "Black Keycard (Sala de experimentación G12 — 15+ inyectores/stims y múltiples spawns de LEDX)",
            "Yellow Keycard y Violet Keycard (Salas de seguridad con armas de alta gama, Bitcoins y electrónica)",
            "Red Keycard, Green Keycard y Blue Keycard (Salas restringidas de alto nivel del complejo)",
            "TerraGroup Labs Weapon Testing Area Key y Manager's Office Key (Acceso directo en el centro del mapa)"
        ],
        "hotspots": [
            "Sala Black Keycard (El mejor punto del juego para farmear estimulantes y LEDX)",
            "Oficinas de Gerencia (Manager's Office), Sala Violeta y Sala Amarilla (Objetos de valor y tecnología)",
            "Domo Central de Pruebas y Nueva Área de Contención Residencial (Blue/Black wing)"
        ]
    },
    "icebreaker": {
        "key": "icebreaker",
        "name": "Icebreaker",
        "aliases": ["icebreaker", "rompehielos", "boreas", "paradigm"],
        "raid_duration": "50 min",
        "players": "1 - 3 PMCs",
        "level_note": "Rompehielos Nuclear Boreas (34x168 m) — Sin seguro (No Insurance) — Mapa re3mr.com v1.7",
        "description": (
            "El gigantesco buque rompehielos a propulsión nuclear Boreas de Paradigm Shipping encallado en el Golfo de Finlandia. "
            "Estructura naval vertical de 14 niveles (desde el Deck 10 Bridge Roof hasta el Deck -3 Lower Automation). "
            "Custodiado por escuadrones tácticos de Black Division, el comandante The Wedge y Knight."
        ),
        "bosses": [
            "The Wedge (100% PvE / 100% PvP — Comandante en Jefe en Deck -2 Engine Room y Deck 9 Bridge)",
            "Knight (Rogue Boss — Patrullas tácticas de cubierta)"
        ],
        "extractions": [
            {"name": "Helicopter Extraction (Helipuerto Deck 2)", "faction": "PMC", "req": "Disparar bengala verde (Green Flare) en la zona de señal del helipuerto + pagar 2450 EUR por jugador"}
        ],
        "transits": [
            "Transit a The Lab (Conducto sumergido de refrigeración)",
            "Transit a Lighthouse (Pista de hielo costera hacia el sur)"
        ],
        "keys": [
            "Boreas Crew Quarters Keycard & Engine Room Keycard",
            "Compartment C-1 Keycard & Compartment C-3 Keycard",
            "SZ-1 Explosive Charge & BBQ-543 Gas Torch (Apertura de compuertas blindadas)",
            "RSP-30 Reactive Signal Cartridge (Bengala verde)",
            "Código de Teclado de Seguridad del Tablón de Anuncios (Bulletin Board Keypad)"
        ],
        "hotspots": [
            "Helipuerto Deck 2 (Extracción única por llamada de helicóptero)",
            "Deck 9 Bridge & Deck 10 Bridge Roof (Sistemas de radar y navegación)",
            "Deck 7 Officers Deck & Deck 3 Gym/Canteen (Habitaciones de oficiales y cajas fuertes)",
            "Deck 0 Storage & Security (Bóvedas acorazadas y armería)",
            "Deck -2 Engine Room & Deck -3 Lower Automation (Reactores y generadores nucleares)"
        ]
    },
    "labyrinth": {
        "key": "labyrinth",
        "name": "The Labyrinth",
        "aliases": ["labyrinth", "laberinto", "subterraneo", "bunker_complex"],
        "raid_duration": "30 min",
        "players": "1 - 5 PMCs",
        "level_note": "Búnker Laberíntico Profundo (118x110 m) — Sin seguro (No Insurance) — Mapa re3mr.com v0.7",
        "description": (
            "Un intrincado búnker subterráneo de túneles secretos y cámaras de prueba de TerraGroup (118x110 m). "
            "Al entrar al centro de la instalación se activa la alarma acústica que atrae patrullas enemigas. "
            "Cuenta con 5 cámaras con puzzles de peligro ambiental (fuego, vapor, gas y trampa de escopeta)."
        ),
        "bosses": [
            "Vengeful Killa (Merodea en cualquier zona del laberinto)",
            "Shadow of Tagilla (Armado con maza pesada en los pasillos estrechos)"
        ],
        "extractions": [
            {"name": "The Way Up (Túneles Oeste)", "faction": "PMC", "req": "Extracción principal abierta tras 15 minutos de raid"},
            {"name": "Ariadne's Path (Túneles Sur - Oculta)", "faction": "PMC", "req": "Requiere 'Ariadne's Symbol Key' en la puerta de la sala de tortura"}
        ],
        "transits": [
            "Transit a Reserve (Búnker subterráneo D-2)",
            "Transit a Ground Zero (Acceso por conductos de estacionamiento)"
        ],
        "keys": [
            "Ariadne's Symbol Key (Extracción secreta Ariadne's Path)",
            "Corpse Room Key (Acceso a la sala de cadáveres y alijos)",
            "Labrys Research Notes (Notas de investigación de TerraGroup)",
            "Figurines & Scientist Corpses (Objetivos de la misión de historia)"
        ],
        "hotspots": [
            "Alarm Trigger Zone & Assembly Room (Zona central con prototipo de bomba)",
            "Chamber 1: Toxic Pool (Bomba de drenaje y llave 1)",
            "Chamber 2: Steam Hazard (Puzzles de válvulas de vapor y llave 2)",
            "Chamber 3: Fire Hazard (Interruptor de supresión de fuego y llave 3)",
            "Chamber 4: Shotgun Trap (Palanca de desactivación y llave 4)",
            "Chamber 5: Toxic Puddle (Soplete de gas y compuerta metálica)",
            "Torture Room & Observation Room (Habitaciones selladas de alta seguridad)"
        ]
    }
}


def normalize_map_key(name: str) -> str:
    """Normaliza cualquier nombre o alias de mapa a su clave canónica."""
    if not name:
        return "customs"
    clean = name.lower().strip()
    if clean in MAPS_TACTICAL_DATA:
        return clean
    for key, data in MAPS_TACTICAL_DATA.items():
        if clean in data.get("aliases", []) or clean in data["name"].lower():
            return key
    compact = clean.replace(" ", "").replace("_", "").replace("-", "")
    if "groundzero" in compact or "sandbox" in compact:
        return "groundzero"
    if "street" in compact:
        return "streetsoftarkov"
    if "icebreaker" in compact or "boreas" in compact or "rompehielos" in compact:
        return "icebreaker"
    if "labyrinth" in compact or "laberinto" in compact:
        return "labyrinth"
    if "lab" in compact:
        return "lab"
    if "factory" in compact:
        return "factory"
    if "custom" in compact:
        return "customs"
    if "wood" in compact:
        return "woods"
    if "shore" in compact:
        return "shoreline"
    if "inter" in compact:
        return "interchange"
    if "reserv" in compact or "rezerv" in compact:
        return "reserve"
    if "light" in compact:
        return "lighthouse"
    return "customs"


def get_enriched_map_data(raw_map: Dict[str, Any]) -> Dict[str, Any]:
    """Combina los datos de SQLite con la base táctica curada."""
    key = normalize_map_key(raw_map.get("key") or raw_map.get("name", ""))
    curated = MAPS_TACTICAL_DATA.get(key, {})
    return {
        "id": raw_map.get("id", key),
        "key": key,
        "name": curated.get("name") or raw_map.get("name", key.title()),
        "raid_duration": curated.get("raid_duration") or (
            f"{raw_map['raid_duration']} min" if raw_map.get("raid_duration") else "40 min"
        ),
        "players": curated.get("players", "10 - 12 PMCs"),
        "level_note": curated.get("level_note", "Abierto a todos los niveles"),
        "description": curated.get("description") or raw_map.get("description") or "Mapa táctico de Escape from Tarkov.",
        "bosses": curated.get("bosses", []),
        "extractions": curated.get("extractions", []),
        "transits": curated.get("transits", []),
        "keys": curated.get("keys", []),
        "hotspots": curated.get("hotspots", [])
    }


MAP_EXTRACTIONS_COORDS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "groundzero": {
        "emercom": (0.52, 0.12),
        "nakatani": (0.48, 0.88),
        "police": (0.32, 0.38),
        "mira": (0.84, 0.45),
        "scav": (0.68, 0.22),
        "tartowers": (0.36, 0.68),
    },
    "customs": {
        "zb-1011": (0.92, 0.72),
        "crossroads": (0.08, 0.42),
        "trailer": (0.08, 0.45),
        "dorms": (0.47, 0.82),
        "zb-1013": (0.49, 0.38),
        "old gas": (0.64, 0.62),
        "zb-1012": (0.65, 0.58),
        "smuggler": (0.38, 0.52),
        "railroad": (0.68, 0.38),
        "boiler": (0.86, 0.65),
        "admin": (0.90, 0.40),
        "shacks": (0.88, 0.35),
    },
    "woods": {
        "outskirts": (0.12, 0.82),
        "un roadblock": (0.88, 0.22),
        "bridge": (0.58, 0.12),
        "zb-014": (0.24, 0.72),
        "zb-016": (0.68, 0.45),
        "northern": (0.82, 0.15),
        "factory": (0.75, 0.65),
        "boat": (0.38, 0.76),
        "dead man": (0.36, 0.80),
    },
    "factory": {
        "gate 3": (0.18, 0.82),
        "gate 0": (0.15, 0.22),
        "cellars": (0.68, 0.78),
        "courtyard": (0.48, 0.88),
        "med tent": (0.82, 0.48),
        "camera": (0.35, 0.65),
        "office": (0.50, 0.35),
    },
    "interchange": {
        "railway": (0.12, 0.22),
        "emercom": (0.88, 0.80),
        "hole": (0.34, 0.14),
        "power station": (0.78, 0.20),
        "saferoom": (0.52, 0.54),
        "scav camp": (0.50, 0.85),
    },
    "shoreline": {
        "road to customs": (0.92, 0.48),
        "tunnel": (0.08, 0.78),
        "lighthouse": (0.08, 0.22),
        "pier": (0.48, 0.88),
        "cottage": (0.28, 0.58),
        "ccp": (0.82, 0.82),
        "adm": (0.55, 0.42),
    },
    "reserve": {
        "cliff": (0.22, 0.82),
        "d-2": (0.42, 0.68),
        "hermetic": (0.78, 0.72),
        "sewer": (0.54, 0.48),
        "scav lands": (0.72, 0.25),
        "hole in wall": (0.25, 0.25),
        "depot": (0.65, 0.35),
    },
    "lighthouse": {
        "southern": (0.55, 0.90),
        "shoreline": (0.82, 0.60),
        "military base": (0.42, 0.15),
        "mountain": (0.72, 0.40),
        "industrial": (0.35, 0.32),
        "hideout": (0.48, 0.45),
    },
    "streetsoftarkov": {
        "courtyard": (0.48, 0.68),
        "evacuation": (0.72, 0.78),
        "klimov": (0.55, 0.18),
        "underpass": (0.38, 0.45),
        "taxi": (0.28, 0.82),
        "pinewood": (0.62, 0.45),
        "cardinal": (0.32, 0.25),
        "damaged house": (0.75, 0.35),
    },
    "lab": {
        "cargo": (0.28, 0.35),
        "main": (0.72, 0.35),
        "medical": (0.68, 0.72),
        "sewage": (0.32, 0.72),
        "hangar": (0.18, 0.50),
        "parking": (0.82, 0.50),
        "ventilation": (0.50, 0.50),
    },
    "icebreaker": {
        "helicopter": (0.60, 0.15),
        "helipad": (0.60, 0.15),
    },
    "labyrinth": {
        "the way up": (0.75, 0.44),
        "way up": (0.75, 0.44),
        "ariadne": (0.47, 0.63),
    }
}


def get_map_extractions_with_coords(map_id: str) -> List[Dict[str, Any]]:
    """Retorna las extracciones del mapa con coordenadas calibradas (x, y) y tipo de facción."""
    norm_key = normalize_map_key(map_id)
    curated = MAPS_TACTICAL_DATA.get(norm_key, {})
    raw_extracts = curated.get("extractions", [])
    coords_dict = MAP_EXTRACTIONS_COORDS.get(norm_key, {})

    results = []
    fallback_angles = [0.15, 0.85, 0.50, 0.30, 0.70, 0.20, 0.80, 0.40, 0.60]

    for idx, ex in enumerate(raw_extracts):
        name = ex.get("name", "")
        faction = ex.get("faction", "PMC")
        name_lower = name.lower()

        x_pct, y_pct = None, None
        for k, (kx, ky) in coords_dict.items():
            if k in name_lower:
                x_pct, y_pct = kx, ky
                break

        if x_pct is None:
            f_val = fallback_angles[idx % len(fallback_angles)]
            x_pct, y_pct = (f_val, 0.88 if idx % 2 == 0 else 0.12)

        is_scav = "scav" in faction.lower() and "pmc" not in faction.lower()
        is_pmc = "pmc" in faction.lower() or "co-op" in faction.lower() or not is_scav

        results.append({
            "name": name,
            "faction": faction,
            "req": ex.get("req", ""),
            "x": float(x_pct),
            "y": float(y_pct),
            "is_pmc": is_pmc,
            "is_scav": is_scav
        })
    return results


MAP_TACTICAL_POIS: Dict[str, List[Dict[str, Any]]] = {
    "groundzero": [
        {"name": "Oficina Científica TerraGroup (Llave)", "type": "key", "x": 0.44, "y": 0.42},
        {"name": "Cuarto Subterráneo Utility (Llave)", "type": "key", "x": 0.52, "y": 0.56},
        {"name": "Cajas Fuertes Banco Capital Insight", "type": "loot", "x": 0.62, "y": 0.36},
        {"name": "Suministros Médicos Skyside / Emercom", "type": "loot", "x": 0.36, "y": 0.25},
    ],
    "customs": [
        {"name": "Dorm 314 Marked Room (Ritual)", "type": "key", "x": 0.46, "y": 0.74},
        {"name": "Dorm 206 / 114 / 214 (Quests & Caja Fuerte)", "type": "key", "x": 0.49, "y": 0.70},
        {"name": "Director's Office Key (Big Red)", "type": "key", "x": 0.17, "y": 0.54},
        {"name": "Factory Exit Key (Atajo Gas / ZB-013)", "type": "key", "x": 0.48, "y": 0.39},
        {"name": "Crackhouse (Inteligencia & Morfinas)", "type": "loot", "x": 0.39, "y": 0.36},
        {"name": "5x Cajas Fuertes de Dorms", "type": "loot", "x": 0.47, "y": 0.72},
        {"name": "Alijos Ocultos (Stashes de Bosque)", "type": "loot", "x": 0.66, "y": 0.68},
    ],
    "woods": [
        {"name": "Cofre de Shturman (Shturman Key)", "type": "key", "x": 0.44, "y": 0.63},
        {"name": "Búnker ZB-014 (Llave ZB-014)", "type": "key", "x": 0.24, "y": 0.70},
        {"name": "Campamento USEC (LEDX / Armas)", "type": "loot", "x": 0.27, "y": 0.38},
        {"name": "Campamento Médico EMERCOM (Salewas)", "type": "loot", "x": 0.63, "y": 0.67},
        {"name": "Sunken Village (Oro & Objetos Raros)", "type": "loot", "x": 0.44, "y": 0.18},
    ],
    "factory": [
        {"name": "Oficina Cerrada Factory Exit Key", "type": "key", "x": 0.11, "y": 0.35},
        {"name": "Pumping Station Key", "type": "key", "x": 0.56, "y": 0.46},
        {"name": "Caja Fuerte & Archivadores 3er Piso", "type": "loot", "x": 0.09, "y": 0.41},
        {"name": "Carpa Médica (Med Tent)", "type": "loot", "x": 0.64, "y": 0.42},
    ],
    "shoreline": [
        {"name": "Resort West 301 / 216 (LEDX & Armas)", "type": "key", "x": 0.36, "y": 0.46},
        {"name": "Resort East 226 / 110 Sanitar (LEDX)", "type": "key", "x": 0.45, "y": 0.46},
        {"name": "Cottage Back Door & Safe Key", "type": "key", "x": 0.22, "y": 0.60},
        {"name": "2x Cajas Fuertes del Muelle (Pier)", "type": "loot", "x": 0.44, "y": 0.86},
        {"name": "Base de Contrabandistas (Noreste)", "type": "loot", "x": 0.66, "y": 0.24},
    ],
    "interchange": [
        {"name": "Tienda de Armas KIBA (2 Llaves)", "type": "key", "x": 0.78, "y": 0.49},
        {"name": "Farmacia ULTRA Medical (LEDX)", "type": "key", "x": 0.76, "y": 0.34},
        {"name": "11SR Saferoom / Object #11SR", "type": "key", "x": 0.80, "y": 0.54},
        {"name": "Techlight / Texho / Rasmussen (GPUs)", "type": "loot", "x": 0.79, "y": 0.39},
        {"name": "Oficinas de IDEA & Goshan (PCs)", "type": "loot", "x": 0.82, "y": 0.28},
    ],
    "reserve": [
        {"name": "RB-BK Marked Room (Black Pawn)", "type": "key", "x": 0.45, "y": 0.56},
        {"name": "RB-VO Marked Room (Barracks)", "type": "key", "x": 0.68, "y": 0.65},
        {"name": "RB-PKPM Marked Room (Búnker)", "type": "key", "x": 0.43, "y": 0.49},
        {"name": "Servidores King (Virtex / COFDM / GPU)", "type": "loot", "x": 0.42, "y": 0.44},
        {"name": "Domo del Radar (Caja Fuerte + Guardias)", "type": "loot", "x": 0.28, "y": 0.76},
    ],
    "lighthouse": [
        {"name": "Merin Car Trunk Key (Oro / Bitcoins)", "type": "key", "x": 0.50, "y": 0.66},
        {"name": "Hillside House Key (Objetos Raros)", "type": "key", "x": 0.58, "y": 0.48},
        {"name": "Operating Room Key (Planta de Agua)", "type": "key", "x": 0.52, "y": 0.28},
        {"name": "Chalet Azul & Chalet Sur (Virtex / BTC)", "type": "loot", "x": 0.56, "y": 0.61},
        {"name": "Planta de Tratamiento (Tech & Rogues)", "type": "loot", "x": 0.53, "y": 0.33},
    ],
    "streetsoftarkov": [
        {"name": "Chekannaya 13 Marked Room", "type": "key", "x": 0.35, "y": 0.62},
        {"name": "Abandoned Factory Marked Key", "type": "key", "x": 0.78, "y": 0.62},
        {"name": "Concesionaria LexOs (Aspect / Kaban Keys)", "type": "key", "x": 0.49, "y": 0.66},
        {"name": "Complejo Concordia (Oro & Seguridad)", "type": "loot", "x": 0.22, "y": 0.84},
        {"name": "Oficinas de Correo & Chekannaya 15", "type": "loot", "x": 0.33, "y": 0.68},
    ],
    "lab": [
        {"name": "Black Keycard (Sala de Inyectores / LEDX)", "type": "key", "x": 0.42, "y": 0.68},
        {"name": "Violet & Red Keycard (Seguridad)", "type": "key", "x": 0.76, "y": 0.34},
        {"name": "Green Keycard (Laboratorio Nv.2)", "type": "key", "x": 0.74, "y": 0.52},
        {"name": "Domo Central y Oficinas Cat (LEDX / GPU)", "type": "loot", "x": 0.48, "y": 0.58},
    ],
    "labyrinth": [
        {"name": "Cámara Central de Experimentos (Keycard)", "type": "key", "x": 0.50, "y": 0.48},
        {"name": "Archivos Clasificados Knossos (Loot)", "type": "loot", "x": 0.55, "y": 0.54},
    ],
}


def get_map_tactical_pois(map_id: str) -> List[Dict[str, Any]]:
    """Retorna puntos tácticos de Llaves/Marked Rooms y Zonas de Botín Top con coordenadas calibradas."""
    norm_key = normalize_map_key(map_id)
    return MAP_TACTICAL_POIS.get(norm_key, [])

