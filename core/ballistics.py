"""
TarkovScope - Módulo de Balística, Cálculo de Penetración y Simulador STK / TTK
Calcula la efectividad de penetración de cada proyectil frente a las 6 clases de blindaje de Tarkov,
disparos para matar al tórax (STK), tiempo para matar (TTK), Leg Meta y efectividad contra Bosses.
"""
import math
from typing import Dict, Any, List


def calculate_armor_effectiveness(penetration_power: float, armor_class: int) -> Dict[str, Any]:
    """
    Calcula el nivel de efectividad (1 a 6) de una bala contra una clase de armadura (1 a 6).
    Devuelve un diccionario con score (0 a 6), etiqueta descriptiva y color hexadecimal.
    
    Escala oficial inspirada en NoFoodAfterMidnight:
    - 6: Penetra con facilidad (>90% de probabilidad en el 1er tiro)
    - 5: Muy alta probabilidad (80-90%)
    - 4: Buena efectividad (50-75%)
    - 3: Efectividad moderada (20-45%, requiere desgastar la armadura)
    - 2: Baja probabilidad (5-15%)
    - 1: Despreciable / Nula (<5%, rebote o absorbida)
    """
    threshold = armor_class * 10.0
    diff = penetration_power - threshold

    if diff >= 5.0:
        score = 6
        label = "Destruye"
        color = "#10B981"  # Verde esmeralda brillante
    elif diff >= 0.0:
        score = 5
        label = "Muy Alta"
        color = "#34D399"  # Verde claro
    elif diff >= -5.0:
        score = 4
        label = "Alta"
        color = "#A3E635"  # Lima
    elif diff >= -10.0:
        score = 3
        label = "Media"
        color = "#FBBF24"  # Amarillo
    elif diff >= -15.0:
        score = 2
        label = "Baja"
        color = "#F97316"  # Naranja
    else:
        score = 1
        label = "Rebota"
        color = "#EF4444"  # Rojo

    return {
        "score": score,
        "label": label,
        "color": color,
        "armor_class": armor_class
    }


def get_full_ballistics_matrix(penetration_power: float) -> Dict[int, Dict[str, Any]]:
    """Calcula la efectividad para todas las clases de armadura (1 al 6)."""
    return {
        ac: calculate_armor_effectiveness(penetration_power, ac)
        for ac in range(1, 7)
    }


def build_armor_matrix(penetration_power: float) -> Dict[int, int]:
    """Retorna un diccionario {clase_armadura: score_1_a_6}."""
    return {
        ac: calculate_armor_effectiveness(penetration_power, ac)["score"]
        for ac in range(1, 7)
    }


def get_armor_rating_color(score: int) -> str:
    """Retorna el color hexadecimal asociado a un score de penetración (1 a 6)."""
    colors = {
        6: "#10B981",
        5: "#34D399",
        4: "#A3E635",
        3: "#FBBF24",
        2: "#F97316",
        1: "#EF4444",
    }
    return colors.get(score, "#EF4444")


def simulate_shots_to_kill(
    damage: int,
    penetration_power: float,
    armor_damage: int,
    armor_class: int,
    target_hp: float = 85.0,
    max_durability: float = 50.0,
    rpm: int = 700,
) -> Dict[str, Any]:
    """
    Simula disparo a disparo el impacto contra un tórax de PMC (85 HP por defecto)
    protegido por una placa balística de Clase `armor_class` (1 a 6).
    Devuelve:
      - stk: Disparos estimados para abatir (Shots To Kill, 1 a 30)
      - ttk_ms: Tiempo para abatir en milisegundos a `rpm` disparos por minuto
      - first_shot_pen_pct: Probabilidad estimada de penetración en el 1er impacto (0 a 98%)
    """
    if damage <= 0 and penetration_power <= 0:
        return {"stk": 0, "ttk_ms": 0, "first_shot_pen_pct": 0, "is_utility": True}

    dmg = max(1.0, float(damage))
    pen = max(0.0, float(penetration_power))
    admg_ratio = max(5.0, float(armor_damage)) / 100.0

    if armor_class <= 0:
        stk = max(1, math.ceil(target_hp / dmg))
        ttk_ms = int(round((stk - 1) * (60000.0 / max(1, rpm))))
        return {"stk": stk, "ttk_ms": ttk_ms, "first_shot_pen_pct": 100}

    base_threshold = armor_class * 10.0
    diff_initial = pen - base_threshold
    if diff_initial >= 8.0:
        first_pen_pct = 97
    elif diff_initial >= 3.0:
        first_pen_pct = 90
    elif diff_initial >= 0.0:
        first_pen_pct = 80
    elif diff_initial >= -5.0:
        first_pen_pct = 55
    elif diff_initial >= -10.0:
        first_pen_pct = 25
    elif diff_initial >= -15.0:
        first_pen_pct = 8
    else:
        first_pen_pct = 1

    hp = float(target_hp)
    dur = float(max_durability)
    shots = 0

    while hp > 0.0 and shots < 30:
        shots += 1
        eff_threshold = base_threshold * (0.35 + 0.65 * (dur / max_durability))
        diff = pen - eff_threshold

        if dur <= 1.0 or diff >= 3.0:
            # Penetración limpia
            mitigation = 1.0 if (dur <= 1.0 or diff >= 4.0) else min(1.0, max(0.82, 0.88 + 0.03 * diff))
            hp -= dmg * mitigation
            dur = max(0.0, dur - max(2.5, pen * admg_ratio * 0.45))
        elif diff >= -4.0:
            # Penetración marginal / transición de ruptura
            hp -= dmg * 0.52
            dur = max(0.0, dur - max(4.0, pen * admg_ratio * 0.65))
        elif diff >= -11.0:
            # Frena pero fractura rápido el blindaje
            hp -= max(1.5, dmg * 0.08)
            dur = max(0.0, dur - max(3.5, pen * admg_ratio * 0.58))
        else:
            # Rebote o absorción pesada (daño contundente mínimo)
            hp -= max(1.0, dmg * 0.03)
            dur = max(0.0, dur - max(1.5, pen * admg_ratio * 0.32))

    ttk_ms = int(round((shots - 1) * (60000.0 / max(1, rpm))))
    return {
        "stk": shots,
        "ttk_ms": ttk_ms,
        "first_shot_pen_pct": first_pen_pct,
    }


