"""
TarkovScope - Base de Datos de Guías Tácticas Offline de Misiones (Wiki Dossier)
Contiene walkthroughs paso a paso en español, coordenadas de objetivos en mapas 2D,
requerimientos de llaves con datos de trueque/compra y advertencias de peligro (minas, francotiradores).
Lógica pura de negocio (Clean Architecture, sin dependencias de UI).
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from core.maps_data import normalize_map_key, MAPS_TACTICAL_DATA


# Coordenadas y datos específicos para misiones clave de Escape from Tarkov
CURATED_QUEST_GUIDES: Dict[str, Dict[str, Any]] = {
    # Prapor
    "Shooting Cans": {
        "map_key": "groundzero",
        "objective_poi": "Edificios Empire y Capital Insight (Plaza Central)",
        "map_pin": (0.48, 0.42),
        "keys_required": [],
        "phases": [
            {
                "phase": "FASE 1: Preparación",
                "badge": "EQUIPO",
                "desc": "Ground Zero está limitado a jugadores nivel 1-20 en cola inicial. Lleva un arma automática compacta o escopeta; el combate es a corta y media distancia en pasillos."
            },
            {
                "phase": "FASE 2: Ametralladora Utyos",
                "badge": "OBJETIVO",
                "desc": "Entra al edificio Empire (lado sur de la plaza). Sube al 2do piso por las escaleras principales. La ametralladora fija NSV Utyos está montada apuntando a la calle principal."
            },
            {
                "phase": "FASE 3: Lanzagranadas AGS-30",
                "badge": "OBJETIVO",
                "desc": "Cruza hacia el edificio Capital Insight (noroeste de Empire). Sube al 2do piso; el lanzagranadas automático AGS está en la sala con ventanales que dan a la plaza central."
            },
            {
                "phase": "FASE 4: Bajas y Extracción",
                "badge": "COMBATE",
                "desc": "Elimina a 5 enemigos (Scavs o PMCs) en cualquier sector. Extrae por Emercom Checkpoint (norte) o Nakatani Basement Stairs (sur)."
            }
        ],
        "danger_notes": [
            "⚠️ No avances por el medio de Mira Avenue hacia el este sin disparar una bengala verde (Green Flare) en la zona de señal, o el francotirador invisible te matará de un solo disparo.",
            "⚠️ En las plantas bajas de Empire y Capital Insight suelen spawnear grupos de 2-3 Scavs agresivos."
        ]
    },
    "Background Check": {
        "map_key": "customs",
        "objective_poi": "Camión Cisterna de Combustible en la Zona de Construcción",
        "map_pin": (0.42, 0.54),
        "keys_required": [
            {
                "name": "Machinery Key (Llave de Maquinaria)",
                "location": "Habitación 205 de Dorms de 3 pisos (en la campera azul colgada detrás de la puerta) o en bolsillos/mochilas de Scavs.",
                "barter": "No requiere compra; spawn garantizado al 100% en la chaqueta de Dorms 205."
            }
        ],
        "phases": [
            {
                "phase": "FASE 1: Obtener la Machinery Key",
                "badge": "LLAVE",
                "desc": "Ve a los Dorms de 3 pisos en Customs. Entra al segundo piso, dirígete a la habitación 205 (sin llave). Revisa la campera azul colgada: la Machinery Key spawnea ahí de forma garantizada."
            },
            {
                "phase": "FASE 2: Infiltración en Construcción",
                "badge": "INFILTRACIÓN",
                "desc": "Dirígete a la zona de Construcción central, cerca de Skeleton / Ruza. El camión cisterna de combustible grande de color blanco/naranja está en el centro del descampado."
            },
            {
                "phase": "FASE 3: Recuperar el Reloj de Bolsillo",
                "badge": "OBJETIVO",
                "desc": "Abre la puerta del conductor del camión con la Machinery Key. El reloj de bolsillo de bronce (Bronze Pocket Watch) está en el piso, entre los pedales del camión."
            },
            {
                "phase": "FASE 4: Extracción y Entrega",
                "badge": "EXTRACCIÓN",
                "desc": "El reloj se guarda en el inventario especial de misiones (Quest Inventory). Extrae con vida por ZB-1011 o Crossroads y entrégaselo a Prapor inmediatamente."
            }
        ],
        "danger_notes": [
            "⚠️ La zona de Construcción es el punto más caliente de Customs: Reshala y sus guardias pueden estar en Stronghold, y suele haber francotiradores en los techos de esqueletos de hormigón.",
            "⚠️ Si mueres con el reloj antes de extraer, deberás volver a abrir el camión con la llave."
        ]
    },
    "Delivery From the Past": {
        "map_key": "customs",
        "objective_poi": "Oficina del Director en Big Red (Customs) y Factoría (Factory)",
        "map_pin": (0.15, 0.48),
        "keys_required": [
            {
                "name": "Customs Factory Corner Key (Oficina de Aduanas)",
                "location": "Abre las oficinas del 2do piso dentro del galpón Big Red.",
                "barter": "Compra en Therapist LL2 o barter de fósforos/mechero."
            }
        ],
        "phases": [
            {
                "phase": "FASE 1: Obtener el maletín en Customs",
                "badge": "PARTE 1 (CUSTOMS)",
                "desc": "Entra a Big Red con la llave de oficina. Rompe la puerta contigua de madera con una patada (Breach). El maletín 'Tarcone Director's Secure Case' está bajo el escritorio del rincón."
            },
            {
                "phase": "FASE 2: Sobrevivir y Salir de Customs",
                "badge": "EXTRACCIÓN",
                "desc": "Extrae con vida de Customs. En el menú de personajes, puedes mover el maletín al 'Off-raid Quest Stash' si no vas a jugar Factory de inmediato para no arriesgarlo."
            },
            {
                "phase": "FASE 3: Colocación en Factory",
                "badge": "PARTE 2 (FACTORY)",
                "desc": "Despliega en Factory (preferentemente nocturno o en grupo). Ve a la sala de control metálica elevada en la zona de silos (Night Factory o Planta 2). Mantén 'F' durante 30 segundos para plantar el maletín."
            },
            {
                "phase": "FASE 4: Extracción de Factory",
                "badge": "FINAL",
                "desc": "Sobrevive y extrae de Factory por Gate 3 o salidas de llave (Cellars / Gate 0)."
            }
        ],
        "danger_notes": [
            "⚠️ Si mueres en Factory mientras plantas el maletín, perderás el objeto y deberás volver a recogerlo en Big Red en Customs.",
            "⚠️ Planta el maletín agachado o tumbado detrás de las placas de metal para evitar que te disparen desde la planta baja de Factory."
        ]
    },
    "Introduction": {
        "map_key": "woods",
        "objective_poi": "Campamento de Cazador de Jaeger cerca del avión derribado",
        "map_pin": (0.64, 0.72),
        "keys_required": [],
        "phases": [
            {
                "phase": "FASE 1: Preparación",
                "badge": "DESBLOQUEO JAEGER",
                "desc": "Misión crítica que desbloquea al Trader Jaeger. Se realiza en Woods tras alcanzar nivel 2 con Mechanic."
            },
            {
                "phase": "FASE 2: Localizar el Avión Derribado",
                "badge": "LOCALIZACIÓN",
                "desc": "Dirígete al sureste de Woods, entre Scav House y la fábrica abandonada / ruinas de la mina. Busca el fuselaje de un avión de pasajeros partido a la mitad entre los pinos."
            },
            {
                "phase": "FASE 3: Encontrar el Puesto de Jaeger",
                "badge": "OBJETIVO",
                "desc": "A unos 30 metros al sur del avión hay una torre de caza de madera camuflada y un refugio de campaña en el suelo. Debajo de la tarima de madera hay una carta encintada ('Encrypted Letter for Mechanic')."
            },
            {
                "phase": "FASE 4: Extracción Segura",
                "badge": "EXTRACCIÓN",
                "desc": "Recoge la carta y extrae con vida por Outskirts, RUAF Roadblock o UN Roadblock. Entrégasela a Mechanic para desbloquear a Jaeger."
            }
        ],
        "danger_notes": [
            "⚠️ Cuidado con la zona de minas terrestres al sureste; mantente pegado a la zona boscosa del avión y no pises los carteles con calaveras.",
            "⚠️ Si mueres antes de extraer, la carta no se guarda en tu alijo y tendrás que volver a recogerla."
        ]
    },
    "Saving the Mole": {
        "map_key": "groundzero",
        "objective_poi": "Edificio TerraGroup (Plaza Norte) y Oficina del Científico",
        "map_pin": (0.52, 0.28),
        "keys_required": [
            {
                "name": "TerraGroup Science Office Key",
                "location": "Spawnea en el cadáver del científico en el pasillo de la planta baja de TerraGroup.",
                "barter": "No requiere compra previa; se recoge en la misma raid."
            }
        ],
        "phases": [
            {
                "phase": "FASE 1: Entrar a TerraGroup",
                "badge": "INFILTRACIÓN",
                "desc": "Accede al edificio principal de TerraGroup en el norte de Ground Zero. En el hall de entrada suele haber Scavs patrullando."
            },
            {
                "phase": "FASE 2: Obtener la Llave del Científico",
                "badge": "LLAVE",
                "desc": "Ve al pasillo de la planta baja cerca de las oficinas médicas. Revisa el cadáver del empleado de TerraGroup caído en el suelo para tomar la 'TerraGroup Science Office Key'."
            },
            {
                "phase": "FASE 3: Subir al 2do Piso y Asegurar el Disco",
                "badge": "OBJETIVO",
                "desc": "Sube al segundo piso y abre la oficina del científico (puerta blanca acristalada). El disco duro (Hard Drive) está escondido en el escritorio o estante detrás del monitor."
            },
            {
                "phase": "FASE 4: Extracción",
                "badge": "EXTRACCIÓN",
                "desc": "Sobrevive y extrae por Emercom o el ascensor del sótano y entrega el disco a Mechanic."
            }
        ],
        "danger_notes": [
            "⚠️ En el 2do piso de TerraGroup hay minas de arcilla (Claymores) en el pasillo que conecta con las oficinas traseras. Sigue el camino marcado y no saltes sobre las barricadas con cables trampa."
        ]
    },
    "Operation Aquarius": {
        "map_key": "customs",
        "objective_poi": "Dorms de 2 Pisos - Habitación 206",
        "map_pin": (0.56, 0.38),
        "keys_required": [
            {
                "name": "Dorm Room 206 Key",
                "location": "En bolsillos de Scavs, camperas de Dorms o compra en el Flea Market.",
                "barter": "Therapist trueque por 1 botella de agua y 1 lata de comida."
            }
        ],
        "phases": [
            {
                "phase": "FASE 1: Conseguir la Llave 206",
                "badge": "PREPARACIÓN",
                "desc": "Adquiere la Dorm Room 206 Key antes de desplegar. Asegúrate de llevarla en tu contenedor seguro (Docs Case / Keytool / Alpha / Beta / Gamma)."
            },
            {
                "phase": "FASE 2: Infiltrarse en Dorms de 2 Pisos",
                "badge": "INFILTRACIÓN",
                "desc": "Entra a los Dorms de 2 pisos (edificio sur) por la entrada este o trasera. Sube al segundo piso."
            },
            {
                "phase": "FASE 3: Abrir y Comprobar el Agua",
                "badge": "OBJETIVO",
                "desc": "Abre la habitación 206 con la llave. Entra y camina hasta el montón de bidones de agua en el rincón. El objetivo se completará de inmediato al pisar la sala."
            },
            {
                "phase": "FASE 4: Extracción",
                "badge": "EXTRACCIÓN",
                "desc": "Sobrevive y extrae de Customs para validar la misión con Therapist."
            }
        ],
        "danger_notes": [
            "⚠️ Los Dorms de 2 y 3 pisos concentran a jugadores veteranos y a Reshala con sus 4 guardias armados con BT/BS.",
            "⚠️ En la parte 2 de esta misión deberás eliminar 15 Scavs en Customs."
        ]
    },
    "Shortage": {
        "map_key": "all",
        "objective_poi": "Botiquines Médicos Salewa (5 unidades con estado FiR)",
        "map_pin": (0.5, 0.5),
        "keys_required": [],
        "phases": [
            {
                "phase": "FASE 1: Fabricación en el Hideout",
                "badge": "MÉTODO 1 (RECOMENDADO)",
                "desc": "Sube el módulo Medstation Nivel 1 en tu Hideout. Puedes fabricar Salewas usando 1x Car First Aid Kit + 2x Bandages + 1x Splint. Todo lo fabricado en el refugio cuenta con estado 'Found in Raid' (FiR) válido."
            },
            {
                "phase": "FASE 2: Loot en Raid (Customs / Woods)",
                "badge": "MÉTODO 2",
                "desc": "En Customs: Revisa el campamento médico militar de USEC (cerca de la fábrica de silos) y el Crackhouse (edificio de laboratorios con biblioteca). Hay estantes repletos de suministros médicos."
            },
            {
                "phase": "FASE 3: Loot en Woods (USEC Camp y Base Militar)",
                "badge": "MÉTODO 3",
                "desc": "En Woods: El campamento militar al lado del lago y las mesas médicas de USEC Camp spawnean entre 2 y 4 Salewas por incursión."
            },
            {
                "phase": "FASE 4: Entrega Progresiva",
                "badge": "ENTREGA",
                "desc": "Puedes entregar las Salewas una por una a Therapist a medida que las consigas en la pantalla de entrega sin necesidad de tener las 5 juntas."
            }
        ],
        "danger_notes": [
            "⚠️ Si compras las Salewas en el Flea Market NO contarán con estado Found in Raid y Therapist no las aceptará.",
            "⚠️ En el campamento USEC Camp de Woods, la ladera norte está completamente minada con minas invisibles antipersona."
        ]
    },
    "Fishing Gear": {
        "map_key": "shoreline",
        "objective_poi": "Bote de pescadores en la Costa / Playa de Shoreline",
        "map_pin": (0.34, 0.82),
        "keys_required": [],
        "phases": [
            {
                "phase": "FASE 1: Conseguir el Rifle SV-98 y la Multiherramienta",
                "badge": "COMPRA",
                "desc": "Compra un rifle de francotirador SV-98 (en Prapor LL3 o Flea) y la 'Leatherman Multitool' (en Mechanic LL1 por ~25,000₽). Pon la multiherramienta en tu contenedor seguro (no se consume)."
            },
            {
                "phase": "FASE 2: Infiltrarse en la Costa de Shoreline",
                "badge": "INFILTRACIÓN",
                "desc": "Despliega en Shoreline. Dirígete a la playa del sur, entre el Muelle (Pier / Gas Station) y el faro de la costa. Busca un pequeño bote pesquero de madera azul y blanco varado en la arena."
            },
            {
                "phase": "FASE 3: Esconder el SV-98 y la Multiherramienta",
                "badge": "OBJETIVO",
                "desc": "Acércate al bote y túmbate detrás para cubrirte. Mantén presionado 'F' durante 30 segundos para plantar el SV-98 y luego otros 30 segundos para la multiherramienta."
            },
            {
                "phase": "FASE 4: Sobrevivir y Extraer",
                "badge": "EXTRACCIÓN",
                "desc": "Sobrevive y extrae por Tunnel, Path to Lighthouse o Road to Customs."
            }
        ],
        "danger_notes": [
            "⚠️ La playa no tiene cobertura sólida. Se recomienda hacer esta misión de noche o con granadas de humo para no ser blanco fácil de francotiradores desde las colinas de la gasolinera.",
            "⚠️ Sanitar y sus guardias pueden spawnear en el Pier justo al este del bote de pesca."
        ]
    }
}


def extract_required_keys_deep(quest: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extrae las llaves requeridas con nombres limpios y datos de uso."""
    title = quest.get("title", "")
    if title in CURATED_QUEST_GUIDES and CURATED_QUEST_GUIDES[title].get("keys_required"):
        return CURATED_QUEST_GUIDES[title]["keys_required"]

    keys_found = []
    lines = quest.get("objectives_lines", [])
    for line in lines:
        l_low = line.lower()
        if "key" in l_low or "llave" in l_low or "keycard" in l_low:
            m = re.search(r"((?:[A-Za-z0-9\.\'\-]+\s+){1,4}(?:key|keycard|marked\s+key|llave)(?:\s+[0-9a-zA-Z\-]+)?)", line, flags=re.IGNORECASE)
            if m:
                k_name = m.group(1).strip(" •-:,.")
                if len(k_name) > 3 and k_name.lower() not in [k["name"].lower() for k in keys_found]:
                    keys_found.append({
                        "name": k_name,
                        "location": f"Requerida para acceder al objetivo en {quest.get('primary_map', 'el mapa')}.",
                        "barter": "Revisa los comerciantes del juego o el Flea Market para adquirirla."
                    })
    return keys_found[:3]


