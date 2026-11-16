"""
TarkovScope - Sistemas de PMC, Skills, Scav Karma (Fence), BTR Driver & Red de Transits
Datos verificados contra la Wiki oficial de Escape from Tarkov en español táctico.
Módulo de lógica pura (sin dependencias de UI).
"""
from typing import Any, Dict, List


PMC_SKILLS_CATALOG: List[Dict[str, Any]] = [
    # --- FÍSICA (7) ---
    {
        "id": "endurance",
        "name": "Endurance (Resistencia)",
        "short_name": "Endurance",
        "category": "Física",
        "cache_key": "skill_endurance",
        "requirements": "Heating Nv. 2 (Nv. 1) · Security Nv. 2 (Nv. 2)",
        "effects": (
            "• +1% stamina máxima por nivel (+50% en Nv. 50)\n"
            "• -0.6% costo de stamina al saltar por nivel (-30% en Élite)\n"
            "• +2% duración de contención de respiración al apuntar (+100% en Élite)\n"
            "• -1% tiempo de recuperación de respiración por nivel (-50% en Élite)"
        ),
        "elite_perk": (
            "• +20% stamina adicional (+70% total acumulado)\n"
            "• Mayor resistencia en brazos al apuntar\n"
            "• La recuperación de respiración deja de depender del nivel de energía"
        ),
        "how_to_level": (
            "• Caminar o esprintar SIN sobrepeso (<33.77% de tu peso máximo límite)\n"
            "• Sesiones de entrenamiento en el Gimnasio del Hideout\n"
            "• Quests: A Life Lesson · Never Too Late To Learn"
        ),
        "note": "",
    },
    {
        "id": "strength",
        "name": "Strength (Fuerza)",
        "short_name": "Strength",
        "category": "Física",
        "cache_key": "skill_strength",
        "requirements": "Batya (Historia Nv. 15) · Vents Nv. 3 (Nv. 2)",
        "effects": (
            "• +0.6% límite de carga por nivel (+30% en Élite: hasta ~100 kg)\n"
            "• +0.4% velocidad de movimiento/sprint y altura de salto (+20% en Élite)\n"
            "• +0.6% potencia de golpe cuerpo a cuerpo (+30% en Élite)\n"
            "• +0.4% distancia de lanzamiento de granadas (+20% en Élite)\n"
            "• -0.4% consumo de stamina de brazo al apuntar (+20% en Élite)"
        ),
        "elite_perk": (
            "• Las armas equipadas en bandolera (sling) y espalda dejan de sumar peso al personaje\n"
            "• +50% probabilidad de golpe crítico cuerpo a cuerpo"
        ),
        "how_to_level": (
            "• Caminar o esprintar con sobrepeso (>33.77% de tu peso máximo límite)\n"
            "• Lanzar granadas y golpear con armas cuerpo a cuerpo\n"
            "• Sesiones en el Gimnasio · Quests: A Life Lesson · Never Too Late To Learn"
        ),
        "note": "",
    },
    {
        "id": "vitality",
        "name": "Vitality (Vitalidad)",
        "short_name": "Vitality",
        "category": "Física",
        "cache_key": "skill_vitality",
        "requirements": "Medstation Nv. 3 (Nv. 3)",
        "effects": (
            "• -1.2% probabilidad de sufrir hemorragia por nivel (-60% en Élite)\n"
            "• -0.5% probabilidad de muerte instantánea por extremidad en negro (-20% en Élite)"
        ),
        "elite_perk": (
            "• Todas las hemorragias se detienen solas (leves tras 20s y graves tras 30s sin usar vendas/torniquetes)\n"
            "• Mayor regeneración de salud en combate"
        ),
        "how_to_level": (
            "• 0.01 pts por cada 5 de daño recibido (+0.3 pts al sufrir sangrado)\n"
            "• Tip: recibir sangrado grave y usar Propital para aguantar daño constante\n"
            "• Quests: Get a Foothold · Profit Retention · Decontamination Service"
        ),
        "note": "",
    },
    {
        "id": "health",
        "name": "Health (Salud)",
        "short_name": "Health",
        "category": "Física",
        "cache_key": "skill_health",
        "requirements": "Health Care Privacy Pt. 4 (Nv. 4) · Medstation Nv. 2 (Nv. 2)",
        "effects": (
            "• -1.2% probabilidad de fractura en extremidades (-60% en Élite)\n"
            "• -0.6% consumo de energía por nivel (-30% en Élite)\n"
            "• -0.6% tasa de deshidratación por nivel (-30% en Élite)"
        ),
        "elite_perk": (
            "• Absorción de daño (Damage absorption)"
        ),
        "how_to_level": (
            "• Gana automáticamente el 25% de los puntos que subas en Endurance, Strength o Vitality\n"
            "• Quests: Get a Foothold · Profit Retention · Beneath The Streets"
        ),
        "note": "⚠️ Nota Wiki: la mecánica exacta de 'Damage absorption' del nivel Élite no tiene reducción de daño verificada.",
    },
    {
        "id": "metabolism",
        "name": "Metabolism (Metabolismo)",
        "short_name": "Metabolism",
        "category": "Física",
        "cache_key": "skill_metabolism",
        "requirements": "Nutrition Unit Nv. 3 (Nv. 3)",
        "effects": (
            "• +1% efectos positivos de comida y bebida por nivel (+50% en Élite)\n"
            "• -1% duración de efectos negativos de estimulantes, comida y agua (-50% en Élite)"
        ),
        "elite_perk": (
            "• Inmunidad total al daño de salud por agotamiento (0 Energía) y deshidratación (0 Agua)"
        ),
        "how_to_level": (
            "• Restaurar energía o hidratación DENTRO del raid (depende de cuánta energía/agua recuperes, no funciona en el alijo)\n"
            "• Quests: Never Too Late To Learn · A Life Lesson"
        ),
        "note": "En nivel Élite, la regeneración de stamina sigue penalizada si llegás a 0 de energía o agua.",
    },
    {
        "id": "stress_resistance",
        "name": "Stress Resistance",
        "short_name": "Stress Res.",
        "category": "Física",
        "cache_key": "skill_stress_resistance",
        "requirements": "Batya (Historia Nv. 10)",
        "effects": (
            "• -1% probabilidad de sufrir shock por dolor (-50% en Élite)\n"
            "• -1.2% oscilación de tremor/temblor por nivel (-60% en Élite)"
        ),
        "elite_perk": (
            "• Acceso al modo Berserk al recibir daño crítico"
        ),
        "how_to_level": (
            "• 0.033 pts/s mientras tengas menos de 130 HP totales · 0.33 pts al recibir efecto Dolor\n"
            "• Quests: Profitable Venture · Bullshit · Safety Guarantee · The Guide · Night Sweep · TerraGroup Employee"
        ),
        "note": "",
    },
    {
        "id": "immunity",
        "name": "Immunity (Inmunidad)",
        "short_name": "Immunity",
        "category": "Física",
        "cache_key": "skill_immunity",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• -1% intensidad de efectos negativos de stims, comida y agua (+50% resistencia en Élite)\n"
            "• -1% potencia de efectos de veneno (+50% en Élite)\n"
            "• +0.6% duración de analgésicos por nivel (+30% en Élite)"
        ),
        "elite_perk": (
            "• +90% probabilidad de inmunidad a efectos negativos de estimulantes, comida y agua\n"
            "• +90% probabilidad de inmunidad contra venenos"
        ),
        "how_to_level": (
            "• Usar y sobrevivir hasta que terminen debuffs de stims/bebidas (~0.0045 pts/s; ej. Max Energy, 2A2-(b-TG), Obdolbos 2)\n"
            "• Quests: Get a Foothold · Profit Retention · Decontamination Service · Crisis"
        ),
        "note": "",
    },

    # --- COMBATE (15) ---
    {
        "id": "aim_drills",
        "name": "Aim Drills (Apuntado)",
        "short_name": "Aim Drills",
        "category": "Combate",
        "cache_key": "skill_aim_drills",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +1% velocidad al apuntar (ADS) por nivel (+50% en Élite)\n"
            "• -1% ruido al apuntar por nivel (-50% en Élite)"
        ),
        "elite_perk": (
            "• Cero temblor de manos durante los primeros 2 segundos tras apuntar sin importar la stamina\n"
            "• Reduce drásticamente el temblor con tremor o fractura durante los primeros 2 segundos al apuntar"
        ),
        "how_to_level": (
            "• 0.2 puntos por cada impacto acertado a enemigos apuntando con la mira (ADS)\n"
            "• Quests: Profitable Venture · Consolation Prize · Safety Guarantee"
        ),
        "note": "",
    },
    {
        "id": "assault_rifles",
        "name": "Assault Rifles (Fusiles de Asalto)",
        "short_name": "Assault Rifles",
        "category": "Combate",
        "cache_key": "skill_assault_rifles",
        "requirements": "Batya (Historia Nv. 10)",
        "effects": (
            "• +0.4% velocidad de recarga (+20% en Élite) y +0.8% velocidad de cambio de arma (+40% en Élite)\n"
            "• -0.3% retroceso (-15% en Élite) y +0.2% ergonomía (+10% en Élite) con fusiles/carabinas de asalto"
        ),
        "elite_perk": (
            "• Apuntado firme durante los primeros 3 segundos bajo cualquier condición de stamina\n"
            "• Duplica la ganancia de Maestría (Mastering) de estas armas"
        ),
        "how_to_level": (
            "• Impactar enemigos, recargar y ciclar/vaciar recámaras con rifles y carabinas de asalto\n"
            "• Quests: The Cleaner · Consolation Prize"
        ),
        "note": "",
    },
    {
        "id": "bolt_action_rifles",
        "name": "Bolt-action Rifles (Cerrojo)",
        "short_name": "Bolt-action",
        "category": "Combate",
        "cache_key": "skill_bolt_action_rifles",
        "requirements": "Make an Impression (Nv. 10) · Psycho Sniper",
        "effects": (
            "• +0.4% velocidad de recarga (+20% en Élite) y +0.8% velocidad de cambio de arma (+40% en Élite)\n"
            "• -0.3% retroceso (-15% en Élite) y +0.2% ergonomía (+10% en Élite) con rifles de cerrojo"
        ),
        "elite_perk": (
            "• Apuntado firme durante los primeros 3 segundos bajo cualquier condición de stamina\n"
            "• Duplica la ganancia de Maestría (Mastering) de rifles de cerrojo"
        ),
        "how_to_level": (
            "• Impactar enemigos, recargar (ej. Mosin/VPO-215) y ciclar cerrojo en raid\n"
            "• Quests: Shooter Born in Heaven · Psycho Sniper · Hunting Trip · Mentor (+3 niveles)"
        ),
        "note": "",
    },
    {
        "id": "dmrs",
        "name": "DMRs (Rifles Tirador)",
        "short_name": "DMRs",
        "category": "Combate",
        "cache_key": "skill_dmrs",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +0.4% velocidad de recarga (+20% en Élite) y +0.8% velocidad de cambio de arma (+40% en Élite)\n"
            "• -0.3% retroceso (-15% en Élite) y +0.2% ergonomía (+10% en Élite) con DMRs"
        ),
        "elite_perk": (
            "• Apuntado firme durante los primeros 3 segundos bajo cualquier condición de stamina\n"
            "• Duplica la ganancia de Maestría (Mastering) de DMRs"
        ),
        "how_to_level": (
            "• Impactar enemigos, recargar y ciclar recámara con rifles DMR (SR-25, RSASS, SVD, M1A)\n"
            "• Quests: The Cleaner · Consolation Prize"
        ),
        "note": "",
    },
    {
        "id": "light_machine_guns",
        "name": "Light Machine Guns (LMGs)",
        "short_name": "LMGs",
        "category": "Combate",
        "cache_key": "skill_light_machine_guns",
        "requirements": "Batya (Historia Nv. 5)",
        "effects": (
            "• +0.4% velocidad de recarga (+20% en Élite) y +0.8% velocidad de cambio de arma (+40% en Élite)\n"
            "• -0.3% retroceso (-15% en Élite) y +0.2% ergonomía (+10% en Élite) con ametralladoras ligeras"
        ),
        "elite_perk": (
            "• Apuntado firme durante los primeros 3 segundos bajo cualquier condición de stamina\n"
            "• Duplica la ganancia de Maestría (Mastering) de LMGs"
        ),
        "how_to_level": (
            "• Impactar enemigos, recargar y ciclar con LMGs (RPD, PKM, M60) o armas fijas montadas\n"
            "• Quests: Consolation Prize · Getting Some Air · Unique Experience"
        ),
        "note": "",
    },
    {
        "id": "heavy_machine_guns",
        "name": "Heavy Machine Guns (HMGs)",
        "short_name": "HMGs",
        "category": "Combate",
        "cache_key": "skill_heavy_machine_guns",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +0.4% velocidad de recarga (+20% Élite) y +0.8% cambio de arma (+40% Élite)\n"
            "• -0.3% retroceso (-15% Élite) y +0.2% ergonomía (+10% Élite)"
        ),
        "elite_perk": (
            "• Apuntado firme durante 3 segundos con cualquier stamina y doble Maestría"
        ),
        "how_to_level": (
            "• Actualmente solo sube completando quests: Consolation Prize · Getting Some Air · Unique Experience"
        ),
        "note": "⚠️ Nota Wiki: esta skill todavía no está implementada correctamente en combate.",
    },
    {
        "id": "pistols",
        "name": "Pistols (Pistolas)",
        "short_name": "Pistols",
        "category": "Combate",
        "cache_key": "skill_pistols",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +0.4% velocidad de recarga (+20% en Élite) y +0.8% velocidad de cambio de arma (+40% en Élite)\n"
            "• -0.3% retroceso (-15% en Élite) y +0.2% ergonomía (+10% en Élite) con pistolas"
        ),
        "elite_perk": (
            "• Apuntado firme durante los primeros 3 segundos bajo cualquier condición de stamina\n"
            "• Duplica la ganancia de Maestría (Mastering) de pistolas"
        ),
        "how_to_level": (
            "• Impactar enemigos, recargar y vaciar recámara con pistolas\n"
            "• Quests: Escort · Consolation Prize · Special Equipment · Trophies"
        ),
        "note": "",
    },
    {
        "id": "revolvers",
        "name": "Revolvers (Revólveres)",
        "short_name": "Revolvers",
        "category": "Combate",
        "cache_key": "skill_revolvers",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +0.4% velocidad de recarga (+20% en Élite) y +0.8% velocidad de cambio de arma (+40% en Élite)\n"
            "• -0.3% retroceso (-15% en Élite) y +0.2% ergonomía (+10% en Élite) con revólveres"
        ),
        "elite_perk": (
            "• Apuntado firme durante los primeros 3 segundos bajo cualquier condición de stamina\n"
            "• Duplica la ganancia de Maestría (Mastering) de revólveres"
        ),
        "how_to_level": (
            "• Impactar enemigos y recargar revólveres (incluye la escopeta revólver MTs-255-12)\n"
            "• Quests: Consolation Prize · Special Equipment · Trophies"
        ),
        "note": "",
    },
    {
        "id": "shotguns",
        "name": "Shotguns (Escopetas)",
        "short_name": "Shotguns",
        "category": "Combate",
        "cache_key": "skill_shotguns",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +0.4% velocidad de recarga (+20% en Élite) y +0.8% velocidad de cambio de arma (+40% en Élite)\n"
            "• -0.3% retroceso (-15% en Élite) y +0.2% ergonomía (+10% en Élite) con escopetas"
        ),
        "elite_perk": (
            "• Apuntado firme durante los primeros 3 segundos bajo cualquier condición de stamina\n"
            "• Duplica la ganancia de Maestría (Mastering) de escopetas"
        ),
        "how_to_level": (
            "• Impactar enemigos, recargar cartuchos y ciclar escopetas\n"
            "• Quests: Night Sweep · Consolation Prize · Silent Caliber"
        ),
        "note": "",
    },
    {
        "id": "submachine_guns",
        "name": "Submachine Guns (SMGs)",
        "short_name": "SMGs",
        "category": "Combate",
        "cache_key": "skill_submachine_guns",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +0.4% velocidad de recarga (+20% en Élite) y +0.8% velocidad de cambio de arma (+40% en Élite)\n"
            "• -0.3% retroceso (-15% en Élite) y +0.2% ergonomía (+10% en Élite) con subfusiles"
        ),
        "elite_perk": (
            "• Apuntado firme durante los primeros 3 segundos bajo cualquier condición de stamina\n"
            "• Duplica la ganancia de Maestría (Mastering) de subfusiles"
        ),
        "how_to_level": (
            "• Impactar enemigos, recargar y ciclar con subfusiles\n"
            "• Quests: Insomnia · Consolation Prize · Intimidator · Counteraction · TerraGroup Employee"
        ),
        "note": "",
    },
    {
        "id": "grenade_launchers",
        "name": "Grenade Launchers",
        "short_name": "Launchers",
        "category": "Combate",
        "cache_key": "skill_grenade_launchers",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +0.4% velocidad de recarga (+20% en Élite) y +0.8% velocidad de cambio de arma (+40% en Élite)\n"
            "• -0.3% retroceso (-15% en Élite) y +0.2% ergonomía (+10% en Élite) con lanzagranadas"
        ),
        "elite_perk": (
            "• Apuntado firme durante los primeros 3 segundos bajo cualquier condición de stamina\n"
            "• Duplica la ganancia de Maestría (Mastering)"
        ),
        "how_to_level": (
            "• Impactar enemigos con lanzagranadas acoplados (underbarrel) y lanzagranadas\n"
            "• Quests: Consolation Prize · The Art of Explosion · Escort"
        ),
        "note": "",
    },
    {
        "id": "underbarrel_launchers",
        "name": "Underbarrel Launchers",
        "short_name": "UGLs",
        "category": "Combate",
        "cache_key": "skill_underbarrel_launchers",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +0.4% velocidad de recarga (+20% Élite) y +0.8% cambio de arma (+40% Élite)\n"
            "• -0.3% retroceso (-15% Élite) y +0.2% ergonomía (+10% Élite)"
        ),
        "elite_perk": (
            "• Apuntado firme durante 3 segundos con cualquier stamina y doble Maestría"
        ),
        "how_to_level": (
            "• Actualmente solo sube completando quests: Consolation Prize · The Art of Explosion · Escort"
        ),
        "note": "⚠️ Nota Wiki: esta skill todavía no está implementada por separado en partida.",
    },
    {
        "id": "melee",
        "name": "Melee (Cuerpo a Cuerpo)",
        "short_name": "Melee",
        "category": "Combate",
        "cache_key": "skill_melee",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• Marcadores de posición heredados (+0.4% recarga / -0.3% retroceso / +0.2% ergo)"
        ),
        "elite_perk": (
            "• Efectos placeholder sin impacto real actualmente"
        ),
        "how_to_level": (
            "• Golpear enemigos con armas cuerpo a cuerpo\n"
            "• Quests: Escort · Consolation Prize"
        ),
        "note": "⚠️ Nota Wiki: sus efectos son placeholders y actualmente no tienen uso práctico.",
    },
    {
        "id": "throwables",
        "name": "Throwables (Granadas)",
        "short_name": "Throwables",
        "category": "Combate",
        "cache_key": "skill_throwables",
        "requirements": "Sin requisito obligatorio (clave para Grenadier)",
        "effects": (
            "• +0.5% fuerza/distancia de lanzamiento por nivel (+25% en Élite)\n"
            "• -1% consumo de energía al lanzar (-50% en Élite)\n"
            "• Aumenta la velocidad de lanzamiento"
        ),
        "elite_perk": (
            "• Lanzar granadas deja de consumir energía/stamina\n"
            "• La fatiga deja de afectar la precisión de tus lanzamientos"
        ),
        "how_to_level": (
            "• Lanzar granadas (F-1, RGD-5, flashes o humo) en cada raid\n"
            "• Quests: Consolation Prize · The Huntsman Path - Control"
        ),
        "note": "",
    },
    {
        "id": "troubleshooting",
        "name": "Troubleshooting (Encasquillamientos)",
        "short_name": "Troubleshooting",
        "category": "Combate",
        "cache_key": "skill_troubleshooting",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +0.5% velocidad para solucionar fallas/encasquillamientos de arma por nivel (+25% en Élite)"
        ),
        "elite_perk": (
            "• Identifica el tipo de falla al instante SIN tener que inspeccionar el arma\n"
            "• -50% chance de repetir falla por cargador, durabilidad del arma o cartucho tras reparar una falla de ese mismo origen"
        ),
        "how_to_level": (
            "• Reparar encasquillamientos/fallas de arma en raid\n"
            "• Quests: Psycho Sniper · Profitable Venture · A Life Lesson · Safety Guarantee · Never Too Late To Learn · Goals and Means · Consolation Prize"
        ),
        "note": "",
    },

    # --- PRÁCTICA (9) ---
    {
        "id": "covert_movement",
        "name": "Covert Movement (Sigilo)",
        "short_name": "Covert Mov.",
        "category": "Práctica",
        "cache_key": "skill_covert_movement",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• -1.2% ruido de pasos en superficies comunes (-60% en Élite)\n"
            "• -0.6% ruido de pasos en superficies ruidosas/raras (-30% en Élite)\n"
            "• +1% velocidad caminando en sigilo (+50% en Élite)\n"
            "• -1.2% ruido de armas y equipo al moverte (-60% en Élite)"
        ),
        "elite_perk": (
            "• El movimiento en sigilo se vuelve igual de silencioso en TODAS las superficies (-60% ruido total)"
        ),
        "how_to_level": (
            "• Caminar por debajo del 25% de velocidad (el ícono del parlante en el HUD debe no mostrar barras); suma al detenerte\n"
            "• Quests: Profitable Venture · Safety Guarantee · Connections Up North · The Huntsman Path - Sadist"
        ),
        "note": "",
    },
    {
        "id": "crafting",
        "name": "Crafting (Fabricación)",
        "short_name": "Crafting",
        "category": "Práctica",
        "cache_key": "skill_crafting",
        "requirements": "Clave para velocidad del Hideout",
        "effects": (
            "• -0.75% tiempo de crafteo de ítems por nivel (-37.5% en Élite)\n"
            "• -0.75% tiempo en producciones cíclicas (excepto Bitcoin Farm) (-37.5% en Élite)"
        ),
        "elite_perk": (
            "• Permite fabricar hasta 2 recetas diferentes a la vez dentro de una misma estación del Hideout (incluye Scav Case)"
        ),
        "how_to_level": (
            "• Alternar entre 2 recetas distintas en el mismo módulo (+5 pts al terminar; repetir siempre la misma receta NO da puntos) · 1.5 pts cada 8h\n"
            "• Quests: Get a Foothold · Never Too Late To Learn · Profit Retention · A Life Lesson"
        ),
        "note": "",
    },
    {
        "id": "hideout_management",
        "name": "Hideout Management",
        "short_name": "Hideout Mgmt",
        "category": "Práctica",
        "cache_key": "skill_hideout_management",
        "requirements": "Library (Biblioteca requiere Nv. 5)",
        "effects": (
            "• +1% a todos los bonus porcentuales de zonas del Hideout (+50% en Élite)\n"
            "• -0.5% consumo de combustible, filtros de aire y filtros de agua (-25% en Élite)"
        ),
        "elite_perk": (
            "• +2 ranuras extra para bidones de combustible en el Generador\n"
            "• +2 ranuras para filtros de agua y +2 para filtros de aire\n"
            "• +2 monedas al límite máximo de almacenamiento en la Bitcoin Farm (5 total)"
        ),
        "how_to_level": (
            "• Mejorar módulos, consumir combustible/filtros, craftear y usar la Scav Case\n"
            "• Quests: The Choice · Never Too Late To Learn · Profit Retention · A Life Lesson · Get a Foothold"
        ),
        "note": "",
    },
    {
        "id": "heavy_vests",
        "name": "Heavy Vests (Blindaje Pesado)",
        "short_name": "Heavy Vests",
        "category": "Práctica",
        "cache_key": "skill_heavy_vests",
        "requirements": "Sin requisito obligatorio (Acero, Cerámica, Combinado, Titanio)",
        "effects": (
            "• -0.5% penalización de velocidad al llevar blindaje pesado (-25% en Élite)\n"
            "• -0.4% daño contundente (blunt) en zonas protegidas (-20% en Élite)\n"
            "• -1% desgaste al usar kits de reparación (-50% en Élite)\n"
            "• Desde Nv. 3: chance de añadir mejora naranja (-3% a -11% daño recibido)"
        ),
        "elite_perk": (
            "• Probabilidad de desviar/rebotar balas en blindaje pesado\n"
            "• 50% de probabilidad de NO consumir durabilidad máxima al reparar\n"
            "• Desbloquea mejora rara al reparar (-20% daño recibido)"
        ),
        "how_to_level": (
            "• Reparar blindajes pesados (Acero/Cerámica/Titanio/Combinado) con Body armor repair kit (0.4 pts cada 10 pts) y recibir daño en placas\n"
            "• Quests: Safety Guarantee · Profitable Venture"
        ),
        "note": "",
    },
    {
        "id": "light_vests",
        "name": "Light Vests (Blindaje Ligero)",
        "short_name": "Light Vests",
        "category": "Práctica",
        "cache_key": "skill_light_vests",
        "requirements": "Sin requisito obligatorio (Aramida, Aluminio, UHMWPE)",
        "effects": (
            "• -0.6% penalización de velocidad al llevar blindaje ligero (-30% en Élite)\n"
            "• -0.6% daño cuerpo a cuerpo recibido en zonas cubiertas (-30% en Élite)\n"
            "• -0.8% desgaste al usar kits de reparación (-40% en Élite)\n"
            "• Desde Nv. 3: chance de añadir mejora naranja (-3% a -11% daño recibido)"
        ),
        "elite_perk": (
            "• Las partes del cuerpo cubiertas por blindaje ligero se vuelven INMUNES a hemorragias\n"
            "• 50% de probabilidad de NO consumir durabilidad máxima al reparar\n"
            "• Desbloquea mejora rara al reparar (-20% daño recibido)"
        ),
        "how_to_level": (
            "• Reparar blindajes ligeros (Aramida/Aluminio/UHMWPE) con Body armor repair kit (0.4 pts cada 10 pts) y absorber daño\n"
            "• Quests: Safety Guarantee · Profitable Venture"
        ),
        "note": "",
    },
    {
        "id": "mag_drills",
        "name": "Mag Drills (Cargadores)",
        "short_name": "Mag Drills",
        "category": "Práctica",
        "cache_key": "skill_mag_drills",
        "requirements": "Clave para recarga táctica de cargadores",
        "effects": (
            "• +0.6% velocidad de carga de balas (+30% en Élite) y -0.6% tiempo de descarga (-30%)\n"
            "• -0.8% tiempo de chequeo de cargador (-40% en Élite)\n"
            "• Nv. 10: estimación numérica (~15) · Nv. 20: cantidad exacta de balas restantes"
        ),
        "elite_perk": (
            "• Los cargadores se revisan INSTANTÁNEAMENTE al moverlos a tu inventario\n"
            "• La carga de balas acelera progresivamente con cada bala introducida"
        ),
        "how_to_level": (
            "• Cargar, descargar y revisar cargadores en raid (incluye tubos de escopetas)\n"
            "• Quests: A Life Lesson · Never Too Late To Learn · Best Job in the World · Escort · Intimidator"
        ),
        "note": "",
    },
    {
        "id": "search",
        "name": "Search (Búsqueda)",
        "short_name": "Search",
        "category": "Práctica",
        "cache_key": "skill_search",
        "requirements": "Scavenger (Nv. 9)",
        "effects": (
            "• +1% velocidad de búsqueda (+50% en Élite)"
        ),
        "elite_perk": (
            "• Permite inspeccionar 2 contenedores o compartimentos (ej. mochila + rig) SIMULTÁNEAMENTE"
        ),
        "how_to_level": (
            "• Revisar contenedores de loot/cuerpos y recoger loot suelto\n"
            "• Quests: Bullshit · Get a Foothold · Profit Retention · Night Sweep"
        ),
        "note": "Nota Wiki: la velocidad de búsqueda actual depende principalmente de Attention, pero el perk Élite de Search (doble búsqueda) sí funciona.",
    },
    {
        "id": "surgery",
        "name": "Surgery (Cirugía)",
        "short_name": "Surgery",
        "category": "Práctica",
        "cache_key": "skill_surgery",
        "requirements": "Clave para supervivencia en Raid",
        "effects": (
            "• +0.4% velocidad de cirugía por nivel (+20% en Élite)\n"
            "• -1% penalización de HP máximo perdido tras operar (-50% en Élite)"
        ),
        "elite_perk": (
            "• +20% velocidad de cirugía extra (+40% total)\n"
            "• -100% penalización de HP: las extremidades negras quedan restauradas con el 100% de su HP máximo"
        ),
        "how_to_level": (
            "• 1.1 puntos por cada extremidad en negro operada en raid con CMS o Surv12\n"
            "• Quests: Get a Foothold · Profit Retention · Beneath The Streets · Crisis"
        ),
        "note": "",
    },
    {
        "id": "weapon_maintenance",
        "name": "Weapon Maintenance",
        "short_name": "Weapon Maint.",
        "category": "Práctica",
        "cache_key": "skill_weapon_maintenance",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• -0.5% desgaste del arma al disparar (-25% en Élite)\n"
            "• -1% probabilidad de pérdida de durabilidad máxima al reparar (-50% en Élite)\n"
            "• Desde Nv. 3: chance de mejora naranja en dispersión (-3% a -11%) o fallas (-5% a -16%)"
        ),
        "elite_perk": (
            "• -50% probabilidad de desgaste permanente al usar Weapon Repair Kits\n"
            "• Desbloquea mejoras raras al reparar: -20% dispersión y -30% chance de encasquillamiento"
        ),
        "how_to_level": (
            "• Reparar armas en el alijo con Weapon repair kit (0.4 pts cada ~5 pts de durabilidad reparada)\n"
            "• Quests: Safety Guarantee · Consolation Prize · Profitable Venture · Goals and Means · Calibration"
        ),
        "note": "",
    },

    # --- MENTAL (4) ---
    {
        "id": "attention",
        "name": "Attention (Atención)",
        "short_name": "Attention",
        "category": "Mental",
        "cache_key": "skill_attention",
        "requirements": "Intelligence Center Nv. 2 (Nv. 3) · Water Collector Nv. 2 (Nv. 3)",
        "effects": (
            "• +2% velocidad al lootear contenedores por nivel (+100% en Élite)\n"
            "• +2% velocidad de examinación de objetos por nivel (+100% en Élite)"
        ),
        "elite_perk": (
            "• Duplica la experiencia (EXP) obtenida al lootear\n"
            "• +50% probabilidad de descubrir/revelar un ítem al instante al abrir un contenedor"
        ),
        "how_to_level": (
            "• Recoger loot suelto y revelar objetos en contenedores (0.08 pts por ítem)\n"
            "• Quests: Profitable Venture · Safety Guarantee · Get a Foothold · Profit Retention · Silent Caliber"
        ),
        "note": "",
    },
    {
        "id": "charisma",
        "name": "Charisma (Carisma)",
        "short_name": "Charisma",
        "category": "Mental",
        "cache_key": "skill_charisma",
        "requirements": "Progreso compartido entre tu PMC y tu Scav",
        "effects": (
            "• -0.1% costo de reemplazo de misiones diarias/semanales (-5% en Élite)\n"
            "• -0.1% precios de curación post-raid, seguros y extracciones pagas (-5% en Élite)"
        ),
        "elite_perk": (
            "• 10% de descuento en envíos de la Scav Case\n"
            "• -50% reducción en penalizaciones de Scav Karma con Fence (aplica también con +6.0)\n"
            "• Añade 1 misión diaria operacional adicional"
        ),
        "how_to_level": (
            "• Recibe 10% de tu EXP en Intellect y 20% de Attention/Perception\n"
            "• Usar Scav Case (0.4 pts), asegurar equipo (0.4 pts/200k ₽) y reparar con Traders (0.4 pts/10k ₽)\n"
            "• Quests: Special Order · A Life Lesson · Antique Enthusiast · Regulated Materials · Never Too Late To Learn"
        ),
        "note": "",
    },
    {
        "id": "intellect",
        "name": "Intellect (Intelecto)",
        "short_name": "Intellect",
        "category": "Mental",
        "cache_key": "skill_intellect",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +2% velocidad al examinar objetos por nivel (+100% en Élite)\n"
            "• +2% efectividad al reparar armas (+100% en Élite)\n"
            "• -0.5% consumo de usos de kits de reparación por nivel (-25% en Élite)"
        ),
        "elite_perk": (
            "• Contador de munición, intuir contenido sin buscar y sin necesidad de manual (actualmente inactivos en el juego)"
        ),
        "how_to_level": (
            "• Craftear ítems en el Hideout y reparar armas/blindajes con Repair Kits (~0.4 pts cada 10 durabilidad)\n"
            "• Quests: Shooter Born in Heaven · A Life Lesson · Setting Priorities · Calibration · Never Too Late To Learn"
        ),
        "note": "⚠️ Nota Wiki: los efectos Élite de Intellect actualmente no funcionan en el juego.",
    },
    {
        "id": "perception",
        "name": "Perception (Percepción)",
        "short_name": "Perception",
        "category": "Mental",
        "cache_key": "skill_perception",
        "requirements": "Sin requisito obligatorio",
        "effects": (
            "• +2% radio de detección visual de loot (punto blanco en pantalla) por nivel (+100% en Élite)"
        ),
        "elite_perk": (
            "• Notificación / detección mejorada de proximidad de loot"
        ),
        "how_to_level": (
            "• Recoger todo tipo de loot suelto y dentro de contenedores\n"
            "• Quests: Profitable Venture · Safety Guarantee · Get a Foothold · Profit Retention"
        ),
        "note": "",
    },
]


