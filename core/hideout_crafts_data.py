"""
TarkovScope - Base de Datos de Crafteos Clave del Hideout e Íconos de Estaciones
Incluye tiempos de fabricación, estación y nivel requerido, materiales de entrada, producto resultante (Found in Raid)
y miniaturas oficiales pre-cacheadas de la Wiki.
"""
from typing import List, Dict, Any

HIDEOUT_STATION_ICONS: Dict[str, Dict[str, str]] = {
    "Air Filtering Unit": {
        "icon_key": "hideout_air_filtering_unit",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/7f/Air_Filtering_Unit_Portrait.png/revision/latest?cb=20200424091408"
    },
    "Bitcoin Farm": {
        "icon_key": "hideout_bitcoin_farm",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/ea/Bitcoin_Farm_Portrait.png/revision/latest?cb=20200424091410"
    },
    "Booze Generator": {
        "icon_key": "hideout_booze_generator",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/f9/Booze_Generator_Portrait.png/revision/latest?cb=20200424091411"
    },
    "Cultist Circle": {
        "icon_key": "hideout_cultist_circle",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/0d/Cultist_Circle_Portrait.png/revision/latest?cb=20240820210535"
    },
    "Defective Wall": {
        "icon_key": "hideout_defective_wall",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/00/Defective_Wall_Portrait.png/revision/latest?cb=20230102013759"
    },
    "Gear Rack": {
        "icon_key": "hideout_gear_rack",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/08/Gear_Rack_Portrait.png/revision/latest?cb=20240820212228"
    },
    "Generator": {
        "icon_key": "hideout_generator",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/02/Generator_Portrait.png/revision/latest?cb=20200424091412"
    },
    "Gym": {
        "icon_key": "hideout_gym",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/77/Gym_Portrait.png/revision/latest?cb=20230102013721"
    },
    "Hall of Fame": {
        "icon_key": "hideout_hall_of_fame",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/1f/Hall_of_Fame_Portrait.png/revision/latest?cb=20231231143429"
    },
    "Heating": {
        "icon_key": "hideout_heating",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/d7/Heating_Portrait.png/revision/latest?cb=20200424091413"
    },
    "Illumination": {
        "icon_key": "hideout_illumination",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/8/83/Illumination_Portrait.png/revision/latest?cb=20200424091414"
    },
    "Intelligence Center": {
        "icon_key": "hideout_intelligence_center",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/4c/Intelligence_Center_Portrait.png/revision/latest?cb=20200424091414"
    },
    "Lavatory": {
        "icon_key": "hideout_lavatory",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/09/Lavatory_Portrait.png/revision/latest?cb=20200424091415"
    },
    "Library": {
        "icon_key": "hideout_library",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/23/Library_Portrait.png/revision/latest?cb=20200424091416"
    },
    "Medstation": {
        "icon_key": "hideout_medstation",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/9/94/Medstation_Portrait.png/revision/latest?cb=20200424091416"
    },
    "Nutrition Unit": {
        "icon_key": "hideout_nutrition_unit",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/f5/Nutrition_Unit_Portrait.png/revision/latest?cb=20200424093117"
    },
    "Rest Space": {
        "icon_key": "hideout_rest_space",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/16/Rest_Space_Portrait.png/revision/latest?cb=20200424091418"
    },
    "Scav Case": {
        "icon_key": "hideout_scav_case",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/30/Scav_Case_Portrait.png/revision/latest?cb=20250321204815"
    },
    "Security": {
        "icon_key": "hideout_security",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/ef/Security_Portrait.png/revision/latest?cb=20200424091419"
    },
    "Shooting Range": {
        "icon_key": "hideout_shooting_range",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/e4/Shooting_Range_Portrait.png/revision/latest?cb=20230104074627"
    },
    "Solar Power": {
        "icon_key": "hideout_solar_power",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/f3/Solar_power_Portrait.png/revision/latest?cb=20200424091420"
    },
    "Stash": {
        "icon_key": "hideout_stash",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/bc/Stash_Portrait.png/revision/latest?cb=20200424091421"
    },
    "Vents": {
        "icon_key": "hideout_vents",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/b/bc/Vents_Portrait.png/revision/latest?cb=20200424091422"
    },
    "Water Collector": {
        "icon_key": "hideout_water_collector",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/4d/Water_Collector_Portrait.png/revision/latest?cb=20230104074408"
    },
    "Weapon Rack": {
        "icon_key": "hideout_weapon_rack",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/d5/Weapon_Rack_Portrait.png/revision/latest?cb=20230813221448"
    },
    "Workbench": {
        "icon_key": "hideout_workbench",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/1c/Workbench_Portrait.png/revision/latest?cb=20200424091422"
    },
    "Christmas Tree": {
        "icon_key": "hideout_christmas_tree",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a6/Christmas_Tree_Portrait.png/revision/latest?cb=20200424091412"
    }
}

