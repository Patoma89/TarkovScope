"""TarkovScope - Datos semilla de misiones modernas, etiquetas de objetivos y mapas.
Extraido de database.py.
"""
from typing import Any, Dict, List


MAP_ID_TO_NAME: Dict[int, str] = {
    0: "Factory",
    1: "Customs",
    2: "Woods",
    3: "Shoreline",
    4: "Interchange",
    5: "The Lab",
    6: "Reserve",
    7: "Lighthouse",
    8: "Streets of Tarkov",
    9: "Ground Zero",
    10: "Icebreaker",
    11: "The Labyrinth",
}

OBJECTIVE_TYPE_LABELS_ES: Dict[str, str] = {
    "kill": "Eliminar",
    "collect": "Entregar",
    "find": "Encontrar en Raid (FiR)",
    "pickup": "Recoger objeto de misión",
    "place": "Colocar / Esconder",
    "mark": "Marcar con baliza MS2000",
    "locate": "Localizar zona",
    "key": "Llave requerida",
    "reputation": "Nivel de Lealtad",
    "skill": "Habilidad requerida",
    "build": "Armar / Modificar (Gunsmith)",
    "warning": "Condición especial",
    "survive": "Sobrevivir y extraer",
}

# Misiones requeridas en la cadena hacia Lightkeeper (Network Provider / Getting Acquainted)
LIGHTKEEPER_REQUIRED_TITLES = {
    "broadcast",
    "broadcast - part 1",
    "decontamination service",
    "private clinic",
    "the huntsman path - outcasts",
    "long road",
    "missing cargo",
    "top secret",
    "cargo x - part 4",
    "wet job - part 5",
    "peacekeeping mission",
    "aesthete",
    "gunsmith - part 15",
    "house arrest - part 1",
    "database - part 2",
    "living high is not a crime - part 2",
    "stray dogs",
    "out of curiosity",
    "corporate secrets",
    "drug trafficking",
    "reconnaissance",
    "network provider - part 1",
    "network provider - part 2",
    "assessment - part 1",
    "assessment - part 2",
    "assessment - part 3",
    "key to the tower",
    "getting acquainted",
    "information source",
    "missing informant",
    "snatch",
    "return the favor",
    "payback",
}