SKILL_LEVELING_MECHANICS: Dict[str, Any] = {'max_level': '51 (Nivel Élite — hasta 60 temporalmente con estimulantes/comida)',
 'diminishing_returns': [('Antes del 1er punto en raid', '129%', '#10B981'),
                         ('Después de 1 punto', '100%', '#FBBF24'),
                         ('Después de 4 puntos', '45%', '#F97316'),
                         ('Después de 5 puntos', '20%', '#EF4444'),
                         ('Después de 6 puntos', '9%', '#EF4444'),
                         ('Después de 7+ puntos', '1% - 4%', '#DC2626')],
 'reset_note': 'Si dejás de ganar puntos de un skill durante 200 segundos, su multiplicador de velocidad se reinicia a '
               '100%.',
 'hideout_boosters': ['Air Filtering Unit (+FP-100): +40% velocidad de leveo en skills Físicas.',
                      'Library (Biblioteca): +30% velocidad de leveo en skills Prácticas.',
                      'Shooting Range Nv. 3: +10% velocidad de leveo en skills de Combate.',
                      'Hall of Fame: bonus a skills de Combate según nivel/cantidad de Dogtags enemigos.',
                      'Defective Wall Nv. 2-5: aplica hasta -12% penalización física hasta que lo repares completo a '
                      'Nv. 6.']}


