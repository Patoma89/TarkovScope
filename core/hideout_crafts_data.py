"""
TarkovScope - Base de Datos de Crafteos Clave del Hideout (FiR para Misiones, Munición Meta y Círculo Cultista)
Incluye tiempos de fabricación, estación y nivel requerido, materiales de entrada, producto resultante (Found in Raid)
y para qué misión o uso táctico sirve cada receta.
"""
from typing import List, Dict, Any

HIDEOUT_CRAFTS_DATA: List[Dict[str, Any]] = [
    # --- WORKBENCH (MESA DE TRABAJO) ---
    {
        "station": "Workbench",
        "level": 1,
        "output": "2x Wires (Cables eléctricos) [FiR]",
        "time": "1h 23m",
        "inputs": "1x Power cord (Cable de alimentación)",
        "usage": "Material base para Hideout y trueques de Mechanic",
        "category": "MATERIAL / QUEST"
    },
    {
        "station": "Workbench",
        "level": 1,
        "output": "2x Capacitors (Capacitores) [FiR]",
        "time": "1h 12m",
        "inputs": "1x Power supply unit (PSU) + 1x Destornillador",
        "usage": "Requerido Found in Raid para 'Farming - Part 4' (Mechanic)",
        "category": "QUEST FiR"
    },
    {
        "station": "Workbench",
        "level": 2,
        "output": "2x Printed circuit board (PCB) [FiR]",
        "time": "1h 04m",
        "inputs": "1x DVD drive + 1x Destornillador plano",
        "usage": "Requerido FiR para 'Signal - Part 2' (Mechanic)",
        "category": "QUEST FiR"
    },
    {
        "station": "Workbench",
        "level": 2,
        "output": "120x 5.45x39mm PP gs [Meta]",
        "time": "2h 15m",
        "inputs": "120x 5.45x39 PS + 1x Pólvora Verde (Eagle) + 1x Pólvora Azul (Kite)",
        "usage": "Munición perforante consistente para AK-74 / RPK-16 en mid-wipe",
        "category": "MUNICIÓN META"
    },
    {
        "station": "Workbench",
        "level": 2,
        "output": "80x .300 Blackout CBJ [Meta]",
        "time": "3h 10m",
        "inputs": "80x 5.56x45 M855 + 1x Pólvora Roja (Hawk) + 1x Pólvora Azul (Kite)",
        "usage": "Penetración 43 (perfora Clase 4/5) para MCX .300 BLK",
        "category": "MUNICIÓN META"
    },
    {
        "station": "Workbench",
        "level": 3,
        "output": "120x 7.62x39mm BP gzh [Meta]",
        "time": "6h 45m",
        "inputs": "120x 7.62x39 PS + 2x Pólvora Roja (Hawk) + 1x Pólvora Verde (Eagle)",
        "usage": "Penetración 47 (Tier S para Mutant Mk47 y RD-704)",
        "category": "MUNICIÓN META"
    },
    {
        "station": "Workbench",
        "level": 3,
        "output": "80x 7.62x51mm M61 [Meta]",
        "time": "7h 30m",
        "inputs": "80x 7.62x51 M80 + 2x Pólvora Roja (Hawk) + 1x Helix radiator",
        "usage": "Penetración 64 (perfora Clase 6 para SR-25, RSASS y SCAR-H)",
        "category": "MUNICIÓN META"
    },
    {
        "station": "Workbench",
        "level": 3,
        "output": "100x 9x19mm PBP gzh [Meta]",
        "time": "4h 50m",
        "inputs": "100x 9x19 PST + 1x Pólvora Verde (Eagle) + 1x Pólvora Roja (Hawk)",
        "usage": "Penetración 39 a 1100 RPM para Vector 9mm y MPX",
        "category": "MUNICIÓN META"
    },
    # --- MEDSTATION (ESTACIÓN MÉDICA) ---
    {
        "station": "Medstation",
        "level": 1,
        "output": "1x Salewa first aid kit [FiR]",
        "time": "26m",
        "inputs": "1x Car first aid kit + 1x Esmarch tourniquet",
        "usage": "Requerido 3x FiR para 'Shortage' (Therapist — primera misión)",
        "category": "QUEST FiR"
    },
    {
        "station": "Medstation",
        "level": 1,
        "output": "2x Disposable syringe (Jeringa) [FiR]",
        "time": "32m",
        "inputs": "1x Pile of meds + 1x Botella de agua",
        "usage": "Material para inyectores y trueques médicos de Therapist",
        "category": "MATERIAL / QUEST"
    },
    {
        "station": "Medstation",
        "level": 2,
        "output": "1x Morphine injector (Morfina) [FiR]",
        "time": "1h 18m",
        "inputs": "1x Analgin painkillers + 1x Jeringa descartable + 1x Pile of meds",
        "usage": "Requerido 4x FiR para 'Painkiller' (Therapist) y 'Spa Tour - Part 7'",
        "category": "QUEST FiR"
    },
    {
        "station": "Medstation",
        "level": 2,
        "output": "2x IFAK individual first aid kit [FiR]",
        "time": "52m",
        "inputs": "2x Pile of meds + 1x Army bandage + 1x Esmarch",
        "usage": "Botiquín compacto de 1 celda y requisito de misiones médicas",
        "category": "QUEST FiR"
    },
    {
        "station": "Medstation",
        "level": 3,
        "output": "2x Propital regenerative stimulant [Meta]",
        "time": "1h 15m",
        "inputs": "1x Golden Star balm (incluso 1/10 usos) + 1x Ibuprofeno (1/15) + 2x Pile of meds",
        "usage": "Crafteo súper rentable: recicla Golden Star e Ibuprofeno gastados (1 uso restante)",
        "category": "RENTABLE / META"
    },
    {
        "station": "Medstation",
        "level": 3,
        "output": "1x M.U.L.E. stimulant injector [FiR]",
        "time": "2h 10m",
        "inputs": "1x Zagustin + 1x Morphine + 2x Pile of meds",
        "usage": "Requerido FiR para 'Samples' (Peacekeeper) y para llevar 70+ kg de botín",
        "category": "QUEST FiR"
    },
    {
        "station": "Medstation",
        "level": 3,
        "output": "1x SJ6 TGLabs combat stimulant [FiR]",
        "time": "1h 55m",
        "inputs": "2x Adrenaline + 1x NaCl saline solution + 1x Pile of meds",
        "usage": "Estimulante de estamina infinita y misiones de Therapist/Peacekeeper",
        "category": "RENTABLE / META"
    },
    {
        "station": "Medstation",
        "level": 3,
        "output": "1x LEDX Skin Transilluminator [FiR]",
        "time": "10h 00m",
        "inputs": "1x Silicon tube + 1x Gas analyzer + 1x Ophthalmoscope + Manual Microcontroller",
        "usage": "Requerido FiR para 'Private Clinic' (T H I C C Item Case) y 'Crisis' (Therapist)",
        "category": "QUEST FiR"
    },
    # --- LAVATORY (LAVABO / TALLER TEXTIL) ---
    {
        "station": "Lavatory",
        "level": 1,
        "output": "1x Gas mask GP-5 /Filtro [FiR]",
        "time": "22m",
        "inputs": "Materiales básicos de taller",
        "usage": "Trueques iniciales y filtros de aire",
        "category": "MATERIAL / QUEST"
    },
    {
        "station": "Lavatory",
        "level": 2,
        "output": "2x Corrugated hose (Manguera corrugada) [FiR]",
        "time": "2h 05m",
        "inputs": "2x Insulating tape + 1x Silicone tube + 3x Wires",
        "usage": "Requerido FiR para 'Spa Tour - Part 6' y mejoras de Water Collector / Booze Generator",
        "category": "QUEST FiR"
    },
    {
        "station": "Lavatory",
        "level": 2,
        "output": "1x 60-round 5.45x39 6L31 magazine [FiR]",
        "time": "1h 36m",
        "inputs": "4x 30-round 6L23 mags + 1x KEKTAPE",
        "usage": "Requerido 3x FiR para 'Ice Cream Cones' (Prapor) y 'Gunsmith - Part 2'",
        "category": "QUEST FiR"
    },
    {
        "station": "Lavatory",
        "level": 2,
        "output": "1x BlackRock chest rig [FiR]",
        "time": "1h 45m",
        "inputs": "1x Tarzan chest rig + 2x Ripstop fabric + 1x Cordura",
        "usage": "Requerido 2x FiR para 'Sew it Good - Part 4' (Ragman)",
        "category": "QUEST FiR"
    },
    {
        "station": "Lavatory",
        "level": 2,
        "output": "2x Cordura polyamide fabric [FiR]",
        "time": "1h 12m",
        "inputs": "1x Sling backpack + 1x Leatherman Multitool",
        "usage": "Requerido 5x FiR para 'Textile - Part 1' (Ragman)",
        "category": "QUEST FiR"
    },
    {
        "station": "Lavatory",
        "level": 3,
        "output": "2x FP-100 filter absorber [Rentable]",
        "time": "3h 30m",
        "inputs": "2x Water filter (gastado) + 2x Gas mask air filter",
        "usage": "Recicla filtros de agua al 1% para usar en Air Filtering Unit o vender en Flea Market",
        "category": "RENTABLE / META"
    },
    # --- INTELLIGENCE CENTER (CENTRO DE INTELIGENCIA) ---
    {
        "station": "Intelligence Center",
        "level": 2,
        "output": "3x Secure Flash drive (Pendrive) [FiR]",
        "time": "18h 20m",
        "inputs": "1x Topographic survey maps + 2x GPhone X + 1x SSD drive",
        "usage": "Requerido 2x FiR para 'What's on the Flash Drive?' (Skier) y 3x FiR para 'Shady Business' (Jaeger)",
        "category": "QUEST FiR"
    },
    {
        "station": "Intelligence Center",
        "level": 2,
        "output": "1x Virtex programmable processor [FiR]",
        "time": "22h 00m",
        "inputs": "1x Military circuit board + 2x Broken GPhone X + 2x Gold neck chain",
        "usage": "Requerido 2x FiR para 'Lend-Lease - Part 2' (Peacekeeper)",
        "category": "QUEST FiR"
    },
    {
        "station": "Intelligence Center",
        "level": 2,
        "output": "1x UHF RFID Reader [FiR]",
        "time": "20h 40m",
        "inputs": "1x Broken GPhone + 1x Signal Jammer + 2x PCB",
        "usage": "Requerido FiR para 'Lend-Lease - Part 2' y 'Import' (Peacekeeper)",
        "category": "QUEST FiR"
    },
    {
        "station": "Intelligence Center",
        "level": 3,
        "output": "1x Graphics card (GPU) [FiR]",
        "time": "48h 00m",
        "inputs": "1x VPX Flash Storage + 2x CPU + 4xCPU Fan + 2x Power supply unit",
        "usage": "Requerido 3x FiR para 'Farming - Part 4' (Mechanic) y para llenar tu Bitcoin Farm",
        "category": "QUEST FiR"
    },
    {
        "station": "Intelligence Center",
        "level": 3,
        "output": "1x COFDM Wireless Signal Transmitter [FiR]",
        "time": "32h 00m",
        "inputs": "2x Military circuit board + 1x Virtex + 1x Microwave",
        "usage": "Requerido FiR para 'Network Provider - Part 1' (acceso a Lightkeeper)",
        "category": "QUEST FiR"
    },
    # --- NUTRITION UNIT (UNIDAD DE NUTRICIÓN) ---
    {
        "station": "Nutrition Unit",
        "level": 1,
        "output": "2x Iskra ration pack (Ración Iskra) [FiR]",
        "time": "48m",
        "inputs": "2x Crackers + 1x Tushonka pequeña + 1x Squash spread",
        "usage": "Requerido 3x FiR en el Día 1 del Wipe para 'Acquaintance' (Jaeger)",
        "category": "QUEST FiR"
    },
    {
        "station": "Nutrition Unit",
        "level": 2,
        "output": "2x Can of beef stew (Large Tushonka) [FiR]",
        "time": "1h 32m",
        "inputs": "2x Small Tushonka + 1x Salt + 1x Croutons",
        "usage": "Requerido 15x FiR para 'General Wares' (Therapist)",
        "category": "QUEST FiR"
    },
    {
        "station": "Nutrition Unit",
        "level": 3,
        "output": "2x Bottle of Tarkovskaya vodka + 1x Can of Majaica coffee [FiR]",
        "time": "1h 15m",
        "inputs": "Ingredientes de cocina y agua purificada",
        "usage": "Trueques de contenedores y misión Collector (Majaica Coffee)",
        "category": "MATERIAL / QUEST"
    },
    # --- CULTIST CIRCLE (CÍRCULO CULTISTA) ---
    {
        "station": "Cultist Circle",
        "level": 1,
        "output": "Ritual de 6 Horas (25% prob.) → Ítems exactos de tus Misiones Activas o Hideout [FiR]",
        "time": "6h 00m (o 14h 00m High-Tier)",
        "inputs": "Sacrificio con valor base de Trader ≥ 400,000 RUB (ej: 5x SSD, 5x Slim Diary o 1x Bitcoin)",
        "usage": "Al superar el umbral de 400,000 RUB de valor base, tienes 25% de activar el timer de 6h (te da ítems FiR que te faltan para Quests/Hideout como LEDX, Virtex, COFDM, Tank Battery) y 75% de timer de 14h (botín raro de alto valor).",
        "category": "CÍRCULO CULTISTA"
    },
    {
        "station": "Cultist Circle",
        "level": 1,
        "output": "Receta Sagrada Fija: 1x Cuchillo Cultista / Figuritas → Ítems Raros",
        "time": "6h 00m",
        "inputs": "1x Figurita de Killa -> Casco Maska 1Sch  |  1x Figurita de Tagilla -> Gorra Boss + Maza  |  1x Figurita de Reshala -> Golden TT",
        "usage": "Las figuritas de jefes tienen recetas únicas de sacrificio garantizado por primera vez en el Círculo Cultista.",
        "category": "CÍRCULO CULTISTA"
    }
]
