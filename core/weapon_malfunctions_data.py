"""
TarkovScope - Datos Puros de Fallas de Arma (Malfunctions), Durabilidad y Repair Kits (EFT Wiki)
Cero dependencias de UI / Tkinter.
"""
from typing import Any, Dict, List


WEAPON_MALFUNCTIONS_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "malf_misfire",
        "name_es": "Misfire (Fallo de Ignición)",
        "name_en": "Misfire",
        "min_durability_threshold": "< 93% Durabilidad",
        "causes_es": "El percutor golpea el fulminante pero el cartucho no detona (probabilidad base de la munición + baja durabilidad del arma).",
        "causes_en": "Firing pin strikes the primer without ignition (ammo misfire chance + low gun durability).",
        "fix_steps_es": [
            "1. Pulsa [L] (Inspeccionar Arma) — obligatorio para identificar el tipo de traba.",
            "2. Pulsa [Shift + T] (Despejar / Clear Jam) para expulsar el cartucho fallido y recargar recámara.",
        ],
        "fix_steps_en": [
            "1. Press [L] (Inspect Weapon) — mandatory to identify the jam.",
            "2. Press [Shift + T] (Check/Clear Chamber) to eject the dud round.",
        ],
        "pro_tip_es": "TIP PRO: Puedes remapear 'Inspect Weapon' (Presionar L) y 'Check Chamber' (Soltar L) a la MISMA tecla para resolver cualquier falla en 1 toque.",
        "pro_tip_en": "PRO TIP: Bind 'Inspect' on Press and 'Clear Malfunction' on Release of the same key to fix jams seamlessly.",
    },
    {
        "id": "malf_fail_to_feed",
        "name_es": "Failure to Feed (Fallo de Alimentación)",
        "name_en": "Failure to Feed",
        "min_durability_threshold": "< 93% Durabilidad",
        "causes_es": "El cerrojo no logra introducir la siguiente bala desde el cargador hacia la recámara (cargadores de alta capacidad / suciedad).",
        "causes_en": "Bolt fails to strip and feed the next round from magazine into the chamber (high-cap mags / wear).",
        "fix_steps_es": [
            "1. Pulsa [L] para inspeccionar el alojamiento del cargador y el cerrojo.",
            "2. Pulsa [Shift + T] para realinear el ciclo y alimentar el cartucho.",
        ],
        "fix_steps_en": [
            "1. Press [L] to inspect the feed ramp and bolt.",
            "2. Press [Shift + T] to rack and feed a fresh round.",
        ],
        "pro_tip_es": "Los cargadores de tambor (60/95/100 balas) tienen mayor probabilidad de Failure to Feed que los de 30.",
        "pro_tip_en": "Drum and 60-round magazines carry a higher Failure to Feed chance modifier than 30-rounders.",
    },
    {
        "id": "malf_fail_to_eject",
        "name_es": "Failure to Eject / Stovepipe (Fallo de Expulsión)",
        "name_en": "Failure to Eject (Stovepipe)",
        "min_durability_threshold": "< 93% Durabilidad",
        "causes_es": "La vaina servida queda atrapada en la ventana de expulsión bloqueando el cierre del cerrojo.",
        "causes_en": "Spent casing gets caught in the ejection port, blocking the bolt from closing.",
        "fix_steps_es": [
            "1. Pulsa [L] para inspeccionar la ventana de expulsión.",
            "2. Pulsa [Shift + T] para limpiar manualmente la vaina atrapada.",
        ],
        "fix_steps_en": [
            "1. Press [L] to inspect the ejection port.",
            "2. Press [Shift + T] to manually clear the trapped brass casing.",
        ],
        "pro_tip_es": "Armas de Scavs (40-60% durabilidad) sufren Failure to Eject con muchísima frecuencia: nunca entres a PvP con armas sin reparar bajo 93%.",
        "pro_tip_en": "Scav guns (40-60% durability) suffer frequent stovepipes — never bring weapons below 93% into PvP.",
    },
    {
        "id": "malf_bolt_jam",
        "name_es": "Bolt Jam / Hard Jam (Cerrojo Trabado)",
        "name_en": "Bolt Jam (Hard Jam)",
        "min_durability_threshold": "< 93% Durabilidad (o Boss Kollontay)",
        "causes_es": "Desgaste severo del arma (<85%) o el debuff de pánico al acercarse demasiado al Boss Kollontay cuando saca su porra.",
        "causes_en": "Severe weapon wear (<85%) or Kollontay's Panic aura when he draws his police baton.",
        "fix_steps_es": [
            "1. Pulsa [L] para inspeccionar el cerrojo bloqueado.",
            "2. Pulsa [Shift + T] para forzar la liberación del cerrojo (animación ligeramente más larga).",
        ],
        "fix_steps_en": [
            "1. Press [L] to inspect the seized bolt.",
            "2. Press [Shift + T] to force the bolt back into battery (slightly longer animation).",
        ],
        "pro_tip_es": "Si peleas contra Kollontay en Streets/Ground Zero, mantén distancia o cambia a arma secundaria/PPSH (la PPSH de cerrojo abierto nunca se traba).",
        "pro_tip_en": "Against Kollontay, keep distance or switch to a backup — open-bolt guns like the PPSh-41 cannot jam.",
    },
    {
        "id": "malf_overheat_jam",
        "name_es": "Overheat Jam (Bloqueo por Sobrecalentamiento)",
        "name_en": "Overheat Jam",
        "min_durability_threshold": "Cualquier Durabilidad (incluso 100%)",
        "causes_es": "Disparar ráfagas continuas largas (especialmente con silenciador) superando la temperatura crítica del cañón.",
        "causes_en": "Sustained automatic fire (amplified by suppressors) exceeding critical barrel heat.",
        "fix_steps_es": [
            "1. Espera 2-3 segundos si el cañón brilla al rojo vivo o cambia a cobertura.",
            "2. Pulsa [L] para inspeccionar y luego [Shift + T] para despejar el cerrojo fundido/trabado.",
        ],
        "fix_steps_en": [
            "1. Break line of sight while the barrel cools slightly.",
            "2. Press [L] to inspect and [Shift + T] to clear the seized bolt.",
        ],
        "pro_tip_es": "El Overheat Jam puede ocurrir incluso en un arma nueva al 100%. Además reduce drásticamente el MOA (precisión) mientras el cañón está caliente.",
        "pro_tip_en": "Overheat Jams can occur even at 100% durability and degrade barrel MOA accuracy while hot.",
    },
]