SCAV_KARMA_BRACKETS: List[Dict[str, Any]] = [{'karma': '-5.0 o menor',
  'btr': 'BLOQUEADO (hostil)',
  'transit_grid': '3x4',
  'effects': 'Los Scavs IA te atacan apenas te ven, cooldown de Scav altísimo, peor loot y sin acceso al BTR.'},
 {'karma': '-0.99 a +0.99',
  'btr': '5x2 slots',
  'transit_grid': '3x4',
  'effects': 'Estado neutral estándar. Tarifas normales de extracción en vehículo/BTR.'},
 {'karma': '+1.0 a +1.99',
  'btr': '6x2 slots',
  'transit_grid': '4x4',
  'effects': 'Cooldown de Scav reducido, mejor equipo inicial y descuentos en extracciones pagas.'},
 {'karma': '+2.0 a +3.99',
  'btr': '5x3 / 6x3 slots',
  'transit_grid': '4x4 / 4x5',
  'effects': 'Mayor probabilidad de aparecer con tarjetas Labs, llaves buenas o mochilas grandes en tu Scav.'},
 {'karma': '+4.0 a +5.99',
  'btr': '5x4 / 6x4 slots',
  'transit_grid': '4x5 / 5x5',
  'effects': 'Cooldown mínimo, gran chance de stims/llaves al spawnear y extractos vehiculares muy baratos.'},
 {'karma': '+6.0 o superior (ÉLITE)',
  'btr': '7x4 slots',
  'transit_grid': '5x5',
  'effects': 'Desbloquea la pestaña secreta Fence LL2 (loot sin asegurar de PMCs), los Bosses son amistosos con tu '
             'Scav y cooldown ultra corto.'}]


