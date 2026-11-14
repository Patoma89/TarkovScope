"""
TarkovScope - Base de Datos Táctica de Llaves, Keycards & Marked Rooms (Keys & Intel)
Datos estructurados por mapa, categoría, misiones requeridas, loot y spawns.
Incluye descarga asíncrona de iconos oficiales desde tarkov.dev a cache/keys/.
Módulo de lógica pura (sin dependencias de UI).
"""
import html as html_lib
import io
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
from PIL import Image
from typing import List, Dict, Any, Optional, Set, Callable

from core.config import CACHE_DIR, TARKOV_DEV_GRAPHQL_URL

KEYS_DIR = os.path.join(CACHE_DIR, "keys")
os.makedirs(KEYS_DIR, exist_ok=True)
_KEY_ICONS_FETCHING = False
_KEY_ICONS_FETCHED = False

DIRECT_KEY_ICON_URLS: Dict[str, str] = {
    "the_labyrinth_labrys_access_keycard": (
        "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/17/"
        "Labrys_access_keycard_icon.png/revision/latest?cb=20250328181401"
    ),
}


KEY_MAPS_ORDER = [
    "Todos",
    "Customs",
    "Shoreline",
    "Reserve",
    "Streets of Tarkov",
    "Lighthouse",
    "Interchange",
    "Woods",
    "Factory",
    "The Lab",
    "Ground Zero",
    "The Labyrinth",
    "Icebreaker",
    "Terminal",
]

KEY_CATEGORIES_ORDER = [
    "Todas",
    "Quest Key",
    "Marked Room",
    "Keycard",
    "Extracto / Utilidad",
]