HIDEOUT_CRAFTS_DATA: List[Dict[str, Any]] = [
    {
        "station": "Workbench",
        "level": 1,
        "output": "2x Wires (Cables eléctricos) [FiR]",
        "time": "1h 23m",
        "inputs": "1x Power cord (Cable de alimentación)",
        "usage": "Material base para Hideout y trueques de Mechanic",
        "category": "MATERIAL / QUEST",
        "icon_key": "craft_wires",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/39/Wires.png/revision/latest?cb=20200618215921"
    },
    {
        "station": "Workbench",
        "level": 1,
        "output": "2x Capacitors (Capacitores) [FiR]",
        "time": "1h 12m",
        "inputs": "1x Power supply unit (PSU) + 1x Destornillador",
        "usage": "Requerido Found in Raid para 'Farming - Part 4' (Mechanic)",
        "category": "QUEST FiR",
        "icon_key": "craft_capacitors",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/1c/Capacitors.png/revision/latest?cb=20181227201603"
    },
    {
        "station": "Workbench",
        "level": 2,
        "output": "2x Printed circuit board (PCB) [FiR]",
        "time": "1h 04m",
        "inputs": "1x DVD drive + 1x Destornillador plano",
        "usage": "Requerido FiR para 'Signal - Part 2' (Mechanic)",
        "category": "QUEST FiR",
        "icon_key": "craft_pcb",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/18/Circuit.png/revision/latest?cb=20250308183348"
    },
    {
        "station": "Workbench",
        "level": 2,
        "output": "120x 5.45x39mm PP gs [Meta]",
        "time": "2h 15m",
        "inputs": "120x 5.45x39 PS + 1x Pólvora Verde (Eagle) + 1x Pólvora Azul (Kite)",
        "usage": "Munición perforante consistente para AK-74 / RPK-16 en mid-wipe",
        "category": "MUNICIÓN META",
        "icon_key": "craft_545_pp",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/ea/AKPPIMAGE.png/revision/latest?cb=20190519005447"
    },
    {
        "station": "Workbench",
        "level": 2,
        "output": "80x .300 Blackout CBJ [Meta]",
        "time": "3h 10m",
        "inputs": "80x 5.56x45 M855 + 1x Pólvora Roja (Hawk) + 1x Pólvora Azul (Kite)",
        "usage": "Penetración 43 (perfora Clase 4/5) para MCX .300 BLK",
        "category": "MUNICIÓN META",
        "icon_key": "craft_300_cbj",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/4b/BlackoutCBJ_View.png/revision/latest?cb=20230812203638"
    },
    {
        "station": "Workbench",
        "level": 3,
        "output": "120x 7.62x39mm BP gzh [Meta]",
        "time": "6h 45m",
        "inputs": "120x 7.62x39 PS + 2x Pólvora Roja (Hawk) + 1x Pólvora Verde (Eagle)",
        "usage": "Penetración 47 (Tier S para Mutant Mk47 y RD-704)",
        "category": "MUNICIÓN META",
        "icon_key": "craft_762x39_bp",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/c/c5/7.62x39BP_ins.png/revision/latest?cb=20200421141100"
    },
    {
        "station": "Workbench",
        "level": 3,
        "output": "80x 7.62x51mm M61 [Meta]",
        "time": "7h 30m",
        "inputs": "80x 7.62x51 M80 + 2x Pólvora Roja (Hawk) + 1x Helix radiator",
        "usage": "Penetración 60 (perfora Clase 6 para SR-25, RSASS y SCAR-H)",
        "category": "MUNICIÓN META",
        "icon_key": "craft_762x51_m61",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/7a/7.62x51_M61_banner.png/revision/latest?cb=20201103203606"
    },
    {
        "station": "Workbench",
        "level": 3,
        "output": "100x 9x19mm PBP gzh [Meta]",
        "time": "4h 50m",
        "inputs": "100x 9x19 PST + 1x Pólvora Verde (Eagle) + 1x Pólvora Roja (Hawk)",
        "usage": "Penetración 39 a 1100 RPM para Vector 9mm y MPX",
        "category": "MUNICIÓN META",
        "icon_key": "craft_9x19_pbp",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/c/c9/9x197N31view.png/revision/latest?cb=20200727164657"
    },
    {
        "station": "Medstation",
        "level": 1,
        "output": "1x Salewa first aid kit [FiR]",
        "time": "26m",
        "inputs": "1x Car first aid kit + 1x Esmarch tourniquet",
        "usage": "Requerido 3x FiR para 'Shortage' (Therapist — primera misión)",
        "category": "QUEST FiR",
        "icon_key": "craft_salewa",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a3/EFT_Salewa-First-Aid-Kit.png/revision/latest?cb=20250107080016"
    },
    {
        "station": "Medstation",
        "level": 1,
        "output": "2x Disposable syringe (Jeringa) [FiR]",
        "time": "32m",
        "inputs": "1x Pile of meds + 1x Botella de agua",
        "usage": "Material para inyectores y trueques médicos de Therapist",
        "category": "MATERIAL / QUEST",
        "icon_key": "craft_syringe",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/6/6a/DisposableSyringe.png/revision/latest?cb=20191030165358"
    },
    {
        "station": "Medstation",
        "level": 2,
        "output": "1x Morphine injector (Morfina) [FiR]",
        "time": "1h 18m",
        "inputs": "1x Analgin painkillers + 1x Jeringa descartable + 1x Pile of meds",
        "usage": "Requerido 4x FiR para 'Painkiller' (Therapist) y 'Spa Tour - Part 7'",
        "category": "QUEST FiR",
        "icon_key": "craft_morphine",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/00/Morphine_injector.png/revision/latest?cb=20200623110616"
    },
    {
        "station": "Medstation",
        "level": 2,
        "output": "2x IFAK individual first aid kit [FiR]",
        "time": "52m",
        "inputs": "2x Pile of meds + 1x Army bandage + 1x Esmarch",
        "usage": "Botiquín compacto de 1 celda y requisito de misiones médicas",
        "category": "QUEST FiR",
        "icon_key": "craft_ifak",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/29/EFT_IFAK.png/revision/latest?cb=20181110230819"
    },
    {
        "station": "Medstation",
        "level": 3,
        "output": "2x Propital regenerative stimulant [Meta]",
        "time": "1h 15m",
        "inputs": "1x Golden Star balm (incluso 1/10 usos) + 1x Ibuprofeno (1/15) + 2x Pile of meds",
        "usage": "Crafteo súper rentable: recicla Golden Star e Ibuprofeno gastados (1 uso restante)",
        "category": "RENTABLE / META",
        "icon_key": "craft_propital",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/8/82/Propital.png/revision/latest?cb=20181227173039"
    },
    {
        "station": "Medstation",
        "level": 3,
        "output": "1x M.U.L.E. stimulant injector [FiR]",
        "time": "2h 10m",
        "inputs": "1x Zagustin + 1x Morphine + 2x Pile of meds",
        "usage": "Requerido FiR para 'Samples' (Peacekeeper) y para llevar 70+ kg de botín",
        "category": "QUEST FiR",
        "icon_key": "craft_mule",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/3c/M.U.L.E._Stimulator.png/revision/latest?cb=20200727180454"
    },
    {
        "station": "Medstation",
        "level": 3,
        "output": "1x SJ6 TGLabs combat stimulant [FiR]",
        "time": "1h 55m",
        "inputs": "2x Adrenaline + 1x NaCl saline solution + 1x Pile of meds",
        "usage": "Estimulante de estamina infinita y misiones de Therapist/Peacekeeper",
        "category": "RENTABLE / META",
        "icon_key": "craft_sj6",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/4a/Combat_stimulant_SJ6.png/revision/latest?cb=20181228105904"
    },
    {
        "station": "Medstation",
        "level": 3,
        "output": "1x LEDX Skin Transilluminator [FiR]",
        "time": "10h 00m",
        "inputs": "1x Silicon tube + 1x Gas analyzer + 1x Ophthalmoscope + Manual Microcontroller",
        "usage": "Requerido FiR para 'Private Clinic' (T H I C C Item Case) y 'Crisis' (Therapist)",
        "category": "QUEST FiR",
        "icon_key": "craft_ledx",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a2/LEDX_on_office_safe.jpg/revision/latest?cb=20250619100712"
    },
    {
        "station": "Lavatory",
        "level": 1,
        "output": "1x Gas mask GP-5 /Filtro [FiR]",
        "time": "22m",
        "inputs": "Materiales básicos de taller",
        "usage": "Trueques iniciales y filtros de aire",
        "category": "MATERIAL / QUEST",
        "icon_key": "craft_gp5",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/e/ee/GP-5.png/revision/latest?cb=20180721210653"
    },
    {
        "station": "Lavatory",
        "level": 2,
        "output": "2x Corrugated hose (Manguera corrugada) [FiR]",
        "time": "2h 05m",
        "inputs": "2x Insulating tape + 1x Silicone tube + 3x Wires",
        "usage": "Requerido FiR para 'Spa Tour - Part 6' y mejoras de Water Collector / Booze Generator",
        "category": "QUEST FiR",
        "icon_key": "craft_hose",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/24/Hose3d.png/revision/latest?cb=20200623105115"
    },
    {
        "station": "Lavatory",
        "level": 2,
        "output": "1x 60-round 5.45x39 6L31 magazine [FiR]",
        "time": "1h 36m",
        "inputs": "4x 30-round 6L23 mags + 1x KEKTAPE",
        "usage": "Requerido 3x FiR para 'Ice Cream Cones' (Prapor) y 'Gunsmith - Part 2'",
        "category": "QUEST FiR",
        "icon_key": "craft_6l31",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/9/9b/ZB-014_6L31_Magazines.png/revision/latest?cb=20261020105907"
    },
    {
        "station": "Lavatory",
        "level": 2,
        "output": "1x BlackRock chest rig [FiR]",
        "time": "1h 45m",
        "inputs": "1x Tarzan chest rig + 2x Ripstop fabric + 1x Cordura",
        "usage": "Requerido 2x FiR para 'Sew it Good - Part 4' (Ragman)",
        "category": "QUEST FiR",
        "icon_key": "craft_blackrock",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/ac/Blackrock_Icon.png/revision/latest?cb=20191029140712"
    },
    {
        "station": "Lavatory",
        "level": 2,
        "output": "2x Cordura polyamide fabric [FiR]",
        "time": "1h 12m",
        "inputs": "1x Sling backpack + 1x Leatherman Multitool",
        "usage": "Requerido 5x FiR para 'Textile - Part 1' (Ragman)",
        "category": "QUEST FiR",
        "icon_key": "craft_cordura",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/2/25/Cordura_-_Jacob_%26_Jacob.png/revision/latest?cb=20200528105759"
    },
    {
        "station": "Lavatory",
        "level": 3,
        "output": "2x FP-100 filter absorber [Rentable]",
        "time": "3h 30m",
        "inputs": "2x Water filter (gastado) + 2x Gas mask air filter",
        "usage": "Recicla filtros de agua al 1% para usar en Air Filtering Unit o vender en Flea Market",
        "category": "RENTABLE / META",
        "icon_key": "craft_fp100",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/a/a6/FP-100_filter_absorber.png/revision/latest?cb=20191028210824"
    },
    {
        "station": "Intelligence Center",
        "level": 2,
        "output": "3x Secure Flash drive (Pendrive) [FiR]",
        "time": "18h 20m",
        "inputs": "1x Topographic survey maps + 2x GPhone X + 1x SSD drive",
        "usage": "Requerido 2x FiR para 'What's on the Flash Drive?' (Skier) y 3x FiR para 'Shady Business' (Jaeger)",
        "category": "QUEST FiR",
        "icon_key": "craft_flash_drive",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/3/34/Drive-in-PC.png/revision/latest?cb=20180322170709"
    },
    {
        "station": "Intelligence Center",
        "level": 2,
        "output": "1x Virtex programmable processor [FiR]",
        "time": "22h 00m",
        "inputs": "1x Military circuit board + 2x Broken GPhone X + 2x Gold neck chain",
        "usage": "Requerido 2x FiR para 'Lend-Lease - Part 2' (Peacekeeper)",
        "category": "QUEST FiR",
        "icon_key": "craft_virtex",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/02/VirtexSpawn.png/revision/latest?cb=20181226220548"
    },
    {
        "station": "Intelligence Center",
        "level": 2,
        "output": "1x UHF RFID Reader [FiR]",
        "time": "20h 40m",
        "inputs": "1x Broken GPhone + 1x Signal Jammer + 2x PCB",
        "usage": "Requerido FiR para 'Lend-Lease - Part 2' y 'Import' (Peacekeeper)",
        "category": "QUEST FiR",
        "icon_key": "craft_rfid",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/18/RFIDReaderSpawn.jpg/revision/latest?cb=20190305103018"
    },
    {
        "station": "Intelligence Center",
        "level": 3,
        "output": "1x Graphics card (GPU) [FiR]",
        "time": "48h 00m",
        "inputs": "1x VPX Flash Storage + 2x CPU + 4xCPU Fan + 2x Power supply unit",
        "usage": "Requerido 3x FiR para 'Farming - Part 4' (Mechanic) y para llenar tu Bitcoin Farm",
        "category": "QUEST FiR",
        "icon_key": "craft_gpu",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/f/f2/Graphics_Card.png/revision/latest?cb=20171102193946"
    },
    {
        "station": "Intelligence Center",
        "level": 3,
        "output": "1x COFDM Wireless Signal Transmitter [FiR]",
        "time": "32h 00m",
        "inputs": "2x Military circuit board + 1x Virtex + 1x Microwave",
        "usage": "Requerido FiR para 'Network Provider - Part 1' (acceso a Lightkeeper)",
        "category": "QUEST FiR",
        "icon_key": "craft_cofdm",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/1/10/Tarkov_Merin_%28COFDM%29.png/revision/latest?cb=20230516211845"
    },
    {
        "station": "Nutrition Unit",
        "level": 1,
        "output": "2x Iskra ration pack (Ración Iskra) [FiR]",
        "time": "48m",
        "inputs": "2x Crackers + 1x Tushonka pequeña + 1x Squash spread",
        "usage": "Requerido 3x FiR en el Día 1 del Wipe para 'Acquaintance' (Jaeger)",
        "category": "QUEST FiR",
        "icon_key": "craft_iskra",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/4c/Lunchbox.png/revision/latest?cb=20200702111802"
    },
    {
        "station": "Nutrition Unit",
        "level": 2,
        "output": "2x Can of beef stew (Large Tushonka) [FiR]",
        "time": "1h 32m",
        "inputs": "2x Small Tushonka + 1x Salt + 1x Croutons",
        "usage": "Requerido 2x FiR para 'Acquaintance' (Jaeger) y crafteos de comida",
        "category": "QUEST FiR",
        "icon_key": "craft_tushonka_large",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/7/7b/Can_of_beef_stew_alt.png/revision/latest?cb=20181112155042"
    },
    {
        "station": "Nutrition Unit",
        "level": 3,
        "output": "2x Bottle of Tarkovskaya vodka + 1x Can of Majaica coffee [FiR]",
        "time": "1h 15m",
        "inputs": "Ingredientes de cocina y agua purificada",
        "usage": "Trueques de contenedores (Holodilnick / Thicc) y Scav Case",
        "category": "MATERIAL / QUEST",
        "icon_key": "craft_vodka",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/4/44/Vodka3D.png/revision/latest?cb=20191030042356"
    },
    {
        "station": "Cultist Circle",
        "level": 1,
        "output": "Ritual de 6 Horas (25% prob.) → Ítems exactos de tus Misiones Activas o Hideout [FiR]",
        "time": "6h 00m (o 14h 00m High-Tier)",
        "inputs": "Sacrificio con valor base de Trader ≥ 400,000 RUB (ej: 5x SSD, 5x Slim Diary o 1x Bitcoin)",
        "usage": "Al superar el umbral de 400,000 RUB de valor base, tienes 25% de activar el timer de 6h (te da ítems FiR que te faltan para Quests/Hideout como LEDX, Virtex, COFDM, Tank Battery) y 75% de timer de 14h (botín raro de alto valor).",
        "category": "CÍRCULO CULTISTA",
        "icon_key": "hideout_cultist_circle",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/0/0d/Cultist_Circle_Portrait.png/revision/latest?cb=20240820210535"
    },
    {
        "station": "Cultist Circle",
        "level": 1,
        "output": "Receta Sagrada Fija: 1x Cuchillo Cultista / Figuritas → Ítems Raros",
        "time": "6h 00m",
        "inputs": "1x Figurita de Killa -> Casco Maska 1Sch  |  1x Figurita de Tagilla -> Gorra Boss + Maza  |  1x Figurita de Reshala -> Golden TT",
        "usage": "Las figuritas de jefes tienen recetas únicas de sacrificio garantizado por primera vez en el Círculo Cultista.",
        "category": "CÍRCULO CULTISTA",
        "icon_key": "craft_sacred_amulet",
        "icon_url": "https://static.wikia.nocookie.net/escapefromtarkov_gamepedia/images/d/de/Sacred_Amulet_image.png/revision/latest?cb=20240118202258"
    }
]