SCAV_KARMA_ACTIONS: List[Dict[str, Any]] = [{'action': 'Extracción Co-Op (PMC + Scav juntos)',
  'change': '+0.25 (1ª vez)',
  'notes': 'Decrece por uso repetido en el mismo mapa (0.25 / total usos).'},
 {'action': 'Extracción en Vehículo (Car Extract) como PMC',
  'change': '+0.20 (1ª vez)',
  'notes': 'Cada mapa tiene su contador propio (0.20 / total usos).'},
 {'action': 'Ayudar a un Scav Boss',
  'change': '+0.05',
  'notes': 'Matar a un PMC que atacó al Boss o defendiendo su zona.'},
 {'action': 'Matar a un Scav Traidor (como Scav)',
  'change': '+0.03',
  'notes': 'Traidor = Scav que dañó a otro Scav/Boss antes.'},
 {'action': 'Matar a un PMC que ya mató Scavs',
  'change': '+0.02 a +0.03',
  'notes': '+0.02 si mató 1 Scav, +0.03 si mató 2+.'},
 {'action': 'Completar misión diaria de Fence',
  'change': '+0.01 a +0.05',
  'notes': 'Ver recompensas en la pestaña diaria de Fence.'},
 {'action': 'Extraer o usar Transit como Scav', 'change': '+0.01', 'notes': 'Suma en cada extracción limpia.'},
 {'action': 'Matar Raiders, Rogues, Cultistas o Black Division',
  'change': '0.00 (Sin cambio)',
  'notes': 'No da ni quita Karma (aunque Raiders/Rogues puedan atacarte).'},
 {'action': 'Matar un Scav IA (como Scav)',
  'change': '-0.03 a -0.05',
  'notes': 'Te marca como Traidor para todos los Scavs del mapa.'},
 {'action': 'Matar un Guardia de Boss (como Scav)', 'change': '-0.05', 'notes': 'Penalización directa.'},
 {'action': 'Matar un Jugador Scav inocente',
  'change': '-0.10',
  'notes': 'Penalización fuerte si no te disparó/dañó primero.'},
 {'action': 'Matar un Scav Boss (como Scav)',
  'change': '-0.20',
  'notes': 'Si estás sobre +6.0 puede bajarte drásticamente cerca de 5.9.'}]