KEYS_CATALOG: List[Dict[str, Any]] = [
    # =========================================================
    # CUSTOMS
    # =========================================================
    {
        "id": "customs_dorm_314_marked",
        "name": "Dorm room 314 marked key",
        "short_name": "Dorm 314 Marked",
        "map": "Customs",
        "category": "Marked Room",
        "uses": 10,
        "quests": ["The Cult - Part 2"],
        "opens": "Habitación 314 en el 3er piso de Dorms de 3 pisos (Customs).",
        "loot": "Weapons Case, Keytool, Injector Case, Docs Case, Keycards, armas de alto tier y objetos raros.",
        "spawns": "Chaquetas, Scavs, Cultistas, Jaeger Stashes y trueque ocasional.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Muy Alto (1.5M - 3.5M ₽)",
    },
    {
        "id": "customs_machinery",
        "name": "Machinery key",
        "short_name": "Machinery",
        "map": "Customs",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Checking (Prapor)"],
        "opens": "Puerta de cabina del camión cisterna naranja en la zona de construcción (Customs).",
        "loot": "Bronze Pocket Watch (ítem de misión).",
        "spawns": "Spawn fijo dentro de la chaqueta en Dorms de 3 pisos (Habitación 205), y en chaquetas.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Bajo (~15k ₽)",
    },
    {
        "id": "customs_tarcone_director",
        "name": "Tarcone Director's office key",
        "short_name": "Tarcone Dir.",
        "map": "Customs",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Delivery from the Past (Prapor)"],
        "opens": "Oficina del director en el 2do piso de Big Red (Customs).",
        "loot": "Seguro (Safe), 3 PCs, documentos de misión, Intel ocasional.",
        "spawns": "Chaquetas, archivadores y Trueque con Therapist LL1.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~45k ₽)",
    },
    {
        "id": "customs_unknown_key",
        "name": "Unknown key",
        "short_name": "Unknown",
        "map": "Customs",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["The Extortionist (Skier)"],
        "opens": "Cabaña metálica cerca de Old Gas / RUAF Roadblock.",
        "loot": "Documento oculto de misión (The Extortionist).",
        "spawns": "Spawn 100% fijo en el cadáver del Scav junto a los arbustos cerca de Crackhouse / RUAF.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Bajo (~10k ₽)",
    },
    {
        "id": "customs_dorm_206",
        "name": "Dorm room 206 key",
        "short_name": "Dorm 206",
        "map": "Customs",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Operation Aquarius - Part 1 (Therapist)"],
        "opens": "Habitación 206 en el 2do piso de Dorms de 2 pisos.",
        "loot": "Depósito de agua para misión.",
        "spawns": "Chaquetas, archivadores, Scavs.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Bajo (~12k ₽)",
    },
    {
        "id": "customs_dorm_114",
        "name": "Dorm room 114 key",
        "short_name": "Dorm 114",
        "map": "Customs",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Pharmacist (Therapist)"],
        "opens": "Habitación 114 en el 1er piso de Dorms de 2 pisos.",
        "loot": "Maletín médico de misión, Safe y Medcase.",
        "spawns": "Spawn fijo en la chaqueta del maletero del coche rojo cerca de Checkpoint militar, y chaquetas.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~35k ₽)",
    },
    {
        "id": "customs_dorm_220",
        "name": "Dorm room 220 key",
        "short_name": "Dorm 220",
        "map": "Customs",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Chemical - Part 1 (Skier)"],
        "opens": "Habitación 220 en el 2do piso de Dorms de 3 pisos.",
        "loot": "Documentos de misión, llave Dorm 220/Safe y Weapon Box.",
        "spawns": "Spawn en el vagón de tren cerca de New Gas / chaquetas.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Bajo (~20k ₽)",
    },
    {
        "id": "customs_dorm_105",
        "name": "Dorm room 105 key",
        "short_name": "Dorm 105",
        "map": "Customs",
        "category": "Llaves",
        "uses": 40,
        "quests": [],
        "opens": "Habitación 105 en el 1er piso de Dorms de 2 pisos.",
        "loot": "Safe (caja fuerte) de fácil acceso para farmear dinero y objetos de valor.",
        "spawns": "Chaquetas, archivadores y Scavs.",
        "verdict": "OPCIONAL / LOOT",
        "approx_value": "Medio (~40k ₽)",
    },
    {
        "id": "customs_security_post",
        "name": "Security post key",
        "short_name": "Security / Office Post",
        "map": "Customs",
        "category": "Llaves",
        "uses": 40,
        "quests": [],
        "opens": "Puerta de la oficina / puesto de guardia para cruzar entre New Gas Station y los galpones industriales (rework de Customs).",
        "loot": "Atajo de cruce entre New Gas y los galpones (no es extracción).",
        "spawns": "Chaquetas, archivadores y Scavs en Customs.",
        "verdict": "OPCIONAL / CRUCE",
        "approx_value": "Medio (~40k - 80k ₽)",
    },
    {
        "id": "customs_usec_stash",
        "name": "USEC stash key",
        "short_name": "USEC Stash",
        "map": "Customs",
        "category": "Llaves",
        "uses": 40,
        "quests": [],
        "opens": "Habitación cerrada en el 2do piso del galpón/almacén industrial de Customs.",
        "loot": "Weapon Boxes, mods de armas, Intel ocasional y chalecos/cascos.",
        "spawns": "Chaquetas y archivadores.",
        "verdict": "OPCIONAL / LOOT",
        "approx_value": "Medio (~45k ₽)",
    },
    {
        "id": "customs_gas_storage",
        "name": "Gas station storage room key",
        "short_name": "Gas Storage",
        "map": "Customs",
        "category": "Llaves",
        "uses": 40,
        "quests": [],
        "opens": "Almacén trasero de New Gas Station (Customs).",
        "loot": "Medcase, cajas de suministros y spawns médicos.",
        "spawns": "Chaquetas y escritorio en Customs.",
        "verdict": "OPCIONAL / LOOT",
        "approx_value": "Bajo (~20k ₽)",
    },

    # =========================================================
    # SHORELINE
    # =========================================================
    {
        "id": "shoreline_san_301",
        "name": "Health Resort West wing room 301 key",
        "short_name": "West 301",
        "map": "Shoreline",
        "category": "Llaves",
        "uses": 40,
        "quests": ["Nostalgia (Jaeger) - indirecto / Loot Meta"],
        "opens": "Habitación 301 del Ala Oeste del Health Resort (conectada con 304 por el balcón).",
        "loot": "Spawns de LEDX, Graphics Card, Ophthalmoscope, Bitcoins, 2 PCs y Weapon Box.",
        "spawns": "Chaquetas, archivadores y Scavs en Shoreline/Customs.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Alto (350k - 600k ₽)",
    },
    {
        "id": "shoreline_san_222",
        "name": "Health Resort East wing room 222 key",
        "short_name": "East 222 / 226",
        "map": "Shoreline",
        "category": "Llaves",
        "uses": 40,
        "quests": [],
        "opens": "Habitación 222 del Ala Este (conecta por balcón con la 226).",
        "loot": "LEDX, Medcase, Weapon Box, Rare Loot y Armor/Weapon spawns.",
        "spawns": "Spawn fijo cerca de la planta de energía (Power Station) y chaquetas.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Alto (250k - 450k ₽)",
    },
    {
        "id": "shoreline_san_216",
        "name": "Health Resort West wing room 216 key",
        "short_name": "West 216",
        "map": "Shoreline",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Lend-Lease - Part 1 (Skier)"],
        "opens": "Habitación 216 del Ala Oeste del Health Resort.",
        "loot": "Motor Controller (ítem de misión) + cajas de armas.",
        "spawns": "Chaquetas y spawn en West 220 / oficina de Admin.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~60k ₽)",
    },
    {
        "id": "shoreline_san_306",
        "name": "Health Resort West wing room 306 key",
        "short_name": "West 306",
        "map": "Shoreline",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Health Care Privacy - Part 2 (Therapist)", "Spa Tour - Part 4 (Peacekeeper)"],
        "opens": "Habitación 306 del Ala Oeste del Resort.",
        "loot": "Objetivos de 2 misiones + PCs y Medbag.",
        "spawns": "Chaquetas, archivadores y dormitorios.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~75k ₽)",
    },
    {
        "id": "shoreline_san_328",
        "name": "Health Resort East wing room 328 key",
        "short_name": "East 328",
        "map": "Shoreline",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Wet Job - Part 5 (Peacekeeper)"],
        "opens": "Habitación 328 del Ala Este (conecta con cuarto de utilidad).",
        "loot": "Disco duro de misión, PCs y Duffel bag.",
        "spawns": "Chaquetas y mesa en la isla de Scav Island.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~55k ₽)",
    },
    {
        "id": "shoreline_cottage_back",
        "name": "Cottage back door key",
        "short_name": "Cottage Back",
        "map": "Shoreline",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Colleagues - Part 2 (Therapist)"],
        "opens": "Puerta trasera de la cabaña cerrada en Villas (Shoreline).",
        "loot": "Ítem de misión (Surgical kit de Sanitar) + 2 Safes.",
        "spawns": "Barriles azules frente a la cabaña, chaquetas y Sanitar.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~70k ₽)",
    },
    {
        "id": "shoreline_tape_key",
        "name": "Health Resort office key with a blue tape",
        "short_name": "San tape",
        "map": "Shoreline",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["The Chemistry Closet (Jaeger)"],
        "opens": "Oficina de Sanitar (Habitación 110 del Ala Este).",
        "loot": "Spawns frecuentes de LEDX, Ophthalmoscope, Stimulants y Medcase.",
        "spawns": "Bolsillos de Sanitar, chaquetas y archivadores.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Alto (200k - 400k ₽)",
    },

    # =========================================================
    # RESERVE
    # =========================================================
    {
        "id": "reserve_rb_bk",
        "name": "RB-BK marked key",
        "short_name": "RB-BK Marked",
        "map": "Reserve",
        "category": "Marked Room",
        "uses": 10,
        "quests": ["The Cult - Part 2"],
        "opens": "Cuarto marcado en el sótano del edificio Black Bishop (Reserve).",
        "loot": "Cases (Docs, Injector, Keytool, Ammo), armas raras y objetos de alto valor.",
        "spawns": "Chaquetas, Scavs, Raiders y Cultistas.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Muy Alto (900k - 2M ₽)",
    },
    {
        "id": "reserve_rb_vo",
        "name": "RB-VO marked key",
        "short_name": "RB-VO Marked",
        "map": "Reserve",
        "category": "Marked Room",
        "uses": 10,
        "quests": ["The Cult - Part 2"],
        "opens": "Cuarto marcado en el 1er piso de Black Pawn (Reserve).",
        "loot": "Cases, Keycards, armas meta y objetos de culto.",
        "spawns": "Chaquetas, Raiders, Glukhar y Cultistas.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Muy Alto (800k - 1.8M ₽)",
    },
    {
        "id": "reserve_rb_pkpm",
        "name": "RB-PKPM marked key",
        "short_name": "RB-PKPM Marked",
        "map": "Reserve",
        "category": "Marked Room",
        "uses": 10,
        "quests": [],
        "opens": "Cuarto marcado en el búnker D-2 (junto a la puerta de control).",
        "loot": "Cases, Intel, Bitcoins y trueque necesario para Dorm 314 con Jaeger.",
        "spawns": "Chaquetas y Raiders.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Muy Alto (1M - 2.2M ₽)",
    },
    {
        "id": "reserve_rb_st",
        "name": "RB-ST key",
        "short_name": "RB-ST",
        "map": "Reserve",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Revision - Reserve (Peacekeeper)", "Disease History (Therapist)", "The Bunker - Part 2"],
        "opens": "Garaje cerrado cerca de White Knight / Tank Garage (Reserve).",
        "loot": "Tank Battery, OFZ Shells, Weapon Boxes y documentos de misión.",
        "spawns": "Archivadores de Reserve, chaquetas y Raiders.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Alto (180k - 350k ₽)",
    },
    {
        "id": "reserve_rb_kprl",
        "name": "RB-KPRL key",
        "short_name": "RB-KPRL",
        "map": "Reserve",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Disease History (Therapist)"],
        "opens": "Casetas de guardia cerca de la cúpula (Dome) en Reserve.",
        "loot": "2 Safes, Intel y documento de misión.",
        "spawns": "Chaquetas y archivadores.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~90k ₽)",
    },
    {
        "id": "reserve_rb_smp",
        "name": "RB-SMP key",
        "short_name": "RB-SMP",
        "map": "Reserve",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Disease History (Therapist)"],
        "opens": "Sala médica en el 2do piso de White Bishop (Reserve).",
        "loot": "Spawns médicos (LEDX/Ophthalmoscope raro), Medbags y carpeta médica de misión.",
        "spawns": "Chaquetas y archivadores.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~85k ₽)",
    },

    # =========================================================
    # STREETS OF TARKOV
    # =========================================================
    {
        "id": "streets_abandoned_factory",
        "name": "Abandoned factory marked key",
        "short_name": "Abandoned Marked",
        "map": "Streets of Tarkov",
        "category": "Marked Room",
        "uses": 10,
        "quests": [],
        "opens": "Cuarto marcado en la fábrica abandonada de Streets of Tarkov.",
        "loot": "Uno de los mejores Marked del juego: Keycards, Cases, armas raras, Bitcoins.",
        "spawns": "Chaquetas, Scavs y archivadores en Streets.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Muy Alto (2M - 4M ₽)",
    },
    {
        "id": "streets_mysterious_room",
        "name": "Mysterious room marked key",
        "short_name": "Mysterious Marked",
        "map": "Streets of Tarkov",
        "category": "Marked Room",
        "uses": 10,
        "quests": [],
        "opens": "Cuarto marcado en Chekannaya 13 (Streets of Tarkov).",
        "loot": "Keycards, Cases, Bitcoins, armas meta y objetos raros.",
        "spawns": "Chaquetas y Scavs.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Muy Alto (1.8M - 3.5M ₽)",
    },
    {
        "id": "streets_rusted_bloody",
        "name": "Rusted bloody key",
        "short_name": "Rusted Bloody",
        "map": "Streets of Tarkov",
        "category": "Quest Key",
        "uses": 1,
        "quests": ["The Door (Mechanic)"],
        "opens": "Puerta cerrada en el 2do piso del Klimov Shopping Mall.",
        "loot": "Decenas de llaves raras en el tablero (incluyendo Marked Keys y Keycards) + cámara de misión.",
        "spawns": "Spawn extremadamente raro debajo de las escaleras del Klimov Mall (no se puede vender en Flea ni meter en Secure Container).",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Invaluable (No vendible en Flea)",
    },
    {
        "id": "streets_chekannaya_15",
        "name": "Chekannaya 15 apartment key",
        "short_name": "Chek 15",
        "map": "Streets of Tarkov",
        "category": "Llaves",
        "uses": 20,
        "quests": ["The Delicious Sausage / Audit"],
        "opens": "Apartamento 15 en Chekannaya 15 (Streets of Tarkov).",
        "loot": "Gran cantidad de spawns de Bitcoin, GP Coin, Lion, Rolex, Virtex y relojes.",
        "spawns": "Bolsillos de Scavs, chaquetas y archivadores.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Muy Alto (800k - 1.5M ₽)",
    },
    {
        "id": "streets_beluga",
        "name": "Beluga restaurant director key",
        "short_name": "Beluga Dir.",
        "map": "Streets of Tarkov",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["House Arrest - Part 1 / Ballet Lover"],
        "opens": "Oficina del director dentro del restaurante Beluga.",
        "loot": "Intel, Safe y objetivo de misión.",
        "spawns": "Chaquetas y archivadores de Streets.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~95k ₽)",
    },

    # =========================================================
    # LIGHTHOUSE
    # =========================================================
    {
        "id": "lighthouse_shared_bedroom",
        "name": "Lighthouse island stash key",
        "short_name": "Lighthouse Stash",
        "map": "Lighthouse",
        "category": "Marked Room",
        "uses": 1,
        "quests": [],
        "opens": "Alijo marcado en la isla del faro (Lighthouse Island).",
        "loot": "Virtex, COFDM, Bitcoins, Weapons y Cases.",
        "spawns": "Chaquetas y Cultistas.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Alto (400k - 800k ₽)",
    },
    {
        "id": "lighthouse_merin",
        "name": "Merin car trunk key",
        "short_name": "Merin Trunk",
        "map": "Lighthouse",
        "category": "Llaves",
        "uses": 40,
        "quests": [],
        "opens": "Maletero del coche rojo Merin en la carretera principal de Lighthouse.",
        "loot": "Virtex, Military Flash Drive, Bitcoin, GP Coin y valuables.",
        "spawns": "Chaquetas y archivadores.",
        "verdict": "OPCIONAL / LOOT",
        "approx_value": "Medio (~80k ₽)",
    },
    {
        "id": "lighthouse_water_treatment_storage",
        "name": "Water treatment plant storage room key",
        "short_name": "WTP Storage",
        "map": "Lighthouse",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Broadcast - Part 3 / Revision - Lighthouse"],
        "opens": "Almacén en la Planta de Tratamiento de Agua (Rogues).",
        "loot": "Electrónica militar y objetivo de misión.",
        "spawns": "Chaquetas y Rogues.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~60k ₽)",
    },
    {
        "id": "lighthouse_operating_room",
        "name": "Operating room key",
        "short_name": "Operating Room",
        "map": "Lighthouse",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Corporate Secrets (Peacekeeper)"],
        "opens": "Sala de operaciones en la planta de Rogues (Edificio 2).",
        "loot": "Documentos confidenciales de misión + spawns médicos.",
        "spawns": "Chaquetas y archivadores.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~75k ₽)",
    },

    # =========================================================
    # INTERCHANGE
    # =========================================================
    {
        "id": "interchange_kiba_inner",
        "name": "KIBA Arms inner grate door key",
        "short_name": "KIBA Inner",
        "map": "Interchange",
        "category": "Llaves",
        "uses": 40,
        "quests": [],
        "opens": "Reja interior de la tienda KIBA Arms (requiere corriente encendida + KIBA Outer).",
        "loot": "Armas modificadas (RSASS, M4, MPX), miras térmicas REAP-IR, chalecos y placas.",
        "spawns": "Chaquetas y trueque / recompensa de Gunsmith.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Alto (200k - 400k ₽)",
    },
    {
        "id": "interchange_ultra_med",
        "name": "ULTRA medical storage key",
        "short_name": "ULTRA Med",
        "map": "Interchange",
        "category": "Llaves",
        "uses": 40,
        "quests": [],
        "opens": "Almacén médico frente a Techlight en el 2do piso (requiere corriente).",
        "loot": "LEDX, Defibrillator, Ophthalmoscope, Grizzly y estimulantes.",
        "spawns": "Chaquetas y Scavs.",
        "verdict": "MARKED / META LOOT",
        "approx_value": "Alto (250k - 500k ₽)",
    },
    {
        "id": "interchange_11sr",
        "name": "Object #11SR keycard",
        "short_name": "11SR Keycard",
        "map": "Interchange",
        "category": "Keycard",
        "secondary_categories": ["Extracto / Utilidad"],
        "uses": 15,
        "quests": [],
        "opens": "Extracción secreta Saferoom Exfil debajo de Burger Spot (requiere corriente).",
        "loot": "Extracción segura con loot de armas, oro y bitcoins.",
        "spawns": "Bolsillos de Killa, Scavs y Raiders.",
        "verdict": "KEYCARD / EXTRACTO",
        "approx_value": "Alto (200k - 350k ₽)",
    },
    {
        "id": "interchange_emercom_med",
        "name": "EMERCOM medical unit key",
        "short_name": "EMERCOM Med",
        "map": "Interchange",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Vitamins - Part 1 (Skier)"],
        "opens": "Unidad médica de EMERCOM en la planta baja del Mall.",
        "loot": "Contenedor químico de misión + Medcases.",
        "spawns": "Spawn fijo en la ambulancia frente a New Gas (Customs) y chaquetas.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Medio (~45k ₽)",
    },

    # =========================================================
    # WOODS
    # =========================================================
    {
        "id": "woods_shturman_stash",
        "name": "Shturman's stash key",
        "short_name": "Shturman Stash",
        "map": "Woods",
        "category": "Llaves",
        "uses": 1,
        "quests": ["Hunting Trip (Jaeger)"],
        "opens": "Caja fuerte / alijo de madera de Shturman en Sawmill (Woods).",
        "loot": "Red Rebel Ice Pick, Keycards, armas modificadas, objetos raros y llaves.",
        "spawns": "100% en los bolsillos de Shturman al eliminarlo.",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Alto (180k - 280k ₽)",
    },
    {
        "id": "woods_zb014",
        "name": "ZB-014 key",
        "short_name": "ZB-014",
        "map": "Woods",
        "category": "Extracto / Utilidad",
        "uses": 40,
        "quests": ["Ice Cream Cones (Prapor)"],
        "opens": "Búnker de extracción ZB-014 en Woods.",
        "loot": "Extracción rápida (con humo verde) + cargadores de 60 balas para misión.",
        "spawns": "Spawn fijo en la habitación 220 de Dorms (Customs), chaquetas.",
        "verdict": "EXTRACTO CLAVE",
        "approx_value": "Bajo (~25k ₽)",
    },

    # =========================================================
    # FACTORY
    # =========================================================
    {
        "id": "factory_exit_key",
        "name": "Factory emergency exit key",
        "short_name": "Factory Exit",
        "map": "Factory",
        "category": "Extracto / Utilidad",
        "uses": 20,
        "quests": ["Scout (Mechanic)"],
        "opens": "Extracciones Gate 0, Cellars y Med Tent en Factory (ya NO abre ZB-013 en Customs).",
        "loot": "Extracciones rápidas y seguras exclusivas de Factory.",
        "spawns": "Chaquetas, mochila de Scavs y Trueque con Jaeger.",
        "verdict": "EXTRACTO CLAVE",
        "approx_value": "Medio (~55k ₽)",
    },

    # =========================================================
    # THE LAB (KEYCARDS)
    # =========================================================
    {
        "id": "labs_access_card",
        "name": "TerraGroup Labs access keycard",
        "short_name": "Labs Access",
        "map": "The Lab",
        "category": "Keycard",
        "uses": 1,
        "quests": ["Fishing Place / Colleagues - Part 3"],
        "opens": "Entrada obligatoria para desplegar en el mapa The Lab.",
        "loot": "Acceso a The Lab (Raiders, LEDX, GPSA, MCC).",
        "spawns": "Therapist LL4, Scav Player spawn, Bosses y archivadores.",
        "verdict": "KEYCARD LABS",
        "approx_value": "Alto (~160k - 220k ₽)",
    },
    {
        "id": "labs_black_keycard",
        "name": "TerraGroup Labs keycard (Black)",
        "short_name": "Black Keycard",
        "map": "The Lab",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Laboratorio de pruebas biológicas (Planta 1, zona central).",
        "loot": "Mejor sala médica del juego: múltiples LEDX y 5-10 estimulantes (SJ6, MULE, EtG).",
        "spawns": "Trueque con Mechanic LL4, Bosses y Marked Rooms.",
        "verdict": "KEYCARD LABS",
        "approx_value": "Muy Alto (2.5M - 4.5M ₽)",
    },
    {
        "id": "labs_green_keycard",
        "name": "TerraGroup Labs keycard (Green)",
        "short_name": "Green Keycard",
        "map": "The Lab",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Sala de investigación médica/experimental en Planta 2.",
        "loot": "LEDX, estimulantes, Intel, Black Keycard spawn ocasional y armas.",
        "spawns": "Spawn raro en Labs, Bosses y Marked Rooms.",
        "verdict": "KEYCARD LABS",
        "approx_value": "Muy Alto (3M - 6M ₽)",
    },
    {
        "id": "labs_red_keycard",
        "name": "TerraGroup Labs keycard (Red)",
        "short_name": "Red Keycard",
        "map": "The Lab",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Oficina de seguridad / arsenal en Planta 2.",
        "loot": "Armas modificadas, munición AP, Intel, Bitcoins y objetos de valor.",
        "spawns": "Spawn ultra raro en Shoreline Resort, Tagilla/Shturman y Marked Rooms.",
        "verdict": "KEYCARD LABS",
        "approx_value": "Muy Alto (4M - 8M ₽)",
    },
    {
        "id": "labs_violet_keycard",
        "name": "TerraGroup Labs keycard (Violet)",
        "short_name": "Violet Keycard",
        "map": "The Lab",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Sala de seguridad en Planta 2 (frente a Red).",
        "loot": "LEDX, Bitcoin, Weapons, GPUs, Attachments meta y Cases.",
        "spawns": "Woods (SUVs/Cabaña), Shturman y Marked Rooms.",
        "verdict": "KEYCARD LABS",
        "approx_value": "Muy Alto (2M - 4M ₽)",
    },
    {
        "id": "labs_blue_keycard",
        "name": "TerraGroup Labs keycard (Blue)",
        "short_name": "Blue Keycard",
        "map": "The Lab",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Laboratorio médico frente a Black en Planta 1.",
        "loot": "Estimulantes, LEDX ocasional y suministros médicos.",
        "spawns": "Shoreline (Ambulancia/West 104/112), Sanitar y Marked Rooms.",
        "verdict": "KEYCARD LABS",
        "approx_value": "Alto (800k - 1.5M ₽)",
    },
    {
        "id": "labs_yellow_keycard",
        "name": "TerraGroup Labs keycard (Yellow)",
        "short_name": "Yellow Keycard",
        "map": "The Lab",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Sala de control de sensores / alarma en el hall central.",
        "loot": "GPUs, LEDX raro, objetos de valor y desactivación de alarmas.",
        "spawns": "Bosses, Scav Case y Marked Rooms.",
        "verdict": "KEYCARD LABS",
        "approx_value": "Alto (400k - 900k ₽)",
    },

    # =========================================================
    # THE LABYRINTH
    # =========================================================
    {
        "id": "the_labyrinth_ariadne_symbol_key",
        "name": "Ariadne symbol key",
        "short_name": "Ariadne",
        "map": "The Labyrinth",
        "category": "Extracto / Utilidad",
        "uses": 1,
        "quests": [],
        "opens": 'Activa la extracción "Ariadne\'s Path" en The Labyrinth.',
        "loot": "Extracción especial en The Labyrinth.",
        "spawns": "Spawns dentro de The Labyrinth.",
        "verdict": "EXTRACTO CLAVE",
        "approx_value": "Alto (Llave de extracción única)",
    },
    {
        "id": "the_labyrinth_labrys_access_keycard",
        "name": "Labrys access keycard",
        "short_name": "Labrys Access",
        "map": "The Labyrinth",
        "category": "Keycard",
        "uses": 1,
        "quests": ["Offensive Reconnaissance (Mechanic)"],
        "opens": "Acceso/tránsito a The Labyrinth desde el sótano del ala oeste de Health Resort en Shoreline (requiere Knossos LLC facility key).",
        "loot": "Acceso al complejo subterráneo de The Labyrinth y sus zonas restringidas.",
        "spawns": "Trueque con Jaeger LL1, Cultist Circle (Labrys research notes) y recompensas de misión.",
        "verdict": "KEYCARD / ACCESO",
        "approx_value": "Alto (Acceso único a Labyrinth)",
    },

    # =========================================================
    # ICEBREAKER (BOREAS) & TERMINAL
    # =========================================================
    {
        "id": "icebreaker_boreas_crew_quarters_keycard",
        "name": "Boreas crew quarters keycard",
        "short_name": "Boreas Crew Quarters",
        "map": "Icebreaker",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Camarotes de tripulación del buque nuclear Boreas en el mapa Icebreaker.",
        "loot": "Suministros tácticos, electrónica y equipamiento de Black Division.",
        "spawns": "Spawns fijos en el nivel 3 del rompehielos Boreas.",
        "verdict": "KEYCARD",
        "approx_value": "Variable (Historia Boreas)",
    },
    {
        "id": "icebreaker_boreas_engine_room_keycard",
        "name": "Boreas engine room keycard",
        "short_name": "Boreas Engine Room",
        "map": "Icebreaker",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Sala de máquinas (Deck -2: Engine Room) del buque Boreas en Icebreaker.",
        "loot": "Zona principal de The Wedge y escuadrón Black Division, equipamiento militar y electrónica.",
        "spawns": "Spawns dentro del buque Boreas y Black Division.",
        "verdict": "KEYCARD",
        "approx_value": "Variable (Historia Boreas)",
    },
    {
        "id": "icebreaker_compartment_c1_keycard",
        "name": "Compartment C-1 keycard",
        "short_name": "Compartment C-1",
        "map": "Icebreaker",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Compartimento C-1 en el interior del buque Boreas (Icebreaker).",
        "loot": "Botín de compartimentos internos del rompehielos.",
        "spawns": "Spawns a bordo del Boreas.",
        "verdict": "KEYCARD",
        "approx_value": "Variable (Historia Boreas)",
    },
    {
        "id": "icebreaker_compartment_c3_keycard",
        "name": "Compartment C-3 keycard",
        "short_name": "Compartment C-3",
        "map": "Icebreaker",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Compartimento C-3 en el interior del buque Boreas (Icebreaker).",
        "loot": "Botín de compartimentos internos del rompehielos.",
        "spawns": "Spawns a bordo del Boreas.",
        "verdict": "KEYCARD",
        "approx_value": "Variable (Historia Boreas)",
    },
    {
        "id": "terminal_black_division_keycard",
        "name": "Black Division keycard",
        "short_name": "Black Division",
        "map": "Terminal",
        "category": "Keycard",
        "uses": 10,
        "quests": [],
        "opens": "Puertas cerradas operadas por Black Division en la zona portuaria de Terminal.",
        "loot": "Equipamiento táctico de Black Division y armas de alto tier.",
        "spawns": "Spawn garantizado en caja de armas (6x2) en el edificio de la terminal portuaria.",
        "verdict": "KEYCARD",
        "approx_value": "Alto (Endgame Terminal)",
    },

    # =========================================================
    # GROUND ZERO
    # =========================================================
    {
        "id": "gz_terragroup_scientist",
        "name": "TerraGroup scientist key",
        "short_name": "TG Scientist",
        "map": "Ground Zero",
        "category": "Quest Key",
        "uses": 40,
        "quests": ["Saving the Mole (Mechanic)"],
        "opens": "Oficina del científico en el 2do piso del edificio TerraGroup (Ground Zero).",
        "loot": "Disco duro de misión (Saving the Mole) + PCs.",
        "spawns": "Spawn 100% fijo en el cadáver del científico en la habitación contigua (se puede saltar por la cornisa si falta).",
        "verdict": "SIEMPRE GUARDAR (Quest)",
        "approx_value": "Bajo (~15k ₽)",
    },
    {
        "id": "gz_tarbank_safe",
        "name": "Tarbank cash register / Safe key",
        "short_name": "Tarbank GZ",
        "map": "Ground Zero",
        "category": "Llaves",
        "uses": 40,
        "quests": [],
        "opens": "Área de cajas / oficina del banco Tarbank en Ground Zero.",
        "loot": "Rublos, dólares y cajas registradoras para inicio de wipe.",
        "spawns": "Archivadores y chaquetas en Ground Zero.",
        "verdict": "OPCIONAL / LOOT",
        "approx_value": "Bajo (~20k ₽)",
    },
]