def get_quest_tactical_guide(quest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retorna la ficha táctica integral de la misión para el Dossier Offline (estilo Wiki).
    Si existe guía curada, la provee completa con coordenadas exactas;
    en caso contrario, sintetiza de manera inteligente el protocolo táctico en español
    para garantizar 100% de cobertura en las 459 misiones del juego.
    """
    title = quest.get("title", "")
    primary_map = quest.get("primary_map", "Cualquier Mapa")
    norm_map = normalize_map_key(primary_map)
    obj_lines = quest.get("objectives_lines", [])
    rewards_lines = quest.get("rewards_lines", [])

    # 1. Si existe guía curada exacta
    if title in CURATED_QUEST_GUIDES:
        guide = dict(CURATED_QUEST_GUIDES[title])
        guide["title"] = title
        guide["trader_name"] = quest.get("trader_name", "Prapor")
        guide["primary_map"] = primary_map
        guide["keys"] = extract_required_keys_deep(quest)
        guide["objectives_lines"] = obj_lines
        guide["rewards_lines"] = rewards_lines
        return guide

    # 2. Generación procedural de alta fidelidad basada en análisis sintáctico de la misión
    map_info = MAPS_TACTICAL_DATA.get(norm_map, {})
    map_name = map_info.get("name", primary_map)
    keys_detected = extract_required_keys_deep(quest)

    # Identificar naturaleza de la misión
    all_obj_str = " ".join(obj_lines).lower()
    is_kill = "eliminate" in all_obj_str or "kill" in all_obj_str or "elimina" in all_obj_str
    is_fir = "found in raid" in all_obj_str or "in raid" in all_obj_str or "fir" in all_obj_str
    is_locate = "locate" in all_obj_str or "find" in all_obj_str or "obtain" in all_obj_str or "encuentra" in all_obj_str
    is_plant = "place" in all_obj_str or "plant" in all_obj_str or "stash" in all_obj_str or "marca" in all_obj_str or "beacon" in all_obj_str

    phases = []

    # Fase 1: Equipamiento y Llaves
    phase_1_desc = f"Verifica tu equipamiento antes de entrar a {map_name}. "
    if keys_detected:
        key_names = [k['name'] for k in keys_detected]
        phase_1_desc += f"Asegúrate de llevar en tu contenedor seguro ({', '.join(key_names)}) para no perderlas si mueres. "
    if is_plant:
        phase_1_desc += "Guarda marcadores MS2000, cámaras Wi-Fi o balizas en el pouch seguro; puedes colocarlos directamente desde allí. "
    if is_kill:
        phase_1_desc += "Equípate con armas y munición de alta penetración según la armadura esperada de los objetivos. "
    phases.append({
        "phase": "FASE 1: Preparación y Logística",
        "badge": "EQUIPO",
        "desc": phase_1_desc
    })

    # Fase 2: Infiltración y Despliegue
    phase_2_desc = f"Despliega en {map_name}. "
    if map_info.get("extractions"):
        first_ex = map_info["extractions"][0]["name"]
        phase_2_desc += f"Identifica tus extracciones asignadas (ej. {first_ex}) según tu punto de aparición para planificar tu ruta de escape anticipadamente. "
    if map_info.get("bosses"):
        boss_names = [b.split(" (")[0] for b in map_info["bosses"][:2]]
        phase_2_desc += f"Precaución en zonas calientes ante posibles patrullas de Bosses ({', '.join(boss_names)}). "
    phases.append({
        "phase": f"FASE 2: Infiltración en {map_name}",
        "badge": "RUTA",
        "desc": phase_2_desc
    })

    # Fase 3: Ejecución de Objetivos
    phase_3_desc = "Cumple con las directivas asignadas:\n"
    for idx_o, obj in enumerate(obj_lines, start=1):
        clean_o = obj.lstrip("• ").strip()
        phase_3_desc += f"  • Paso {idx_o}: {clean_o}\n"
    if is_fir:
        phase_3_desc += "Los ítems requeridos 'Found in Raid' deben extraerse con estado 'Survived' (al menos 7 min en raid o 200+ EXP) o craftearse en el Hideout."
    phases.append({
        "phase": "FASE 3: Ejecución Táctica de Objetivos",
        "badge": "OBJETIVO",
        "desc": phase_3_desc.strip()
    })

    # Fase 4: Extracción
    phases.append({
        "phase": "FASE 4: Extracción y Protocolo de Entrega",
        "badge": "EXTRACCIÓN",
        "desc": f"Evita combates innecesarios al completar las tareas y dirígete a tu punto de extracción más seguro en {map_name}. Si recogiste un ítem especial del Quest Inventory, entrégalo inmediatamente al Trader tras salir de raid."
    })

    # Advertencias de peligro
    danger_notes = []
    if "ground zero" in primary_map.lower():
        danger_notes.append("⚠️ Advertencia: No avances por Mira Avenue hacia el este sin disparar una bengala verde (Green Flare) en la zona de señal delimitada.")
    elif "woods" in primary_map.lower():
        danger_notes.append("⚠️ Advertencia: La frontera este y el USEC Camp tienen campos de minas terrestres activos. Respeta los carteles de advertencia de calavera.")
    elif "customs" in primary_map.lower():
        danger_notes.append("⚠️ Advertencia: En Dorms y Fortaleza (Stronghold) pueden spawnear Reshala y sus guardias o The Goons con fuego de ametralladora pesada.")
    elif "shoreline" in primary_map.lower():
        danger_notes.append("⚠️ Advertencia: El complejo Health Resort concentra combate CQC de alto calibre. Lleva audífonos tácticos y granadas de despeje.")
    elif "lighthouse" in primary_map.lower():
        danger_notes.append("⚠️ Advertencia: La planta de tratamiento de agua está custodiada por Rogues con lanzagranadas AGS y ametralladoras montadas en los techos.")
    else:
        danger_notes.append("⚠️ Advertencia Táctica: Mantén audio al máximo y revisa esquinas antes de abrir puertas con llave.")

    # Coordenadas por defecto en el centro del mapa
    default_pin = (0.50, 0.50)
    if "customs" in norm_map:
        default_pin = (0.45, 0.52)
    elif "woods" in norm_map:
        default_pin = (0.50, 0.60)
    elif "factory" in norm_map:
        default_pin = (0.50, 0.50)
    elif "interchange" in norm_map:
        default_pin = (0.50, 0.45)
    elif "ground" in norm_map:
        default_pin = (0.50, 0.40)

    return {
        "title": title,
        "trader_name": quest.get("trader_name", "Prapor"),
        "primary_map": primary_map,
        "map_key": norm_map,
        "objective_poi": f"Zona de operaciones en {primary_map}",
        "map_pin": default_pin,
        "keys": keys_detected,
        "phases": phases,
        "danger_notes": danger_notes,
        "objectives_lines": obj_lines,
        "rewards_lines": rewards_lines
    }