BTR_SERVICE_DATA: Dict[str, Any] = {'maps': ['Woods', 'Streets of Tarkov', 'Lighthouse'],
 'unlock_note': "Las misiones del BTR Driver se desbloquean al aceptar 'A Helping Hand' de Mechanic. Permanece 2 min "
                'por parada y toca bocina 2 veces 10s antes de salir.',
 'services': [{'service': 'Servicio Taxi (Viaje entre paradas)',
               'usec': '11,250 ₽',
               'bear': '7,500 ₽',
               'scav': '6,000 ₽'},
              {'service': 'Fuego de Cobertura (Ametralladora coaxial)',
               'usec': '75,000 ₽',
               'bear': '50,000 ₽',
               'scav': '40,000 ₽'},
              {'service': 'Envío de Ítems FiR al Alijo (por slot)',
               'usec': '750 + 7.5% valor',
               'bear': '500 + 5% valor',
               'scav': 'No disponible'}],
 'hostile_rule': 'El BTR es neutral hasta que alguien le dispara o compra Fuego de Cobertura (se vuelve hostil '
                 'temporalmente). Con Scav Karma -5 o menor rechaza tu acceso.'}


TRANSITS_CATALOG: List[Dict[str, Any]] = [{'from_map': 'Reserve',
  'to_map': 'Customs',
  'name': 'Transit to Customs',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'North of the black bishop barracks, where the train track ends'},
 {'from_map': 'Reserve',
  'to_map': 'Lighthouse',
  'name': 'Transit to Lighthouse',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'At the map border southwest of the train yard'},
 {'from_map': 'Reserve',
  'to_map': 'Woods',
  'name': 'Transit to Woods',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'At the map border northwest of the train yard'},
 {'from_map': 'Streets of Tarkov',
  'to_map': 'Ground Zero',
  'name': 'Transit to Ground Zero',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Next to the ministry of the interior academy'},
 {'from_map': 'Streets of Tarkov',
  'to_map': 'Interchange',
  'name': 'Transit to Interchange',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Southwest of the Concordia apartment complex'},
 {'from_map': 'Streets of Tarkov',
  'to_map': 'The Lab',
  'name': 'Transit to The Lab',
  'faction': 'PMC',
  'notes': 'Requiere: TerraGroup Labs access keycard per player | Underground entrance in front of the Klimova 16A '
           'building with the Cosmonaut painting'},
 {'from_map': 'Interchange',
  'to_map': 'Customs',
  'name': 'Transit to Customs',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'At the southern end of the highway'},
 {'from_map': 'Interchange',
  'to_map': 'Streets of Tarkov',
  'name': 'Transit to Streets of Tarkov',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'At the northern end of the highway'},
 {'from_map': 'Customs',
  'to_map': 'Factory',
  'name': 'Transit to Factory',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Next to the Old Gas Station extraction'},
 {'from_map': 'Customs',
  'to_map': 'Interchange',
  'name': 'Transit to Interchange',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Next to the Trailer Park extraction, inside the bus'},
 {'from_map': 'Customs',
  'to_map': 'Reserve',
  'name': 'Transit to Reserve',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Disponible tras 1 minuto de raid (timer 20s).'},
 {'from_map': 'Customs',
  'to_map': 'Shoreline',
  'name': 'Transit to Shoreline',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Disponible tras 1 minuto de raid (timer 20s).'},
 {'from_map': 'Factory',
  'to_map': 'Customs',
  'name': 'Transit to Customs',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Med Tent Gate extraction side outdoor area'},
 {'from_map': 'Factory',
  'to_map': 'The Lab',
  'name': 'Transit to The Lab',
  'faction': 'PMC',
  'notes': 'Requiere: TerraGroup Labs access keycard per player | In the sewer tunnel connected to the flooded area'},
 {'from_map': 'Factory',
  'to_map': 'Woods',
  'name': 'Transit to Woods',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'At the Courtyard Gate extraction'},
 {'from_map': 'Woods',
  'to_map': 'Customs',
  'name': 'Transit to Customs',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Disponible tras 1 minuto de raid (timer 20s).'},
 {'from_map': 'Woods',
  'to_map': 'Factory',
  'name': 'Transit to Factory',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Disponible tras 1 minuto de raid (timer 20s).'},
 {'from_map': 'Woods',
  'to_map': 'Lighthouse',
  'name': 'Transit to Lighthouse',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Disponible tras 1 minuto de raid (timer 20s).'},
 {'from_map': 'Woods',
  'to_map': 'Reserve',
  'name': 'Transit to Reserve',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Disponible tras 1 minuto de raid (timer 20s).'},
 {'from_map': 'Lighthouse',
  'to_map': 'Icebreaker',
  'name': 'Transit to Icebreaker',
  'faction': 'PMC',
  'notes': 'Requiere: Sudak-Tudak marine repair kit per player | At the pier next to the seaside houses · Has to be '
           'unlocked through the story chapter Boreas'},
 {'from_map': 'Lighthouse',
  'to_map': 'Reserve',
  'name': 'Transit to Reserve',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'On the road leading to the Road to Military Base V-Ex extraction'},
 {'from_map': 'Lighthouse',
  'to_map': 'Shoreline',
  'name': 'Transit to Shoreline',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Next to the Path to Shoreline extraction'},
 {'from_map': 'Lighthouse',
  'to_map': 'Woods',
  'name': 'Transit to Woods',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'On the road leading to the Road to Northern Checkpoint extraction'},
 {'from_map': 'Shoreline',
  'to_map': 'Icebreaker',
  'name': 'Transit to Icebreaker',
  'faction': 'PMC',
  'notes': 'Requiere: Sudak-Tudak marine repair kit per player | At the pier · Has to be unlocked through the story '
           'chapter Boreas'},
 {'from_map': 'Shoreline',
  'to_map': 'Labyrinth',
  'name': 'Transit to Labyrinth',
  'faction': 'PMC',
  'notes': 'Requiere: Labrys access keycard per player | In the basement of the health resort west wing · Knossos LLC '
           'facility key required'},
 {'from_map': 'Shoreline',
  'to_map': 'Lighthouse',
  'name': 'Transit to Lighthouse',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'In front of the Path to Lighthouse extraction'},
 {'from_map': 'Shoreline',
  'to_map': 'Terminal',
  'name': 'Transit to Terminal',
  'faction': 'PMC',
  'notes': 'in the time period of 21:00-6:00 | Requires presenting the access item at the port garrison intercom to '
           'not get shot'},
 {'from_map': 'The Lab',
  'to_map': 'Streets of Tarkov',
  'name': 'Transit to Streets of Tarkov',
  'faction': 'PMC',
  'notes': 'Near the orange dome, next to the office with the billiard table'},
 {'from_map': 'Ground Zero',
  'to_map': 'Streets of Tarkov',
  'name': 'Transit to Streets of Tarkov',
  'faction': 'Todos (PMC/Scav)',
  'notes': 'Next to the Mira Ave extraction'}]


TRANSIT_EXP_MULTIPLIERS: List[tuple] = [('1º mapa', '1.16×'),
 ('2º mapa', '1.34×'),
 ('3º mapa', '1.56×'),
 ('4º mapa', '1.80×'),
 ('5º mapa', '2.09×'),
 ('6º mapa', '2.42×'),
 ('8º mapa', '3.26×'),
 ('10º mapa', '4.37×'),
 ('16º mapa', '10.60×')]


SKILL_CATEGORIES = ["Todas", "Física", "Combate", "Práctica", "Mental"]


def filter_skills(category: str = "Todas", query: str = "") -> List[Dict[str, Any]]:
    """Filtra las skills del PMC por categoría o texto (nombre, quest/Hideout requerida)."""
    q = (query or "").strip().lower()
    res: List[Dict[str, Any]] = []
    for sk in PMC_SKILLS_CATALOG:
        if category and category != "Todas" and sk.get("category") != category:
            continue
        if q:
            hay = " ".join([
                sk.get("name", ""),
                sk.get("short_name", ""),
                sk.get("requirements", ""),
                sk.get("effects", ""),
                sk.get("elite_perk", ""),
                sk.get("how_to_level", ""),
            ]).lower()
            if q not in hay:
                continue
        res.append(sk)
    return res


def filter_transits(from_map: str = "Todos", query: str = "") -> List[Dict[str, Any]]:
    """Filtra las conexiones de Transit por mapa de origen o destino."""
    q = (query or "").strip().lower()
    res: List[Dict[str, Any]] = []
    for tr in TRANSITS_CATALOG:
        if from_map and from_map != "Todos" and tr.get("from_map") != from_map:
            continue
        if q:
            hay = " ".join([tr.get("from_map", ""), tr.get("to_map", ""), tr.get("notes", "")]).lower()
            if q not in hay:
                continue
        res.append(tr)
    return res