def _merge_wiki_extra_keys() -> None:
    """Agrega las llaves restantes del catálogo completo de la Wiki sin duplicar."""
    try:
        from core.keys_wiki_catalog import WIKI_EXTRA_KEYS
    except ImportError:
        return
    existing_ids = {k["id"] for k in KEYS_CATALOG}
    existing_names = {k["name"].strip().lower() for k in KEYS_CATALOG}
    for item in WIKI_EXTRA_KEYS:
        if item["id"] in existing_ids or item["name"].strip().lower() in existing_names:
            continue
        KEYS_CATALOG.append(item)
        existing_ids.add(item["id"])
        existing_names.add(item["name"].strip().lower())


_merge_wiki_extra_keys()


def get_keys_maps() -> List[str]:
    """Devuelve los mapas ordenados disponibles en el catálogo de llaves."""
    present = {k["map"] for k in KEYS_CATALOG}
    ordered = [m for m in KEY_MAPS_ORDER if m == "Todos" or m in present]
    extras = sorted(m for m in present if m not in ordered)
    return ordered + extras


def get_keys_categories() -> List[str]:
    """Devuelve las categorías principales para la barra de filtros (sin redundar con 'Todas')."""
    return list(KEY_CATEGORIES_ORDER)


def filter_keys(
    map_filter: str = "Todos",
    category_filter: str = "Todas",
    query: str = "",
    owned_ids: Optional[Set[str]] = None,
    only_missing_quest: bool = False,
) -> List[Dict[str, Any]]:
    """Filtra el catálogo de llaves por mapa, categoría, búsqueda de texto y estado de posesión."""
    q = (query or "").strip().lower()
    owned = owned_ids or set()
    results: List[Dict[str, Any]] = []

    for item in KEYS_CATALOG:
        if map_filter and map_filter != "Todos" and item["map"] != map_filter:
            continue
        if category_filter and category_filter != "Todas":
            if item["category"] != category_filter and category_filter not in item.get("secondary_categories", ()):
                continue
        if only_missing_quest:
            if not item.get("quests") or item["id"] in owned:
                continue
        if q:
            haystack = " ".join([
                item.get("name", ""),
                item.get("short_name", ""),
                item.get("map", ""),
                item.get("category", ""),
                item.get("opens", ""),
                item.get("loot", ""),
                " ".join(item.get("quests", [])),
            ]).lower()
            if q not in haystack:
                continue
        results.append(item)

    return results


