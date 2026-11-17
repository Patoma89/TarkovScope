"""
TarkovScope - Motor de Horario Oficial In-Raid de Escape from Tarkov
Calcula los dos relojes oficiales de incursión (ciclo 7x respecto al tiempo real,
con +3h MSK en el horario izquierdo y desfase exacto de +12h en el derecho)
y detecta automáticamente la ventana nocturna / aparición de Cultists (22:00-07:00).
"""
import time
from typing import Any, Dict, Optional

TARKOV_TIME_MULTIPLIER = 7
MSK_OFFSET_MS = 3 * 3600 * 1000
RIGHT_CLOCK_OFFSET_MS = 12 * 3600 * 1000
DAY_MS = 24 * 3600 * 1000


def _format_ms_parts(ms_in_day: int) -> tuple[int, int, int, str, str, bool]:
    """Descompone milisegundos del día en (h, m, s, HH:MM:SS, HH:MM, is_night)."""
    total_seconds = (ms_in_day // 1000) % 86400
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    full_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    short_str = f"{hours:02d}:{minutes:02d}"
    is_night = hours >= 22 or hours < 7
    return hours, minutes, seconds, full_str, short_str, is_night


def get_tarkov_raid_times(utc_timestamp: Optional[float] = None) -> Dict[str, Any]:
    """Calcula ambos relojes de incursión de Tarkov y el estado nocturno/Cultists."""
    ts = time.time() if utc_timestamp is None else float(utc_timestamp)
    tarkov_ms = int(ts * 1000 * TARKOV_TIME_MULTIPLIER)
    left_ms = (tarkov_ms + MSK_OFFSET_MS) % DAY_MS
    right_ms = (left_ms + RIGHT_CLOCK_OFFSET_MS) % DAY_MS

    l_h, l_m, l_s, left_str, left_short, left_is_night = _format_ms_parts(left_ms)
    r_h, r_m, r_s, right_str, right_short, right_is_night = _format_ms_parts(right_ms)

    return {
        "left_hour": l_h,
        "left_minute": l_m,
        "left_second": l_s,
        "left_time": left_str,
        "left_short": left_short,
        "left_is_night": left_is_night,
        "right_hour": r_h,
        "right_minute": r_m,
        "right_second": r_s,
        "right_time": right_str,
        "right_short": right_short,
        "right_is_night": right_is_night,
        "cultists_window_active": left_is_night or right_is_night,
    }