# Misiones modernas esenciales (Ground Zero, Streets of Tarkov, Ref y Lightkeeper) con sus correlativas
EXTRA_MODERN_QUESTS: List[Dict[str, Any]] = [
    {
        "id": 9001,
        "title": "Shooting Cans",
        "trader_name": "Prapor",
        "level_req": 1,
        "exp": 1800,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/Shooting_Cans",
        "map_name": "Ground Zero",
        "require": {"level": 1, "quests": []},
        "nokappa": False,
        "objectives": [
            {"type": "locate", "target": "Ametralladora pesada NSV 'Utyos' en el edificio Empire", "number": 1, "location": 9, "map_name": "Ground Zero"},
            {"type": "locate", "target": "Lanzagranadas automático AGS-30 en el edificio Empire", "number": 1, "location": 9, "map_name": "Ground Zero"},
            {"type": "kill", "target": "Cualquier objetivo en Ground Zero", "number": 5, "location": 9, "map_name": "Ground Zero"}
        ]
    },
    {
        "id": 9002,
        "title": "Luxurious Life",
        "trader_name": "Prapor",
        "level_req": 2,
        "exp": 2200,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/Luxurious_Life",
        "map_name": "Ground Zero",
        "require": {"level": 2, "quests": [9001]},
        "nokappa": False,
        "objectives": [
            {"type": "find", "target": "Bottle of Tarkovskaya vodka (En el restaurante Fusion de Ground Zero)", "number": 1, "location": 9, "map_name": "Ground Zero"},
            {"type": "collect", "target": "Bottle of Tarkovskaya vodka", "number": 1, "location": 9, "map_name": "Ground Zero"}
        ]
    },
    {
        "id": 9003,
        "title": "First in Line",
        "trader_name": "Therapist",
        "level_req": 1,
        "exp": 1700,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/First_in_Line",
        "map_name": "Ground Zero",
        "require": {"level": 1, "quests": []},
        "nokappa": False,
        "objectives": [
            {"type": "locate", "target": "Puesto médico de Emercom en la rampa norte de Ground Zero", "number": 1, "location": 9, "map_name": "Ground Zero"},
            {"type": "collect", "target": "Botiquines / Suministros médicos Found in Raid", "number": 3, "location": 9, "map_name": "Ground Zero"}
        ]
    },
    {
        "id": 9004,
        "title": "Burning Rubber",
        "trader_name": "Skier",
        "level_req": 1,
        "exp": 1900,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/Burning_Rubber",
        "map_name": "Ground Zero",
        "require": {"level": 1, "quests": []},
        "nokappa": False,
        "objectives": [
            {"type": "survive", "target": "Extraer usando el vehículo pagado (Police Cordon V-Ex) frente a TerraGroup en Ground Zero", "number": 1, "location": 9, "map_name": "Ground Zero"}
        ]
    },
    {
        "id": 9005,
        "title": "Saving the Mole",
        "trader_name": "Mechanic",
        "level_req": 1,
        "exp": 2500,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/Saving_the_Mole",
        "map_name": "Ground Zero",
        "require": {"level": 1, "quests": []},
        "nokappa": False,
        "objectives": [
            {"type": "locate", "target": "Grupo de científicos de TerraGroup en el estacionamiento de Ground Zero", "number": 1, "location": 9, "map_name": "Ground Zero"},
            {"type": "key", "target": "TerraGroup Science Office Key (En el cuerpo del científico)", "number": 1, "location": 9, "map_name": "Ground Zero"},
            {"type": "pickup", "target": "Disco duro (Hard Drive) en la oficina científica del piso 2 de TerraGroup", "number": 1, "location": 9, "map_name": "Ground Zero"}
        ]
    },
    {
        "id": 9006,
        "title": "The Huntsman Path - Big Game",
        "trader_name": "Jaeger",
        "level_req": 25,
        "exp": 18500,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/The_Huntsman_Path_-_Big_Game",
        "map_name": "Streets of Tarkov",
        "require": {"level": 25, "quests": []},
        "nokappa": True,
        "objectives": [
            {"type": "kill", "target": "Kaban en la concesionaria LexOs", "number": 1, "location": 8, "map_name": "Streets of Tarkov"},
            {"type": "kill", "target": "Basmach y Gus (Guardias de élite de Kaban)", "number": 2, "location": 8, "map_name": "Streets of Tarkov"}
        ]
    },
    {
        "id": 9007,
        "title": "The Huntsman Path - Crooked Cop",
        "trader_name": "Jaeger",
        "level_req": 28,
        "exp": 19000,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/The_Huntsman_Path_-_Crooked_Cop",
        "map_name": "Streets of Tarkov",
        "require": {"level": 28, "quests": [9006]},
        "nokappa": True,
        "objectives": [
            {"type": "kill", "target": "Kollontay en Klimov Mall, Academia MVD o Ground Zero", "number": 1, "location": 8, "map_name": "Streets of Tarkov"},
            {"type": "kill", "target": "Guardias antidisturbios de Kollontay", "number": 3, "location": 8, "map_name": "Streets of Tarkov"}
        ]
    },
    {
        "id": 9008,
        "title": "Easy Money - Part 1",
        "trader_name": "Ref",
        "level_req": 7,
        "exp": 5500,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/Easy_Money_-_Part_1",
        "map_name": "Ground Zero",
        "require": {"level": 7, "quests": []},
        "nokappa": True,
        "objectives": [
            {"type": "place", "target": "Póster de Tarkov Arena en el refugio de Scavs de Ground Zero", "number": 1, "location": 9, "map_name": "Ground Zero"},
            {"type": "place", "target": "Póster de Tarkov Arena en la fortaleza de Customs", "number": 1, "location": 1, "map_name": "Customs"}
        ]
    },
    {
        "id": 9009,
        "title": "To Great Heights! - Part 1",
        "trader_name": "Ref",
        "level_req": 10,
        "exp": 7200,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/To_Great_Heights!_-_Part_1",
        "map_name": "Cualquier Mapa",
        "require": {"level": 10, "quests": [9008]},
        "nokappa": True,
        "objectives": [
            {"type": "kill", "target": "Ganar una partida clasificada en EFT: Arena (Modo TeamFight o BlastGang)", "number": 1, "location": -1, "map_name": "Cualquier Mapa"},
            {"type": "collect", "target": "GP Coin", "number": 5, "location": -1, "map_name": "Cualquier Mapa"}
        ]
    },
    {
        "id": 9010,
        "title": "Balancing - Part 1",
        "trader_name": "Ref",
        "level_req": 12,
        "exp": 8400,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/Balancing_-_Part_1",
        "map_name": "Customs",
        "require": {"level": 12, "quests": [9009]},
        "nokappa": True,
        "objectives": [
            {"type": "kill", "target": "Scavs usando chaleco PACA y rifle Kalashnikov AK-74N", "number": 10, "location": 1, "map_name": "Customs"}
        ]
    },
    {
        "id": 9011,
        "title": "Information Source",
        "trader_name": "Lightkeeper",
        "level_req": 35,
        "exp": 28000,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/Information_Source",
        "map_name": "Lighthouse",
        "require": {"level": 35, "quests": []},
        "nokappa": True,
        "objectives": [
            {"type": "survive", "target": "Extraer mediante vehículos V-Ex en Woods, Customs, Interchange y Streets of Tarkov", "number": 4, "location": 7, "map_name": "Lighthouse"},
            {"type": "locate", "target": "Cruzar a la Isla del Faro con el Transmisor Digital DSP codificado activo", "number": 1, "location": 7, "map_name": "Lighthouse"}
        ]
    },
    {
        "id": 9012,
        "title": "Missing Informant",
        "trader_name": "Lightkeeper",
        "level_req": 36,
        "exp": 32000,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/Missing_Informant",
        "map_name": "Streets of Tarkov",
        "require": {"level": 36, "quests": [9011]},
        "nokappa": True,
        "objectives": [
            {"type": "locate", "target": "Escondite del informante en el edificio Chekannaya 13 de Streets of Tarkov", "number": 1, "location": 8, "map_name": "Streets of Tarkov"},
            {"type": "pickup", "target": "Diario de inteligencia oculto para Lightkeeper", "number": 1, "location": 8, "map_name": "Streets of Tarkov"}
        ]
    },
    {
        "id": 9013,
        "title": "Return the Favor",
        "trader_name": "Lightkeeper",
        "level_req": 38,
        "exp": 38000,
        "wiki_url": "https://escapefromtarkov.fandom.com/wiki/Return_the_Favor",
        "map_name": "Woods",
        "require": {"level": 38, "quests": [9012]},
        "nokappa": True,
        "objectives": [
            {"type": "kill", "target": "PMCs alrededor de la montaña Sniper Rock en Woods", "number": 15, "location": 2, "map_name": "Woods"},
            {"type": "place", "target": "Carpetas de Inteligencia TerraGroup Blue Folders en los puntos indicados", "number": 2, "location": 2, "map_name": "Woods"}
        ]
    }
]
