"""
TarkovScope - Sistemas de PMC, Skills, Scav Karma (Fence), BTR Driver & Red de Transits
Datos verificados contra la Wiki oficial de Escape from Tarkov en español táctico.
Módulo de lógica pura (sin dependencias de UI).
"""
from typing import Any, Dict, List


PMC_SKILLS_CATALOG: List[Dict[str, Any]] = [{'id': 'strength',
  'name': 'Strength (Fuerza)',
  'category': 'Física',
  'requirements': 'Batya (Historia Nv. 15) · Vents Nv. 3 (Nv. 2)',
  'effects': '+0.6% límite de peso por nivel (+30% Élite), +0.4% velocidad de movimiento/sprint, +0.4% salto y '
             'distancia de granadas.',
  'elite_perk': 'Las armas equipadas en bandolera y espalda dejan de sumar peso al personaje; +50% chance de golpe '
                'crítico cuerpo a cuerpo.',
  'how_to_level': 'Caminar o esprintar con sobrepeso (amarillo/naranja, >55-60% peso máximo), lanzar granadas, usar el '
                  'Gimnasio del Hideout y completar quests que otorguen puntos.'},
 {'id': 'endurance',
  'name': 'Endurance (Resistencia)',
  'category': 'Física',
  'requirements': 'Heating Nv. 2 (Nv. 1) · Security Nv. 2 (Nv. 2)',
  'effects': '+1% stamina por nivel (+50% Élite), -0.6% costo de salto, +2% contención de respiración al apuntar.',
  'elite_perk': '+20% stamina adicional (+70% total), mayor resistencia en brazos al apuntar y respiración '
                'independiente de energía.',
  'how_to_level': 'Correr y caminar SIN sobrepeso (<33.77% de tu peso máximo límite) al inicio del raid antes de '
                  'lootear pesado, más sesiones en el Gimnasio.'},
 {'id': 'vitality',
  'name': 'Vitality (Vitalidad)',
  'category': 'Física',
  'requirements': 'Medstation Nv. 3 (Nv. 3)',
  'effects': '-1.2% probabilidad de sufrir hemorragia por nivel y reduce chance de muerte instantánea por extremidad '
             'negra.',
  'elite_perk': 'Todas las hemorragias se detienen solas (leves en 20s, graves en 30s) y regeneración de vida en '
                'combate.',
  'how_to_level': 'Recibir daño (0.01 pts cada 5 HP recibidos) y sufrir pérdida de sangre (+0.3 pts). Tip: curarse '
                  "daño por alambre de púas/fuego controladamente o completar 'Get a Foothold' / 'Decontamination "
                  "Service'."},
 {'id': 'health',
  'name': 'Health (Salud)',
  'category': 'Física',
  'requirements': 'Health Care Privacy Pt. 4 (Nv. 4) · Medstation Nv. 2 (Nv. 2)',
  'effects': 'Acelera recuperación fuera de raid, reduce probabilidad de fracturas (-60% Élite) y reduce consumo de '
             'energía/hidratación.',
  'elite_perk': 'Reduce severamente riesgo de fracturas y desgaste metabólico durante raids largos.',
  'how_to_level': 'Sube automáticamente cada vez que subís Strength, Endurance o Vitality (gana puntos proporcionales '
                  'al entrenamiento físico).'},
 {'id': 'metabolism',
  'name': 'Metabolism (Metabolismo)',
  'category': 'Física',
  'requirements': 'Nutrition Unit Nv. 3 (Nv. 3)',
  'effects': '+1% duración y eficacia de comida/bebida por nivel, reduce caída de skills físicos por hambre/sed.',
  'elite_perk': 'Inmunidad total a perder salud o sufrir desmayos por 0 Energía o 0 Hidratación.',
  'how_to_level': 'Comer y beber dentro del raid cada vez que gastes energía o hidratación (Golden Star / Mayo + '
                  'botella de agua en el seguro acelera muchísimo).'},
 {'id': 'stress_resistance',
  'name': 'Stress Resistance (Resistencia al Estrés)',
  'category': 'Física',
  'requirements': 'Batya (Historia Nv. 10)',
  'effects': 'Reduce el temblor de manos al recibir daño, disminuye el efecto de visión túnel / tremor y baja la '
             'probabilidad de shock por dolor.',
  'elite_perk': 'Modo Berserk al recibir daño crítico: resistencia temporal a supresión y dolor.',
  'how_to_level': 'Correr con extremidades fracturadas o negras sin usar analgésicos durante unos segundos, o pelear '
                  'herido.'},
 {'id': 'immunity',
  'name': 'Immunity (Inmunidad)',
  'category': 'Física',
  'requirements': 'Sin requisito obligatorio de Hideout',
  'effects': 'Reduce la duración y severidad de efectos negativos de venenos, radiación, toxinas y debuffs de '
             'estimulantes.',
  'elite_perk': 'Reducción del 90% de efectos secundarios negativos de stims y veneno.',
  'how_to_level': 'Usar comida/bebida o stims que dejan efectos temporales y esperar a que pasen sus debuffs (ej. '
                  'Obdolbos, Mayo, SJ6).'},
 {'id': 'bolt_action_rifles',
  'name': 'Bolt-action Rifles (Cerrojo / Sniper)',
  'category': 'Combate',
  'requirements': 'Make an Impression (Nv. 10) · Wet Job Pt. 6 / Psycho Sniper',
  'effects': '+0.5% velocidad de recarga y +0.8% velocidad de apuntado con rifles de cerrojo por nivel.',
  'elite_perk': 'Recarga ultrarrápida y mayor control en disparos de larga distancia.',
  'how_to_level': 'Recargar repetidamente rifles de cerrojo sin cargador (Mosin / VPO-215 / DVL) en raid, impactar '
                  "disparos a larga distancia y usar la quest 'Mentor' de Peacekeeper (+3 niveles) en nivel 7+."},
 {'id': 'throwables',
  'name': 'Throwables (Granadas)',
  'category': 'Combate',
  'requirements': 'Sin requisito fijo (muy útil para Grenadier)',
  'effects': 'Aumenta distancia máxima y velocidad de lanzamiento de granadas hasta +25%.',
  'elite_perk': 'Alcance máximo y menor consumo de stamina de brazo al preparar lanzamientos.',
  'how_to_level': 'Lanzar granadas (F-1, RGD-5, flashes Zarya o humo M18 económicas) en cada raid; las primeras 4 por '
                  'raid dan rendimiento óptimo (129%/100%).'},
 {'id': 'search',
  'name': 'Search (Búsqueda)',
  'category': 'Práctica',
  'requirements': 'Scavenger (Nv. 9)',
  'effects': 'Aumenta la velocidad al inspeccionar mochilas, cajas, cajones y bolsillos hasta +50%.',
  'elite_perk': 'Permite examinar 2 contenedores o ranuras simultáneamente (doble loot speed).',
  'how_to_level': 'Abrir y revisar la mayor cantidad posible de archivadores, chaquetas, mochilas y cuerpos (Scavs '
                  'aunque no tengan buen loot).'},
 {'id': 'covert_movement',
  'name': 'Covert Movement (Sigilo)',
  'category': 'Práctica',
  'requirements': 'Sin requisito obligatorio',
  'effects': 'Reduce el ruido generado al caminar lento y apuntar agachado sobre madera, vidrio y metal.',
  'elite_perk': 'Movimiento lento completamente silencioso en la mayoría de superficies estándar.',
  'how_to_level': 'Caminar a velocidad mínima (rueda del mouse abajo) sin sobrepeso durante tramos tácticos.'},
 {'id': 'crafting',
  'name': 'Crafting (Fabricación)',
  'category': 'Práctica',
  'requirements': 'Escala producción del Hideout',
  'effects': 'Reduce el tiempo de crafteo en el Hideout (hasta -37.5% al máximo).',
  'elite_perk': 'Permite producir 2 recetas simultáneas por estación del Hideout.',
  'how_to_level': 'Alternar crafteos distintos en Workbench, Medstation, Lavatory y Nutrition Unit (repetir '
                  'exactamente la misma receta seguida da mucha menos XP).'},
 {'id': 'hideout_management',
  'name': 'Hideout Management',
  'category': 'Práctica',
  'requirements': 'Library (Nv. 5)',
  'effects': 'Aumenta bonificaciones de cada módulo, alarga duración de combustible/filtros y mejora el bono del '
             'Sacred Amulet.',
  'elite_perk': '+2 slots extra en Generador, Air Filter y Water Collector.',
  'how_to_level': 'Construir módulos del Hideout y consumir combustible, filtros FP-100 y filtros de agua mientras '
                  'mantenés crafteos activos.'},
 {'id': 'weapon_maintenance',
  'name': 'Weapon Maintenance (Mantenimiento)',
  'category': 'Práctica',
  'requirements': 'Sin requisito obligatorio',
  'effects': 'Reduce el desgaste permanente al reparar armas y aumenta la probabilidad de aplicar Enhancements (bonos '
             'dorados/azules).',
  'elite_perk': 'Mayor chance de Enhancements raros y menor pérdida de durabilidad máxima.',
  'how_to_level': 'Reparar armas dañadas de Scavs o Raids usando Weapon Repair Kits (en alijo, antes de venderlas a '
                  'Mechanic).'},
 {'id': 'attention',
  'name': 'Attention (Atención)',
  'category': 'Mental',
  'requirements': 'Intelligence Center Nv. 2 (Nv. 3) · Water Collector Nv. 2 (Nv. 3)',
  'effects': 'Acelera el tiempo para revelar ítems al lootear y mejora chance de encontrar mejor botín al abrir '
             'contenedores.',
  'elite_perk': '50% de probabilidad de examinar un ítem instantáneamente al aparecer.',
  'how_to_level': 'Llevar ítems encontrados al inventario y volver a soltarlos si hace falta; revisar contenedores '
                  'nuevos en cada raid.'},
 {'id': 'perception',
  'name': 'Perception (Percepción)',
  'category': 'Mental',
  'requirements': 'Clave para PvP y detección temprana',
  'effects': 'Aumenta el rango de audición (+0.3% por nivel -> +15% en Élite) y el radio del punto blanco de detección '
             'de loot.',
  'elite_perk': 'Máxima distancia auditiva de pasos/recargas combinable con auriculares ComTac V/VI.',
  'how_to_level': 'Recoger cualquier ítem suelto del suelo/cajas dentro del raid (especialmente los primeros ítems de '
                  'cada partida).'},
 {'id': 'surgery',
  'name': 'Surgery (Cirugía)',
  'category': 'Práctica',
  'requirements': 'Clave para supervivencia en Squad/Solo',
  'effects': 'Acelera tiempo de uso de CMS / Surv12 y reduce la pérdida de HP máximo de extremidades reparadas.',
  'elite_perk': 'La extremidad operada conserva prácticamente el 100% de su HP máximo original y tarda mucho menos.',
  'how_to_level': 'Reparar extremidades en negro usando CMS o Surv12 en raid.'}]


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
                sk.get("requirements", ""),
                sk.get("effects", ""),
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
