"""TarkovScope - Constantes y helpers compartidos de la pestana de Balistica.
"""
import re
from typing import Dict, Tuple
from ui.theme import C_AMBER, C_BG_INSET, C_RED_DARK, C_WHITE


CALIBER_CLEAN_MAP: Dict[str, Tuple[str, str]] = {
    "Caliber127x33": ("Calibre .50 Action Express (.50 AE)", ".50 AE"),
    "Caliber50AE": ("Calibre .50 Action Express (.50 AE)", ".50 AE"),
    "Caliber58x42": ("Calibre 5.8x42 mm", "5.8x42"),
    "Caliber93x64": ("Calibre 9.3x64 mm Brenneke", "9.3x64"),
    "Caliber545x39": ("Calibre 5.45x39", "5.45x39"),
    "Caliber556x45NATO": ("Calibre 5.56x45 NATO", "5.56x45 NATO"),
    "Caliber762x39": ("Calibre 7.62x39", "7.62x39"),
    "Caliber762x51": ("Calibre 7.62x51 NATO", "7.62x51 NATO"),
    "Caliber762x54R": ("Calibre 7.62x54R", "7.62x54R"),
    "Caliber762x35": ("Calibre 7.62x35 (.300 BLK)", "7.62x35 BLK"),
    "Caliber68x51": ("Calibre 6.8x51 (.277 Fury)", "6.8x51 Fury"),
    "Caliber9x39": ("Calibre 9x39", "9x39"),
    "Caliber9x19PARA": ("Calibre 9x19 Parabellum", "9x19 Para"),
    "Caliber1143x23ACP": ("Calibre 11.43x23 (.45 ACP)", "11.43x23 ACP"),
    "Caliber57x28": ("Calibre 5.7x28 FN", "5.7x28 FN"),
    "Caliber46x30": ("Calibre 4.6x30 HK", "4.6x30 HK"),
    "Caliber9x21": ("Calibre 9x21 Gyurza", "9x21 Gyurza"),
    "Caliber9x18PM": ("Calibre 9x18 PM", "9x18 PM"),
    "Caliber762x25TT": ("Calibre 7.62x25 TT", "7.62x25 TT"),
    "Caliber9x33R": ("Calibre 9x33R (.357 Mag)", "9x33R .357"),
    "Caliber366TKM": ("Calibre .366 TKM", ".366 TKM"),
    "Caliber127x55": ("Calibre 12.7x55 (ASh-12)", "12.7x55"),
    "Caliber86x70": ("Calibre 8.6x70 (.338 Lapua)", "8.6x70 .338"),
    "Caliber127x108": ("Calibre 12.7x108", "12.7x108"),
    "Caliber127x99": ("Calibre 12.7x99 mm (.50 BMG)", ".50 BMG"),
    "Caliber12g": ("Calibre 12/70 (12 Gauge)", "12/70 (12g)"),
    "Caliber20g": ("Calibre 20/70 (20 Gauge)", "20/70 (20g)"),
    "Caliber23x75": ("Calibre 23x75 (KS-23)", "23x75 KS-23"),
    "Caliber40x46": ("Calibre 40x46 mm (GL)", "40x46 mm"),
    "Caliber40mmRU": ("Calibre 40 mm VOG", "40 mm VOG"),
    "Caliber30x29": ("Calibre 30x29 mm (AGS)", "30x29 mm"),
    "Caliber26x75": ("Calibre 26x75 (Bengala)", "26x75"),
}

def format_caliber_dropdown(raw_cal: str) -> str:
    """Convierte 'Caliber556x45NATO' -> 'Calibre 5.56x45 NATO' con espacio entre Calibre y el número."""
    if not raw_cal or raw_cal == "TODOS":
        return "TODOS LOS CALIBRES"
    if raw_cal in CALIBER_CLEAN_MAP:
        return CALIBER_CLEAN_MAP[raw_cal][0]
    cleaned = re.sub(r"^Caliber\s*", "", raw_cal, flags=re.IGNORECASE)
    cleaned = re.sub(r"([0-9])([A-Za-z])", r"\1 \2", cleaned)
    return f"Calibre {cleaned}"

def format_caliber_short(raw_cal: str) -> str:
    """Convierte 'Caliber556x45NATO' -> '5.56x45 NATO' para la columna CALIBRE de la tabla."""
    if not raw_cal:
        return "—"
    if raw_cal in CALIBER_CLEAN_MAP:
        return CALIBER_CLEAN_MAP[raw_cal][1]
    cleaned = re.sub(r"^Caliber\s*", "", raw_cal, flags=re.IGNORECASE)
    return re.sub(r"([0-9])([A-Za-z])", r"\1 \2", cleaned)

COLUMNS_SPEC = [
    # (Título, Ancho fijo en px, Campo de ordenamiento, Alineación)
    ("CALIBRE", 132, "caliber", "w"),
    ("PROYECTIL", 180, "name", "w"),
    ("DAÑO ↕", 64, "damage", "center"),
    ("PEN. ↕", 68, "penetration_power", "center"),
    ("DAÑO ARM. ↕", 84, "armor_damage", "center"),
    ("VEL. m/s ↕", 76, "initial_speed", "center"),
    ("CLASS\n1", 44, None, "center"),
    ("CLASS\n2", 44, None, "center"),
    ("CLASS\n3", 44, None, "center"),
    ("CLASS\n4", 44, None, "center"),
    ("CLASS\n5", 44, None, "center"),
    ("CLASS\n6", 44, None, "center"),
]

CLASS_SCORE_COLORS = {
    6: ("#34D359", C_BG_INSET),  # 6: Verde brillante (Pasa >90%)
    5: ("#78D637", C_BG_INSET),  # 5: Verde lima (Alta 80-90%)
    4: ("#B5BD2B", C_BG_INSET),  # 4: Oliva/Amarillo verdoso (Buena 50-75%)
    3: (C_AMBER, C_BG_INSET),  # 3: Naranja/Ámbar (Media)
    2: ("#EA580C", C_WHITE),  # 2: Naranja rojizo (Baja)
    1: (C_RED_DARK, C_WHITE),  # 1: Rojo intenso (Nula / Rebota)
}