def calculate_leg_meta_shots(damage: int, total_pmc_hp: int = 440) -> int:
    """
    Calcula los disparos necesarios a las piernas (sin blindaje) para abatir a un PMC (440 HP).
    Toma en cuenta el multiplicador de desbordamiento en extremidades destruidas.
    """
    if damage <= 0:
        return 0
    dmg = max(1, int(damage))
    if dmg >= total_pmc_hp:
        return 1
    # Primeros 65 HP destruyen la pierna; el resto se transfiere al cuerpo a factor ~0.88 efectivo
    effective_per_shot = dmg * 0.90
    return max(1, math.ceil(total_pmc_hp / effective_per_shot))


def simulate_boss_targets(damage: int, penetration_power: float, armor_damage: int) -> List[Dict[str, Any]]:
    """
    Simula cuántos disparos requiere este proyectil contra 4 objetivos icónicos de Bosses:
      1. Killa (Visor Maska-1SCh Clase 6 • Cabeza 70 HP)
      2. Tagilla (Máscara Soldador UBEY Clase 5 • Cabeza 100 HP)
      3. Knight / Big Pipe (Placa Clase 5 • Tórax 220 HP)
      4. Zryachiy (Sin Casco • Cabeza 175 HP a larga distancia)
    """
    if damage <= 0 and penetration_power <= 0:
        return [
            {"target": "Proyectil Especial / Utilidad (Sin daño balístico)", "stk": 0, "pen_pct": 0, "verdict": "No letal / Cartucho de señal o flash"}
        ]

    killa_sim = simulate_shots_to_kill(damage, penetration_power, armor_damage, armor_class=6, target_hp=70.0, max_durability=50.0)
    tagilla_sim = simulate_shots_to_kill(damage, penetration_power, armor_damage, armor_class=5, target_hp=100.0, max_durability=45.0)
    goons_sim = simulate_shots_to_kill(damage, penetration_power, armor_damage, armor_class=5, target_hp=220.0, max_durability=60.0)
    zryachiy_shots = max(1, math.ceil(175.0 / max(1, damage)))

    return [
        {
            "target": "Killa (Visor Maska Clase 6 • 70 HP)",
            "stk": killa_sim["stk"],
            "pen_pct": killa_sim["first_shot_pen_pct"],
            "verdict": "One-Tap letal al visor" if killa_sim["stk"] == 1 else f"{killa_sim['stk']} impactos al visor",
        },
        {
            "target": "Tagilla (Máscara UBEY Clase 5 • 100 HP)",
            "stk": tagilla_sim["stk"],
            "pen_pct": tagilla_sim["first_shot_pen_pct"],
            "verdict": "Abate de 1 tiro en cabeza" if tagilla_sim["stk"] == 1 else f"{tagilla_sim['stk']} tiros a la máscara",
        },
        {
            "target": "The Goons (Tórax Clase 5 • 220 HP)",
            "stk": goons_sim["stk"],
            "pen_pct": goons_sim["first_shot_pen_pct"],
            "verdict": f"Ráfaga de {goons_sim['stk']} tiros al pecho ({goons_sim['ttk_ms']} ms)",
        },
        {
            "target": "Zryachiy (Cabeza sin casco • 175 HP)",
            "stk": zryachiy_shots,
            "pen_pct": 100,
            "verdict": "✅ One-Tap (≥175 daño)" if zryachiy_shots == 1 else f"⚠️ Requiere {zryachiy_shots} headshots (daño < 175)",
        },
    ]