DURABILITY_AND_REPAIR_GUIDE: Dict[str, Any] = {
    "threshold_93_title_es": "La Regla de Oro del 93% de Durabilidad",
    "threshold_93_title_en": "The Golden 93% Durability Rule",
    "threshold_93_desc_es": (
        "En Escape from Tarkov, NINGUNA falla mecánica (Misfire, Feed, Eject, Bolt Jam) puede ocurrir mientras "
        "la durabilidad actual del arma esté por encima del 93.0%. Solo el Overheat Jam (por fuego continuo "
        "extremo) puede trabar un arma por encima de ese umbral. Si tu receptor (lower receiver) baja de 93% máx, "
        "compra un nuevo receptor en el Flea o comerciante y traslada todos tus accesorios."
    ),
    "threshold_93_desc_en": (
        "In Escape from Tarkov, NO mechanical malfunction (Misfire, Feed, Eject, Bolt Jam) can trigger while "
        "weapon durability stays above 93.0%. Only Overheat Jams can happen above 93%. Once maximum durability "
        "drops below 93%, buy a fresh receiver and swap all your attachments onto it."
    ),
    "overheat_stages": [
        {
            "stage": "Fase 1 (Templada / Mild)",
            "heat": "100–130 pts",
            "effects_es": "Humo leve del guardamanos. Precisión intacta, sin riesgo de traba.",
            "effects_en": "Light smoke from handguard. Accuracy intact, no jam risk.",
        },
        {
            "stage": "Fase 2 (Caliente / Medium)",
            "heat": "130–170 pts",
            "effects_es": "Mirage térmico visible en la mira. Aumenta desgaste de durabilidad por disparo.",
            "effects_en": "Visible heat mirage in optics. Increased durability burn per shot.",
        },
        {
            "stage": "Fase 3 (Severa / Red Glow)",
            "heat": "170–220 pts",
            "effects_es": "El cañón y silenciador brillan rojo; el MOA empeora drásticamente y sube riesgo de Overheat Jam.",
            "effects_en": "Red glowing barrel/suppressor; severe MOA degradation & Overheat Jam risk.",
        },
        {
            "stage": "Fase 4 (Crítica / Failure)",
            "heat": "> 220 pts",
            "effects_es": "Probabilidad muy alta de Overheat Jam instantáneo hasta enfriarse.",
            "effects_en": "Very high instant Overheat Jam probability until cooled down.",
        },
    ],
    "repair_kits_guide": [
        {
            "title_es": "Weapon Repair Kit (Kit de Reparación de Armas)",
            "title_en": "Weapon Repair Kit",
            "detail_es": (
                "Repara armas desde tu Alijo mucho más barato que Mechanic/Prapor, pierde menos durabilidad máxima "
                "y sube rápidamente la skill 'Weapon Maintenance'. Al nivel 10+ permite obtener Enhancements "
                "(Common/Rare) con -15% a -45% probabilidad de falla o mejor precisión (MOA)."
            ),
            "detail_en": (
                "Repairs guns in stash far cheaper than Mechanic/Prapor with lower max-durability loss while leveling "
                "'Weapon Maintenance'. At Lv.10+ unlocks Common/Rare Enhancements (malfunction reduction or MOA boost)."
            ),
        },
        {
            "title_es": "Body Armor Repair Kit (Kit de Blindaje)",
            "title_en": "Body Armor Repair Kit",
            "detail_es": (
                "Repara chalecos, cascos y placas de aramida/acero/titanio. Sube las skills 'Light Vests' y 'Heavy Vests', "
                "habilitando Enhancements dorados de mitigación de daño balístico."
            ),
            "detail_en": (
                "Repairs vests, helmets, and armor plates. Levels 'Light/Heavy Vests' skills and grants Rare "
                "golden ballistic damage-reduction Enhancements."
            ),
        },
        {
            "title_es": "¿Qué Trader usar si no tienes Repair Kit?",
            "title_en": "Which Trader to use without a Repair Kit?",
            "detail_es": (
                "• Mechanic: mejor calidad (menor pérdida de durabilidad máxima), pero más caro.\n"
                "• Skier: balance medio en costo/pérdida.\n"
                "• Prapor: más barato, pero destruye mucha durabilidad máxima."
            ),
            "detail_en": (
                "• Mechanic: Best quality (lowest max durability loss), highest cost.\n"
                "• Skier: Mid-tier cost and max loss.\n"
                "• Prapor: Cheapest, highest max durability loss."
            ),
        },
    ],
}