def get_key_stats(owned_ids: Optional[Set[str]] = None) -> Dict[str, int]:
    """Calcula estadísticas resumen del llavero del usuario."""
    owned = owned_ids or set()
    total = len(KEYS_CATALOG)
    owned_count = sum(1 for k in KEYS_CATALOG if k["id"] in owned)
    quest_total = sum(1 for k in KEYS_CATALOG if k.get("quests"))
    quest_missing = sum(1 for k in KEYS_CATALOG if k.get("quests") and k["id"] not in owned)
    return {
        "total": total,
        "owned": owned_count,
        "quest_total": quest_total,
        "quest_missing": quest_missing,
    }


def get_key_icon_path(key_id: str) -> Optional[str]:
    """Devuelve la ruta en caché local del icono de una llave si ya fue descargado."""
    path = os.path.join(KEYS_DIR, f"{key_id}.png")
    return path if os.path.exists(path) and os.path.getsize(path) > 100 else None


def fetch_key_icons_async(on_done: Optional[Callable[[], None]] = None) -> None:
    """
    Descarga en segundo plano los iconos oficiales de inventario de cada llave desde
    la página Keys_&_Intel de la Wiki oficial (MediaWiki API parse) y los guarda en cache/keys/<key_id>.png.
    """
    global _KEY_ICONS_FETCHING, _KEY_ICONS_FETCHED
    if _KEY_ICONS_FETCHING or _KEY_ICONS_FETCHED:
        return

    missing = [k for k in KEYS_CATALOG if not get_key_icon_path(k["id"])]
    if not missing:
        _KEY_ICONS_FETCHED = True
        return

    _KEY_ICONS_FETCHING = True

    def _worker():
        global _KEY_ICONS_FETCHING, _KEY_ICONS_FETCHED
        downloaded_any = False
        api_headers = {"User-Agent": "TarkovScope/1.0 (Desktop Companion)"}
        img_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://escapefromtarkov.fandom.com/",
        }
        wiki_api = "https://escapefromtarkov.fandom.com/api.php"
        try:
            url_by_name: Dict[str, str] = {}
            needs_wiki = any(k["id"] not in DIRECT_KEY_ICON_URLS for k in missing)
            if needs_wiki:
                resp = requests.get(
                    wiki_api,
                    params={
                        "action": "parse",
                        "page": "Keys_&_Intel",
                        "prop": "text",
                        "format": "json",
                    },
                    headers=api_headers,
                    timeout=20,
                )
                if resp.status_code == 200:
                    html = ((resp.json().get("parse") or {}).get("text") or {}).get("*", "")
                    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
                        m_img = re.search(
                            r'(?:data-src|src)=["\'](https://static\.wikia\.nocookie\.net/[^"\']+)["\']',
                            row,
                        )
                        if not m_img:
                            continue
                        img_url = m_img.group(1).replace("&amp;", "&")
                        if "data:image" in img_url:
                            continue
                        for m_title in re.findall(r'<a[^>]+title=["\']([^"\']+)["\']', row):
                            t_clean = html_lib.unescape(m_title).strip().lower()
                            if t_clean and t_clean not in url_by_name:
                                url_by_name[t_clean] = img_url

            wiki_aliases = {
                "customs_zb013": "zb-1013 key",
                "shoreline_tape_key": "key with tape",
                "gz_terragroup_scientist": "terragroup",
                "gz_tarbank_safe": "tarbank",
                "labs_access_card": "labs access keycard",
            }

            def _download_one(k: Dict[str, Any]) -> bool:
                img_url = DIRECT_KEY_ICON_URLS.get(k["id"])
                k_name = k["name"].strip().lower()
                k_short = k["short_name"].strip().lower()
                alias = wiki_aliases.get(k["id"], "")
                if not img_url and url_by_name:
                    img_url = (
                        url_by_name.get(k_name)
                        or url_by_name.get(k_short)
                        or (url_by_name.get(alias) if alias else None)
                    )
                if not img_url and url_by_name:
                    for wiki_title, w_url in url_by_name.items():
                        if (
                            k_name in wiki_title
                            or wiki_title in k_name
                            or (len(k_short) >= 4 and k_short in wiki_title)
                            or (alias and alias in wiki_title)
                        ):
                            img_url = w_url
                            break
                if not img_url:
                    return False
                try:
                    img_resp = requests.get(img_url, headers=img_headers, timeout=10)
                    if img_resp.status_code == 200 and len(img_resp.content) > 100:
                        dst = os.path.join(KEYS_DIR, f"{k['id']}.png")
                        with Image.open(io.BytesIO(img_resp.content)) as im:
                            im.convert("RGBA").save(dst, "PNG")
                        return True
                except Exception:
                    pass
                return False

            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(_download_one, missing))
            downloaded_any = any(results)
            _KEY_ICONS_FETCHED = True
        except Exception:
            pass
        finally:
            _KEY_ICONS_FETCHING = False
            if downloaded_any and on_done:
                try:
                    on_done()
                except Exception:
                    pass

    threading.Thread(target=_worker, daemon=True).start()
