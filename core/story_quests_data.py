"""
TarkovScope - Base de Datos Exhaustiva de Quests de la Historia (Storyline Chapters 1 al 10)
Contiene las misiones oficiales de campaña introducidas en Escape from Tarkov que narran
la trama principal completa, desde la huida inicial de Ground Zero hasta los 4 finales de escape:
1. Tour (11 misiones)
2. Batya (8 misiones)
3. Falling Skies (8 misiones)
4. Accidental Witness (7 misiones)
5. They Are Already Here (7 misiones)
6. The Unheard (7 misiones)
7. Blue Fire (6 misiones)
8. Boreas (6 misiones)
9. The Ticket (6 misiones)
10. The Labyrinth (6 misiones)
"""
from typing import List, Dict, Any

STORYLINE_QUESTS_DATA: List[Dict[str, Any]] = [
    # =========================================================================
    # CHAPTER 1: TOUR (11 MISIONES)
    # =========================================================================
    {
        "id": "tour_01",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Ground Zero Escape",
        "trader": "Therapist",
        "map": "Ground Zero",
        "level_req": 1,
        "briefing": (
            "Tras quedar atrapado en el sector financiero de Ground Zero durante la evacuación inicial, "
            "debes contactar a Therapist y coordinar la salida hacia la ciudad abierta de Tarkov."
        ),
        "objectives": [
            "Sobrevivir y extraer de Ground Zero",
            "Hablar con Therapist en el refugio",
            "Obtener las primeras directivas de evacuación"
        ],
        "rewards": {"xp": 3500, "rep": "+0.02 Therapist", "roubles": "25,000 ₽", "items": ["2x Botiquín Salewa", "Férula Inmovilizadora"]}
    },
    {
        "id": "tour_02",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Access to Streets of Tarkov",
        "trader": "Therapist",
        "map": "Streets of Tarkov",
        "level_req": 2,
        "briefing": (
            "Para abrir las rutas hacia las avenidas principales de Streets of Tarkov, Therapist necesita asegurar "
            "fondos de rescate para sobornar a los puestos de control locales."
        ),
        "objectives": [
            "Entregar 250,000 Roubles a Therapist (o completar reconocimiento de ruta)",
            "Asegurar el acceso seguro al mapa Streets of Tarkov",
            "Sobrevivir y extraer de una incursión en Streets"
        ],
        "rewards": {"xp": 5200, "rep": "+0.03 Therapist", "roubles": "45,000 ₽", "items": ["Inyector Propital", "Llave de Farmacia"]}
    },
    {
        "id": "tour_03",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Interchange Recon",
        "trader": "Ragman",
        "map": "Interchange",
        "level_req": 3,
        "briefing": (
            "Ragman controla las rutas logísticas del centro comercial Ultra en Interchange. "
            "Necesita que inspecciones el estado de las galerías centrales y confirmes si Killa o sus bandas patrullan la zona."
        ),
        "objectives": [
            "Hablar con Ragman sobre las rutas comerciales",
            "Sobrevivir y extraer de Interchange (o explorar Ultra 3 veces)",
            "Informar a Ragman sobre el estado del centro comercial"
        ],
        "rewards": {"xp": 5800, "rep": "+0.03 Ragman", "roubles": "38,000 ₽", "items": ["Chaleco 6B23-1", "Casco Kolpak-1S"]}
    },
    {
        "id": "tour_04",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Customs Supply Line",
        "trader": "Skier",
        "map": "Customs",
        "level_req": 4,
        "briefing": (
            "Skier no confía en recién llegados. Para ganar su favor y asegurar el tránsito hacia la zona industrial "
            "de Customs, te exige reunir materiales de construcción encontrados en incursión."
        ),
        "objectives": [
            "Hablar con Skier en su puesto de contrabando",
            "Entregar 5 materiales de construcción 'Found in Raid' a Skier",
            "Sobrevivir y extraer de Customs"
        ],
        "rewards": {"xp": 6400, "rep": "+0.04 Skier", "roubles": "42,000 ₽", "items": ["Mochila Berkut", "Pistola TT-33"]}
    },
    {
        "id": "tour_05",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Factory Arsenal",
        "trader": "Mechanic",
        "map": "Factory",
        "level_req": 5,
        "briefing": (
            "Mechanic busca evaluar tus capacidades en combates cerrados. Te envía a la fábrica química (Factory) "
            "a recuperar armamento operativo bajo el asedio continuo de Tagilla."
        ),
        "objectives": [
            "Hablar con Mechanic en su taller",
            "Sobrevivir y extraer de Factory",
            "Entregar 2 armas operativas 'Found in Raid' a Mechanic"
        ],
        "rewards": {"xp": 6800, "rep": "+0.03 Mechanic", "roubles": "50,000 ₽", "items": ["Escopeta MP-133 Táctica", "50x Cartuchos Flechette"]}
    },
    {
        "id": "tour_06",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Woods Hostile Sweep",
        "trader": "Skier",
        "map": "Woods",
        "level_req": 6,
        "briefing": (
            "Los francotiradores y cazadores de Shturman dominan los bosques de Woods. "
            "Skier te encarga neutralizar amenazas activas en el perímetro del aserradero."
        ),
        "objectives": [
            "Eliminar a 3 objetivos hostiles en Woods",
            "Sobrevivir y extraer de Woods con vida",
            "Confirmar la limpieza del sector a Skier"
        ],
        "rewards": {"xp": 7200, "rep": "+0.03 Skier", "roubles": "48,000 ₽", "items": ["Rifle Mosin Infantería", "60x Munición 7.62x54R LPS"]}
    },
    {
        "id": "tour_07",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Port Terminal Gate",
        "trader": "Peacekeeper",
        "map": "Shoreline",
        "level_req": 8,
        "briefing": (
            "El objetivo supremo de cualquier operador es la salida marítima de Tarkov a través de la Terminal del Puerto. "
            "Llega a las puertas exteriores blindadas de la Terminal y utiliza el intercomunicador militar para contactar a la guarnición."
        ),
        "objectives": [
            "Localizar la entrada exterior blindada a la Terminal del Puerto",
            "Usar el intercomunicador de la puerta para contactar a los guardias portuarios",
            "Descubrir los requisitos oficiales de escape de Tarkov",
            "Sobrevivir y extraer de Shoreline"
        ],
        "rewards": {"xp": 9500, "rep": "+0.04 Peacekeeper", "roubles": "$ 850 USD", "items": ["Fusil Colt M4A1", "3x Cargadores STANAG"]}
    },
    {
        "id": "tour_08",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Reserve Infiltration",
        "trader": "Prapor",
        "map": "Reserve",
        "level_req": 10,
        "briefing": (
            "La base militar federal de Reserve contiene los depósitos estatales de armamento de emergencia. "
            "Prapor te exige probar tu temple en combate entregando placas identificatorias (dogtags) de otros operadores."
        ),
        "objectives": [
            "Asegurar el acceso a la base militar de Reserve",
            "Entregar 5 dogtags de PMCs enemigos a Prapor",
            "Sobrevivir y extraer de Reserve"
        ],
        "rewards": {"xp": 8800, "rep": "+0.04 Prapor", "roubles": "65,000 ₽", "items": ["AK-74M", "Granada F-1", "Cargador 60 tiros 6L31"]}
    },
    {
        "id": "tour_09",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Shoreline Sanitarium Recon",
        "trader": "Therapist",
        "map": "Shoreline",
        "level_req": 12,
        "briefing": (
            "El balneario Azure Coast en Shoreline fue el epicentro de las investigaciones médicas encubiertas de TerraGroup. "
            "Inspecciona las tres alas del sanatorio y localiza las rutas seguras de extracción."
        ),
        "objectives": [
            "Inspeccionar las alas Este, Oeste y edificio de administración del balneario",
            "Sobrevivir y extraer de Shoreline",
            "Entregar reporte médico preliminar a Therapist"
        ],
        "rewards": {"xp": 8200, "rep": "+0.03 Therapist", "roubles": "55,000 ₽", "items": ["Botiquín Grizzly 1800 HP", "Inyector SJ6"]}
    },
    {
        "id": "tour_10",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - Lighthouse Clearance",
        "trader": "Mechanic",
        "map": "Lighthouse",
        "level_req": 15,
        "briefing": (
            "El cabo de Lighthouse está custodiado por Rogues USEC en la planta de tratamiento y francotiradores en las colinas. "
            "Mechanic necesita fondos en divisas fuertes para financiar los códigos de acceso de radiobaliza."
        ),
        "objectives": [
            "Asegurar el acceso a Lighthouse",
            "Entregar $ 8,000 USD a Mechanic para la red satelital",
            "Sobrevivir y extraer de Lighthouse"
        ],
        "rewards": {"xp": 10500, "rep": "+0.04 Mechanic", "roubles": "80,000 ₽", "items": ["Rifle SR-25 7.62x51", "Mira Vortex Razor HD 1-6x"]}
    },
    {
        "id": "tour_11",
        "chapter_id": 1,
        "chapter_name": "Chapter 1: Tour",
        "title": "Tour - The Lab Secret Entry",
        "trader": "Mechanic",
        "map": "The Lab",
        "level_req": 20,
        "briefing": (
            "Culminación del capítulo Tour: ingresar al complejo subterráneo ultra secreto de The Lab bajo las calles de Tarkov. "
            "Debes infiltrarte en las oficinas de la alta gerencia de TerraGroup, la sala de servidores principal y el sistema de drenaje de escape."
        ),
        "objectives": [
            "Conseguir una tarjeta de acceso TerraGroup Labs Access Keycard",
            "Infiltrarse en The Lab y revisar las oficinas de la alta gerencia",
            "Explorar la sala de servidores central",
            "Localizar el conducto de escape subterráneo del drenaje (Sewers)",
            "Sobrevivir y extraer de The Lab"
        ],
        "rewards": {"xp": 18000, "rep": "+0.06 Mechanic", "roubles": "150,000 ₽", "items": ["Tarjeta Keycard de Acceso", "Inyector LEDX", "Maletín de Municiones"]}
    },

    # =========================================================================
    # CHAPTER 2: BATYA (8 MISIONES)
    # =========================================================================
    {
        "id": "batya_01",
        "chapter_id": 2,
        "chapter_name": "Chapter 2: Batya",
        "title": "Batya - Traces of the Bogatyrs",
        "trader": "Prapor",
        "map": "Customs",
        "level_req": 14,
        "briefing": (
            "El escuadrón especial de élite BEAR conocido como los Bogatyrs desapareció en combate sin dejar rastro formal. "
            "Descubre las primeras huellas del escuadrón en los refugios improvisados de Customs, Reserve o Shoreline."
        ),
        "objectives": [
            "Localizar las marcas secretas de los Bogatyrs en el sitio de construcción de Customs (o radar de Reserve)",
            "Encontrar el parche distintivo del escuadrón Bogatyr",
            "Consultar a Prapor sobre el destino de los comandos BEAR"
        ],
        "rewards": {"xp": 7500, "rep": "+0.03 Prapor", "roubles": "45,000 ₽", "items": ["Parche Bogatyr", "Munición 7.62x39 BP"]}
    },
    {
        "id": "batya_02",
        "chapter_id": 2,
        "chapter_name": "Chapter 2: Batya",
        "title": "Batya - Ryabina Outpost",
        "trader": "Prapor",
        "map": "Woods",
        "level_req": 15,
        "briefing": (
            "Los Bogatyrs mantenían un puesto de avanzada fortificado denominado 'Ryabina' en los densos bosques de Woods. "
            "Revisa las posiciones defensivas y recupera efectos personales de los soldados."
        ),
        "objectives": [
            "Localizar el puesto de avanzada Ryabina en Woods",
            "Recuperar el recuerdo personal de uno de los soldados Bogatyr",
            "Sobrevivir y extraer de Woods"
        ],
        "rewards": {"xp": 8200, "rep": "+0.03 Prapor", "roubles": "52,000 ₽", "items": ["Fusil SVD Dragunov", "Mira PSO-1"]}
    },
    {
        "id": "batya_03",
        "chapter_id": 2,
        "chapter_name": "Chapter 2: Batya",
        "title": "Batya - Carousel Outpost",
        "trader": "Ragman",
        "map": "Interchange",
        "level_req": 16,
        "briefing": (
            "El escuadrón operó dentro del centro comercial Ultra bajo el nombre clave 'Carousel'. "
            "Inspecciona los túneles de carga y pasillos de servicio donde establecieron su base temporal."
        ),
        "objectives": [
            "Localizar la posición defensiva Carousel en Interchange",
            "Buscar informes sobre el avance de las fuerzas enemigas",
            "Sobrevivir y extraer de Interchange"
        ],
        "rewards": {"xp": 8600, "rep": "+0.03 Ragman", "roubles": "55,000 ₽", "items": ["Chaleco TV-110", "Auriculares ComTac 2"]}
    },
    {
        "id": "batya_04",
        "chapter_id": 2,
        "chapter_name": "Chapter 2: Batya",
        "title": "Batya - Gnezdo Outpost Fate",
        "trader": "Prapor",
        "map": "Interchange",
        "level_req": 18,
        "briefing": (
            "El último reducto conocido del escuadrón fue el puesto 'Gnezdo'. "
            "Allí los Bogatyrs sostuvieron su combate final contra un contingente masivo. Investiga qué ocurrió con el escuadrón."
        ),
        "objectives": [
            "Localizar el puesto Gnezdo en Interchange",
            "Buscar las notas personales de los comandos Strelets y Taran",
            "Encontrar las pertenencias del comandante Voevoda (Batya)"
        ],
        "rewards": {"xp": 9400, "rep": "+0.04 Prapor", "roubles": "68,000 ₽", "items": ["Armadura Korund-VM", "Cargador de tambor 95 tiros"]}
    },
    {
        "id": "batya_05",
        "chapter_id": 2,
        "chapter_name": "Chapter 2: Batya",
        "title": "Batya - Moreman's Audio Tapes",
        "trader": "Mechanic",
        "map": "Hideout",
        "level_req": 20,
        "briefing": (
            "Entre los restos del escuadrón hallaste el teléfono satelital del operador Moreman. "
            "Usa tu banco de trabajo en el refugio para reparar las cintas magnéticas de audio y escuchar sus últimas palabras."
        ),
        "objectives": [
            "Fabricar y restaurar la cinta de audio #1 de Moreman en Workbench Nivel 1",
            "Fabricar y restaurar la cinta de audio #2 de Moreman",
            "Escuchar ambas grabaciones para desentrañar la traición interna"
        ],
        "rewards": {"xp": 9800, "rep": "+0.04 Mechanic", "roubles": "75,000 ₽", "items": ["2x Circuit Boards", "Caja de Herramientas Militar"]}
    },
    {
        "id": "batya_06",
        "chapter_id": 2,
        "chapter_name": "Chapter 2: Batya",
        "title": "Batya - The Ambush Site",
        "trader": "Prapor",
        "map": "Woods",
        "level_req": 22,
        "briefing": (
            "Las grabaciones revelan las coordenadas exactas de la emboscada mortal en los valles de Woods. "
            "Acude al claro del bosque y recupera el equipo táctico encriptado que dejaron oculto bajo tierra."
        ),
        "objectives": [
            "Localizar el lugar exacto de la emboscada en Woods",
            "Recuperar el teléfono satelital y el receptor militar de Moreman",
            "Sobrevivir y extraer de Woods"
        ],
        "rewards": {"xp": 11200, "rep": "+0.04 Prapor", "roubles": "85,000 ₽", "items": ["Rifle AS VAL 9x39", "Balas SPP gs"]}
    },
    {
        "id": "batya_07",
        "chapter_id": 2,
        "chapter_name": "Chapter 2: Batya",
        "title": "Batya - Contacting Voevoda",
        "trader": "Lightkeeper",
        "map": "Lighthouse",
        "level_req": 25,
        "briefing": (
            "Para establecer contacto con el legendario comandante Voevoda necesitas un Centro de Inteligencia Nivel 3 "
            "en tu refugio y cruzar el puente minado hacia el faro de Lightkeeper para entregar las pruebas de supervivencia."
        ),
        "objectives": [
            "Poseer Centro de Inteligencia Nivel 3 en el refugio",
            "Obtener acceso a la isla de Lightkeeper en Lighthouse",
            "Entregar los objetos de los Bogatyrs a Lightkeeper"
        ],
        "rewards": {"xp": 15000, "rep": "+0.05 Lightkeeper", "roubles": "120,000 ₽", "items": ["Transmisor DSP Radio", "Balas .338 Lapua Magnum"]}
    },
    {
        "id": "batya_08",
        "chapter_id": 2,
        "chapter_name": "Chapter 2: Batya",
        "title": "Batya - Voevoda's Trial by Fire",
        "trader": "Prapor",
        "map": "Cualquier Mapa",
        "level_req": 30,
        "briefing": (
            "Voevoda solo reconoce a guerreros que dominan el arte supremo del combate. "
            "Debes completar sus brutales desafíos físicos y marciales sin morir en el intento."
        ),
        "objectives": [
            "Alcanzar nivel 5 en la habilidad Ametralladoras Ligeras (LMG)",
            "Alcanzar nivel 10 en Fusiles de Asalto",
            "Alcanzar nivel 10 en Resistencia al Estrés",
            "Alcanzar nivel 15 en Fuerza",
            "Eliminar a 15 objetivos consecutivos en combate sin morir",
            "Eliminar a 4 operadores PMC sin morir"
        ],
        "rewards": {"xp": 25000, "rep": "+0.08 Prapor", "roubles": "250,000 ₽", "items": ["Ametralladora PKP Pecheneg", "Armadura Slick Clase 6", "Logro: Legado de Batya"]}
    },

    # =========================================================================
    # CHAPTER 3: FALLING SKIES (8 MISIONES)
    # =========================================================================
    {
        "id": "sky_01",
        "chapter_id": 3,
        "chapter_name": "Chapter 3: Falling Skies",
        "title": "Falling Skies - The Downed Plane",
        "trader": "Mechanic",
        "map": "Woods",
        "level_req": 10,
        "briefing": (
            "Un avión de transporte militar no identificado fue derribado en los primeros días del bloqueo sobre los bosques de Woods. "
            "Pregunta a Mechanic y localiza el fuselaje destrozado de la aeronave entre las colinas."
        ),
        "objectives": [
            "Consultar a Mechanic sobre los radares del avión derribado",
            "Localizar el fuselaje del avión estrellado en Woods",
            "Alcanzar nivel de lealtad LL2 con Prapor",
            "Sobrevivir y extraer de Woods"
        ],
        "rewards": {"xp": 6800, "rep": "+0.03 Mechanic", "roubles": "45,000 ₽", "items": ["Kit Quirúrgico CMS", "Mortero de señales"]}
    },
    {
        "id": "sky_02",
        "chapter_id": 3,
        "chapter_name": "Chapter 3: Falling Skies",
        "title": "Falling Skies - G-Wagon Investigation",
        "trader": "Prapor",
        "map": "Shoreline",
        "level_req": 12,
        "briefing": (
            "El convoy de escolta que transportaba el soporte técnico del vuelo huyó hacia la costa de Shoreline. "
            "Inspecciona los SUVs blindados G-Wagon cerca del túnel de extracción y recupera el pendrive encriptado."
        ),
        "objectives": [
            "Localizar los vehículos G-Wagon cerca del túnel en Shoreline",
            "Extraer la memoria USB encriptada de la guantera del vehículo principal",
            "Entregar el pendrive a Prapor y aguardar su análisis"
        ],
        "rewards": {"xp": 7400, "rep": "+0.03 Prapor", "roubles": "48,000 ₽", "items": ["Chaleco PACA", "Cargador 60 tiros"]}
    },
    {
        "id": "sky_03",
        "chapter_id": 3,
        "chapter_name": "Chapter 3: Falling Skies",
        "title": "Falling Skies - Flight Recorder Recovery",
        "trader": "Prapor",
        "map": "Woods",
        "level_req": 14,
        "briefing": (
            "La caja negra del avión derribado contiene las grabaciones de voz de cabina y la telemetría del impacto de misil. "
            "Dirígete al avión en Woods y rescata la caja negra antes de que la nieve la sepulte."
        ),
        "objectives": [
            "Llegar a la cola del avión estrellado en Woods",
            "Desatornillar y extraer la caja negra de la aeronave (Flight Recorder)",
            "Sobrevivir y extraer de Woods con la caja intacta"
        ],
        "rewards": {"xp": 8500, "rep": "+0.04 Prapor", "roubles": "58,000 ₽", "items": ["Casco 6B47 Ratnik", "Munición 7.62x39 PS"]}
    },
    {
        "id": "sky_04",
        "chapter_id": 3,
        "chapter_name": "Chapter 3: Falling Skies",
        "title": "Falling Skies - Fisherman's Island Stash",
        "trader": "Prapor",
        "map": "Shoreline",
        "level_req": 15,
        "briefing": (
            "Para evitar que la inteligencia enemiga rastree la caja negra, Prapor te ordena esconderla temporalmente "
            "en una cabaña segura en la isla de los pescadores frente a la costa de Shoreline."
        ),
        "objectives": [
            "Cruzar el puente hacia la isla de los pescadores en Shoreline",
            "Ocultar la caja negra en la habitación de la esquina de la casa",
            "Sobrevivir y extraer de Shoreline"
        ],
        "rewards": {"xp": 8200, "rep": "+0.03 Prapor", "roubles": "50,000 ₽", "items": ["Botiquín Salewa", "Analgésicos Ibuprofeno"]}
    },
    {
        "id": "sky_05",
        "chapter_id": 3,
        "chapter_name": "Chapter 3: Falling Skies",
        "title": "Falling Skies - Repairing the Black Box",
        "trader": "Prapor",
        "map": "Hideout",
        "level_req": 16,
        "briefing": (
            "Los circuitos de la caja negra sufrieron daños por el impacto. "
            "Reúne componentes electrónicos militares y herramientas para que los ingenieros de Prapor puedan leer los datos."
        ),
        "objectives": [
            "Entregar 2x Cajas de Herramientas (Toolset)",
            "Entregar 3x Baterías Recargables",
            "Entregar 5x Placas de Circuitos Impresos (Printed Circuit Boards - FiR)",
            "Aguardar a que Prapor procese la extracción de datos"
        ],
        "rewards": {"xp": 9600, "rep": "+0.04 Prapor", "roubles": "65,000 ₽", "items": ["Fusil AK-74M Modificado", "Mira Óptica PSO"]}
    },
    {
        "id": "sky_06",
        "chapter_id": 3,
        "chapter_name": "Chapter 3: Falling Skies",
        "title": "Falling Skies - Elektronik's Decryption",
        "trader": "Mechanic",
        "map": "Streets of Tarkov",
        "level_req": 18,
        "briefing": (
            "El hacker 'Elektronik' logró decodificar la transcripción de la tripulación de vuelo. "
            "El informe revela que a bordo no solo viajaban científicos, sino un contenedor blindado de titanio con prototipos clasificados."
        ),
        "objectives": [
            "Obtener la transcripción de la tripulación y el pendrive seguro de Elektronik",
            "Analizar la ruta de escape mencionada por los pilotos",
            "Entregar los registros validados a Prapor"
        ],
        "rewards": {"xp": 10500, "rep": "+0.04 Mechanic", "roubles": "75,000 ₽", "items": ["Placas de Circuitos Militares", "Moneda GP"]}
    },
    {
        "id": "sky_07",
        "chapter_id": 3,
        "chapter_name": "Chapter 3: Falling Skies",
        "title": "Falling Skies - The Armored Case",
        "trader": "Prapor",
        "map": "Woods",
        "level_req": 20,
        "briefing": (
            "Las coordenadas del contenedor blindado de titanio señalan una zanja oculta junto a los escombros de la nave en Woods. "
            "Dirígete al lugar, recupera el maletín blindado ultrasecreto y escapa con vida."
        ),
        "objectives": [
            "Localizar el compartimiento secreto en la zanja de Woods",
            "Extraer el maletín blindado clasificado (Armored Case)",
            "Sobrevivir y extraer de Woods"
        ],
        "rewards": {"xp": 12000, "rep": "+0.05 Prapor", "roubles": "90,000 ₽", "items": ["Maletín Blindado", "Munición 7.62x54R BT"]}
    },
    {
        "id": "sky_08",
        "chapter_id": 3,
        "chapter_name": "Chapter 3: Falling Skies",
        "title": "Falling Skies - The Pivotal Choice",
        "trader": "Prapor",
        "map": "Refugio / Prapor",
        "level_req": 22,
        "briefing": (
            "¡Dilema crucial de la historia! Puedes entregar el maletín blindado a Prapor para seguir la ruta militar estándar hacia el capítulo 'The Ticket', "
            "o quedarte el maletín para ti y tus propios intereses (perdiendo casi toda la reputación con Prapor pero abriendo caminos alternativos)."
        ),
        "objectives": [
            "Opción A: Entregar el maletín blindado a Prapor (Ruta oficial aliada)",
            "Opción B: Conservar el maletín blindado para beneficio propio (Ruta mercenaria)",
            "Aceptar las consecuencias políticas del desenlace"
        ],
        "rewards": {"xp": 16000, "rep": "Variable según elección", "roubles": "150,000 ₽", "items": ["Desbloqueo de Capítulo: The Ticket", "Logro de Campaña"]}
    },

    # =========================================================================
    # CHAPTER 4: ACCIDENTAL WITNESS (7 MISIONES)
    # =========================================================================
    {
        "id": "witness_01",
        "chapter_id": 4,
        "chapter_name": "Chapter 4: Accidental Witness",
        "title": "Accidental Witness - Kozlov's Quarters",
        "trader": "Skier",
        "map": "Customs",
        "level_req": 8,
        "briefing": (
            "Kozlov, un contador clave de las redes clandestinas de Tarkov, desapareció repentinamente debiendo millones. "
            "Investiga su residencia en las inmediaciones de Customs y revisa indicios de violencia."
        ),
        "objectives": [
            "Averiguar dónde vivía Kozlov en Customs",
            "Leer la nota de amenaza 'Note for Kozlov (Debt)' clavada en su puerta",
            "Sobrevivir y extraer de Customs"
        ],
        "rewards": {"xp": 5400, "rep": "+0.03 Skier", "roubles": "32,000 ₽", "items": ["Pistola Tokarev", "Reloj Roto"]}
    },
    {
        "id": "witness_02",
        "chapter_id": 4,
        "chapter_name": "Chapter 4: Accidental Witness",
        "title": "Accidental Witness - The Shady Involvement",
        "trader": "Skier",
        "map": "Customs",
        "level_req": 10,
        "briefing": (
            "Descubre en qué turbios negocios estaba involucrado Kozlov antes de huir. "
            "Habla con Skier para obtener los contactos de su cómplice en los dormitorios de Customs."
        ),
        "objectives": [
            "Consultar a los comerciantes sobre Kozlov y su socia Anastasia",
            "Hablar con Skier para obtener pistas de su cómplice",
            "Reunir información sobre las deudas de contrabando"
        ],
        "rewards": {"xp": 6000, "rep": "+0.03 Skier", "roubles": "35,000 ₽", "items": ["Llave de Dormitorio", "Bálsamo Labial"]}
    },
    {
        "id": "witness_03",
        "chapter_id": 4,
        "chapter_name": "Chapter 4: Accidental Witness",
        "title": "Accidental Witness - Dorm Room 110",
        "trader": "Skier",
        "map": "Customs",
        "level_req": 12,
        "briefing": (
            "El cómplice de Skier operaba en la habitación 110 del dormitorio de 2 plantas de Customs. "
            "Consigue la llave, inspecciona la habitación revuelta y lee las cartas abandonadas."
        ),
        "objectives": [
            "Conseguir la llave de la habitación 110 del dormitorio",
            "Entrar en la habitación 110 y registrar los cajones secretos",
            "Leer las cartas y pistas dejadas por el cómplice",
            "Sobrevivir y extraer de Customs"
        ],
        "rewards": {"xp": 7200, "rep": "+0.03 Skier", "roubles": "45,000 ₽", "items": ["Cadena de Oro", "Balas 9x19 PBP"]}
    },
    {
        "id": "witness_04",
        "chapter_id": 4,
        "chapter_name": "Chapter 4: Accidental Witness",
        "title": "Accidental Witness - Anastasia's Mailbox",
        "trader": "Skier",
        "map": "Streets of Tarkov",
        "level_req": 14,
        "briefing": (
            "Las pistas te llevan al edificio residencial de Anastasia en Streets of Tarkov. "
            "Revisa el buzón número 7 en el portal de entrada y lee la correspondencia desbordada."
        ),
        "objectives": [
            "Localizar el edificio de departamentos de Anastasia en Streets of Tarkov",
            "Revisar el buzón número 7 en la entrada principal",
            "Leer las cartas enviadas por el mensajero Pasha"
        ],
        "rewards": {"xp": 7800, "rep": "+0.03 Skier", "roubles": "50,000 ₽", "items": ["Mochila VKBO", "Moneda GP"]}
    },
    {
        "id": "witness_05",
        "chapter_id": 4,
        "chapter_name": "Chapter 4: Accidental Witness",
        "title": "Accidental Witness - Courier Pasha's Fate",
        "trader": "Skier",
        "map": "Woods",
        "level_req": 16,
        "briefing": (
            "El mensajero Pasha fue interceptado mientras transportaba documentos cruciales. "
            "Localiza su bicicleta ensangrentada entre las rocas al oeste de los dormitorios en Woods y recupera el sobre bajo la chaqueta."
        ),
        "objectives": [
            "Localizar la bicicleta destrozada de Pasha junto a las rocas en Woods",
            "Recuperar el sobre confidencial oculto bajo la chaqueta ensangrentada",
            "Sobrevivir y extraer de Woods"
        ],
        "rewards": {"xp": 8600, "rep": "+0.04 Skier", "roubles": "60,000 ₽", "items": ["Rifle VPO-136", "Culata Magpul MOE"]}
    },
    {
        "id": "witness_06",
        "chapter_id": 4,
        "chapter_name": "Chapter 4: Accidental Witness",
        "title": "Accidental Witness - Reshala's Stash",
        "trader": "Skier",
        "map": "Customs",
        "level_req": 18,
        "briefing": (
            "Pasha fue emboscado por los hombres del jefe Reshala. "
            "Infiltra el campamento de Reshala en Customs y busca el escondite donde guardaron la libreta contable de Kozlov."
        ),
        "objectives": [
            "Revisar la zona de Nueva Gasolinera o Dormitorios de Reshala",
            "Localizar el escondite de contrabando con los libros contables",
            "Extraer con los documentos financieros"
        ],
        "rewards": {"xp": 9500, "rep": "+0.04 Skier", "roubles": "75,000 ₽", "items": ["Pistola TT Dorada", "Balas 7.62x39 MAI AP"]}
    },
    {
        "id": "witness_07",
        "chapter_id": 4,
        "chapter_name": "Chapter 4: Accidental Witness",
        "title": "Accidental Witness - Pay Your Debt",
        "trader": "Skier",
        "map": "Streets of Tarkov",
        "level_req": 20,
        "briefing": (
            "Culminación del caso Kozlov: descubre el refugio subterráneo final donde se ocultaba, "
            "liquida las cuentas pendientes y desbloquea el logro especial de campaña 'Pay Your Debt'."
        ),
        "objectives": [
            "Localizar el refugio subterráneo final de Kozlov en Streets of Tarkov",
            "Recuperar el maletín con los fondos residuales y documentos de identidad",
            "Entregar las pruebas a Skier y cerrar la investigación",
            "Desbloquear el logro oficial: 'Pay Your Debt'"
        ],
        "rewards": {"xp": 14000, "rep": "+0.06 Skier", "roubles": "120,000 ₽", "items": ["Maletín de Armas", "Logro: Pay Your Debt"]}
    },

    # =========================================================================
    # CHAPTER 5: THEY ARE ALREADY HERE (7 MISIONES)
    # =========================================================================
    {
        "id": "cult_01",
        "chapter_id": 5,
        "chapter_name": "Chapter 5: They Are Already Here",
        "title": "They Are Already Here - Eye of the World",
        "trader": "Mechanic",
        "map": "Customs",
        "level_req": 15,
        "briefing": (
            "Los Cultistas han dejado notas inquietantes sobre el 'Ojo del Mundo' en habitaciones marcadas de Customs y Reserve. "
            "Encuentra la nota ritual y descifra el significado de sus inscripciones en sangre."
        ),
        "objectives": [
            "Encontrar la 'Note about the Eye of the World' en la habitación marcada de Customs (314) o círculos de Woods",
            "Leer y analizar las profecías de la secta",
            "Consultar a Mechanic sobre los símbolos del Ojo del Mundo"
        ],
        "rewards": {"xp": 7800, "rep": "+0.03 Mechanic", "roubles": "50,000 ₽", "items": ["Vela Ritual", "Munición 9x39 SPP"]}
    },
    {
        "id": "cult_02",
        "chapter_id": 5,
        "chapter_name": "Chapter 5: They Are Already Here",
        "title": "They Are Already Here - The Torture House",
        "trader": "Mechanic",
        "map": "Lighthouse",
        "level_req": 18,
        "briefing": (
            "Los cultistas mantienen una casa de torturas y sacrificios en las montañas de Lighthouse. "
            "Infiltra la cabaña abandonada y busca evidencias de interrogatorios a operadores de TerraGroup."
        ),
        "objectives": [
            "Localizar la casa de torturas de los cultistas en Lighthouse",
            "Inspeccionar el sótano y las marcas rituales en las paredes",
            "Sobrevivir y extraer de Lighthouse"
        ],
        "rewards": {"xp": 8600, "rep": "+0.03 Mechanic", "roubles": "60,000 ₽", "items": ["Cuchillo Cultista Cultist Blade", "Morfina"]}
    },
    {
        "id": "cult_03",
        "chapter_id": 5,
        "chapter_name": "Chapter 5: They Are Already Here",
        "title": "They Are Already Here - The Victim's Audio Tapes",
        "trader": "Mechanic",
        "map": "Lighthouse",
        "level_req": 20,
        "briefing": (
            "Dentro de la casa de torturas hallaste la segunda cinta de audio grabada por una de las víctimas del culto. "
            "Escucha los sobrecogedores audios para localizar su departamento en Streets of Tarkov."
        ),
        "objectives": [
            "Recuperar y escuchar la segunda cinta de audio de la víctima en Lighthouse",
            "Extraer los datos sobre el paradero de su departamento en Streets",
            "Entregar informe a Mechanic"
        ],
        "rewards": {"xp": 9200, "rep": "+0.04 Mechanic", "roubles": "65,000 ₽", "items": ["Inyector Obdolbos", "Balas 5.45x39 BS"]}
    },
    {
        "id": "cult_04",
        "chapter_id": 5,
        "chapter_name": "Chapter 5: They Are Already Here",
        "title": "They Are Already Here - Streets Safehouse",
        "trader": "Mechanic",
        "map": "Streets of Tarkov",
        "level_req": 22,
        "briefing": (
            "El departamento de la víctima en Streets of Tarkov fue allanado por la secta. "
            "Consigue la llave de acceso, ingresa a la vivienda y recupera la primera cinta de audio original."
        ),
        "objectives": [
            "Conseguir la llave del departamento de la víctima en Streets of Tarkov",
            "Investigar el departamento y encontrar la primera cinta de audio",
            "Sobrevivir y extraer de Streets"
        ],
        "rewards": {"xp": 9800, "rep": "+0.04 Mechanic", "roubles": "72,000 ₽", "items": ["Moneda GP", "Auriculares Sordin"]}
    },
    {
        "id": "cult_05",
        "chapter_id": 5,
        "chapter_name": "Chapter 5: They Are Already Here",
        "title": "They Are Already Here - The Planted Grimoire",
        "trader": "Mechanic",
        "map": "Streets of Tarkov",
        "level_req": 24,
        "briefing": (
            "Los cultistas colocaron un libro apócrifo (Grimoire) en las pertenencias del científico Igor para incriminarlo. "
            "Recupera el tomo encuadernado y llévaselo a Mechanic para que descifre el lenguaje secreto."
        ),
        "objectives": [
            "Obtener y leer el libro que los cultistas plantaron en el departamento de Igor",
            "Consultar a Mechanic sobre los planes del Sacerdote Cultista",
            "Identificar el punto de reunión de la secta"
        ],
        "rewards": {"xp": 10500, "rep": "+0.04 Mechanic", "roubles": "80,000 ₽", "items": ["Libro Ritual Cultista", "Balas 7.62x54R SNB"]}
    },
    {
        "id": "cult_06",
        "chapter_id": 5,
        "chapter_name": "Chapter 5: They Are Already Here",
        "title": "They Are Already Here - Hunt the Cultist Priest",
        "trader": "Mechanic",
        "map": "Customs",
        "level_req": 26,
        "briefing": (
            "El líder de la secta, el temido Cultist Priest (Sacerdote), realiza ceremonias nocturnas. "
            "Cázalo en plena noche, elimina a sus discípulos armados con dagas envenenadas y recupera su nota secreta."
        ),
        "objectives": [
            "Localizar y neutralizar a un Cultist Priest en incursión nocturna",
            "Obtener la nota personal del Sacerdote Cultista",
            "Sobrevivir y extraer con la información ritual"
        ],
        "rewards": {"xp": 16000, "rep": "+0.06 Mechanic", "roubles": "140,000 ₽", "items": ["Daga Envenenada", "Armadura Hexgrid Clase 6"]}
    },
    {
        "id": "cult_07",
        "chapter_id": 5,
        "chapter_name": "Chapter 5: They Are Already Here",
        "title": "They Are Already Here - Station 14-4 Pass",
        "trader": "Mechanic",
        "map": "Lighthouse",
        "level_req": 28,
        "briefing": (
            "La nota del sacerdote apunta al chalet de montaña en Lighthouse marcado con el Ojo del Mundo. "
            "Registra la habitación cultista profanada y rescata el pase militar dañado 'Station 14-4 KORD Arshavin K.'."
        ),
        "objectives": [
            "Localizar el lugar marcado con el Ojo del Mundo en el chalet de Lighthouse",
            "Investigar la habitación oculta y rescatar las pertenencias de la víctima",
            "Encontrar el pase militar dañado 'Station 14-4 KORD Arshavin K.'",
            "Entregar el pase a Mechanic y desbloquear el logro: 'They Are Already Here'"
        ],
        "rewards": {"xp": 20000, "rep": "+0.08 Mechanic", "roubles": "180,000 ₽", "items": ["Pase Station 14-4", "Visor Nocturno GPNVG-18", "Logro de Campaña"]}
    },

    # =========================================================================
    # CHAPTER 6: THE UNHEARD (7 MISIONES)
    # =========================================================================
    {
        "id": "unheard_01",
        "chapter_id": 6,
        "chapter_name": "Chapter 6: The Unheard",
        "title": "The Unheard - The Purification Note",
        "trader": "Mechanic",
        "map": "Streets of Tarkov",
        "level_req": 18,
        "briefing": (
            "En la sala de videovigilancia del puesto de seguridad de TerraGroup en Streets of Tarkov (o en la oficina 4 de Ground Zero) "
            "apareció un perturbador manifiesto sobre la 'Purificación' inminente de toda la región."
        ),
        "objectives": [
            "Recoger y leer la nota con los delirios sobre la 'Purificación'",
            "Consultar a Mechanic para aprender sobre The Unheard",
            "Descubrir qué actividades secretas realizaba TerraGroup"
        ],
        "rewards": {"xp": 8200, "rep": "+0.03 Mechanic", "roubles": "55,000 ₽", "items": ["Memoria Flash", "Balas 5.56x45 M855A1"]}
    },
    {
        "id": "unheard_02",
        "chapter_id": 6,
        "chapter_name": "Chapter 6: The Unheard",
        "title": "The Unheard - Rzhevsky's Service Car",
        "trader": "Mechanic",
        "map": "Streets of Tarkov",
        "level_req": 20,
        "briefing": (
            "El jefe de seguridad Rzhevsky supervisó el cargamento de un catalizador combustible ultra secreto. "
            "Localiza su vehículo de servicio blindado en Streets of Tarkov y extrae el disco rígido de la consola."
        ),
        "objectives": [
            "Localizar el auto de servicio de Rzhevsky en Streets of Tarkov",
            "Extraer el disco rígido y los efectos personales de Rzhevsky",
            "Sobrevivir y extraer de Streets"
        ],
        "rewards": {"xp": 9000, "rep": "+0.04 Mechanic", "roubles": "65,000 ₽", "items": ["Disco Rígido Encriptado", "Fusil HK416A5"]}
    },
    {
        "id": "unheard_03",
        "chapter_id": 6,
        "chapter_name": "Chapter 6: The Unheard",
        "title": "The Unheard - Intercepted Transcript",
        "trader": "Mechanic",
        "map": "Hideout",
        "level_req": 22,
        "briefing": (
            "La transcripción de la última llamada de Rzhevsky menciona un envío de combustible con nombre clave 'Blue Ice'. "
            "Revisa los textos para rastrear los laboratorios donde se desarrollaba la investigación."
        ),
        "objectives": [
            "Leer la transcripción completa de la conversación de Rzhevsky",
            "Localizar los documentos sobre la investigación del catalizador 'Blue Ice'",
            "Identificar el rol del misterioso científico con iniciales 'A.P.'"
        ],
        "rewards": {"xp": 9600, "rep": "+0.04 Mechanic", "roubles": "70,000 ₽", "items": ["Placas de Blindaje Clase 5", "Monedas GP"]}
    },
    {
        "id": "unheard_04",
        "chapter_id": 6,
        "chapter_name": "Chapter 6: The Unheard",
        "title": "The Unheard - The Lab Infiltration",
        "trader": "Mechanic",
        "map": "The Lab",
        "level_req": 24,
        "briefing": (
            "Los servidores centrales de The Lab albergan las carpetas clasificadas de los directores de TerraGroup. "
            "Busca cualquier mención o archivo asignado al investigador 'A.P.'."
        ),
        "objectives": [
            "Ingresar a The Lab con tarjeta de acceso",
            "Buscar menciones de A.P. en los terminales de investigación",
            "Descubrir la habitación secreta que A.P. ocupaba en el Resort de Shoreline",
            "Sobrevivir y extraer de The Lab"
        ],
        "rewards": {"xp": 14000, "rep": "+0.05 Mechanic", "roubles": "110,000 ₽", "items": ["Tarjeta Keycard Negra", "Inyector Propital"]}
    },
    {
        "id": "unheard_05",
        "chapter_id": 6,
        "chapter_name": "Chapter 6: The Unheard",
        "title": "The Unheard - Health Resort Sanctuary",
        "trader": "Mechanic",
        "map": "Shoreline",
        "level_req": 26,
        "briefing": (
            "A.P. se atrincheró en una suite de lujo del balneario de Shoreline antes de escapar de la región. "
            "Consigue la llave de la habitación, penetra en el cuarto y recupera el dispositivo de almacenamiento masivo."
        ),
        "objectives": [
            "Localizar la habitación de A.P. en el Sanatorio de Shoreline",
            "Obtener el dispositivo de almacenamiento de datos de alta capacidad de A.P.",
            "Recuperar los efectos personales del científico",
            "Sobrevivir y extraer de Shoreline"
        ],
        "rewards": {"xp": 15000, "rep": "+0.05 Mechanic", "roubles": "125,000 ₽", "items": ["Dispositivo de Datos A.P.", "Armadura Crye AVS"]}
    },
    {
        "id": "unheard_06",
        "chapter_id": 6,
        "chapter_name": "Chapter 6: The Unheard",
        "title": "The Unheard - The 5M Decryption Protocol",
        "trader": "Mechanic",
        "map": "Refugio / Mechanic",
        "level_req": 28,
        "briefing": (
            "El pendrive de A.P. cuenta con un cifrado cuántico militar que bloquea cualquier intento de lectura. "
            "Mechanic puede contratar a los mejores hackers de la red clandestina si financias la operación con 5,000,000 de rublos."
        ),
        "objectives": [
            "Entregar el pendrive militar de A.P. a Mechanic",
            "Entregar 5,000,000 Roubles a Mechanic para costear el descifrado",
            "Aguardar las noticias del hacker Elektronik"
        ],
        "rewards": {"xp": 18000, "rep": "+0.06 Mechanic", "roubles": "Bitcoins x2", "items": ["Caja de Munición Militar", "Tarjeta Labs"]}
    },
    {
        "id": "unheard_07",
        "chapter_id": 6,
        "chapter_name": "Chapter 6: The Unheard",
        "title": "The Unheard - Technological Convergence",
        "trader": "Mechanic",
        "map": "Cualquier Mapa",
        "level_req": 30,
        "briefing": (
            "Elektronik ha descifrado los planes maestros de The Unheard. "
            "Integra los archivos tecnológicos en tu Centro de Inteligencia para revelar la conspiración de catalizadores y finalizar el capítulo."
        ),
        "objectives": [
            "Integrar los archivos descifrados de Elektronik en el refugio",
            "Descubrir los vínculos entre el combustible Blue Ice y el rompehielos Boreas",
            "Desbloquear el logro oficial: 'The Unheard'"
        ],
        "rewards": {"xp": 24000, "rep": "+0.08 Mechanic", "roubles": "200,000 ₽", "items": ["Rifle MCX SPEAR 6.8x51", "Logro: The Unheard"]}
    },

    # =========================================================================
    # CHAPTER 7: BLUE FIRE (6 MISIONES)
    # =========================================================================
    {
        "id": "blue_01",
        "chapter_id": 7,
        "chapter_name": "Chapter 7: Blue Fire",
        "title": "Blue Fire - The EMERCOM Leaflets",
        "trader": "Mechanic",
        "map": "Woods",
        "level_req": 16,
        "briefing": (
            "Folletos de evacuación de emergencia militar (EMERCOM) advierten sobre un pulso electromagnético masivo (EMP) "
            "que inutilizó las redes eléctricas de Tarkov. Encuentra un folleto en Woods, Interchange o en Chek 13 en Streets."
        ),
        "objectives": [
            "Leer un folleto de defensa civil EMERCOM en Woods, Interchange o Chek 13",
            "Consultar a Mechanic sobre el origen del estallido EMP",
            "Averiguar los efectos sobre los servidores de TerraGroup"
        ],
        "rewards": {"xp": 7200, "rep": "+0.03 Mechanic", "roubles": "45,000 ₽", "items": ["Batería Militar", "Cables"]}
    },
    {
        "id": "blue_02",
        "chapter_id": 7,
        "chapter_name": "Chapter 7: Blue Fire",
        "title": "Blue Fire - The EMP Blast Incident",
        "trader": "Mechanic",
        "map": "Customs",
        "level_req": 18,
        "briefing": (
            "Mechanic descubrió que el pulso electromagnético no fue un accidente, sino una detonación dirigida con el 'Dispositivo 1156'. "
            "Investiga el epicentro del pulso y recolecta fragmentos del generador de microondas."
        ),
        "objectives": [
            "Hablar con Mechanic sobre los componentes del dispositivo 1156",
            "Localizar y obtener el fragmento del dispositivo en Customs",
            "Entregar el fragmento a Mechanic"
        ],
        "rewards": {"xp": 8500, "rep": "+0.04 Mechanic", "roubles": "58,000 ₽", "items": ["Placas de Circuitos", "Relés"]}
    },
    {
        "id": "blue_03",
        "chapter_id": 7,
        "chapter_name": "Chapter 7: Blue Fire",
        "title": "Blue Fire - The Server Room Hack",
        "trader": "Mechanic",
        "map": "The Lab",
        "level_req": 20,
        "briefing": (
            "Para extraer los registros del pulso antes de que sean borrados, Mechanic te entrega un módulo de hackeo. "
            "Infiltra la sala de servidores en The Lab y conéctalo en el rack principal."
        ),
        "objectives": [
            "Llevar el módulo de hackeo a la sala de servidores de The Lab",
            "Plantar el dispositivo en el rack central de datos",
            "Sobrevivir y extraer de The Lab",
            "Reportar el éxito a Mechanic"
        ],
        "rewards": {"xp": 12500, "rep": "+0.05 Mechanic", "roubles": "95,000 ₽", "items": ["Tarjeta Gráfica GPU", "Moneda Bitcoin"]}
    },
    {
        "id": "blue_04",
        "chapter_id": 7,
        "chapter_name": "Chapter 7: Blue Fire",
        "title": "Blue Fire - The Fragment Dilemma",
        "trader": "Mechanic",
        "map": "Refugio / Mechanic",
        "level_req": 22,
        "briefing": (
            "Tras el hackeo recuperaste un núcleo secundario intacto del Ítem 1156. "
            "Puedes entregárselo a Mechanic para fabricar contramedidas o conservarlo para estudiar su tecnología."
        ),
        "objectives": [
            "Decidir si entregar el fragmento del Ítem 1156 a Mechanic o conservarlo",
            "Analizar las pistas sobre el envío de prototipos hacia la oficina de correos Rus Post"
        ],
        "rewards": {"xp": 9800, "rep": "+0.04 Mechanic", "roubles": "75,000 ₽", "items": ["Dispositivo 1156 Fragment", "Munición AP"]}
    },
    {
        "id": "blue_05",
        "chapter_id": 7,
        "chapter_name": "Chapter 7: Blue Fire",
        "title": "Blue Fire - Rus Post Central Office",
        "trader": "Mechanic",
        "map": "Streets of Tarkov",
        "level_req": 24,
        "briefing": (
            "La oficina central de correos Rus Post en Streets of Tarkov fue el centro de distribución clandestino del artefacto. "
            "Ingresa a las oficinas postales y busca el manifiesto de envío del vehículo de transporte."
        ),
        "objectives": [
            "Investigar la sucursal central de Rus Post en Streets of Tarkov",
            "Localizar los registros de despacho de encomiendas especiales",
            "Sobrevivir y extraer de Streets"
        ],
        "rewards": {"xp": 10500, "rep": "+0.04 Mechanic", "roubles": "80,000 ₽", "items": ["Llave de Rus Post", "Caja de Herramientas"]}
    },
    {
        "id": "blue_06",
        "chapter_id": 7,
        "chapter_name": "Chapter 7: Blue Fire",
        "title": "Blue Fire - The Rus Post Transport",
        "trader": "Mechanic",
        "map": "Streets of Tarkov",
        "level_req": 26,
        "briefing": (
            "El furgón blindado de Rus Post quedó varado en una intersección de Streets. "
            "Abre el compartimiento de carga, asegura el reactor Blue Fire y completa el capítulo."
        ),
        "objectives": [
            "Localizar el auto de transporte de Rus Post en Streets of Tarkov",
            "Extraer el núcleo del reactor Blue Fire del furgón",
            "Entregar el dispositivo a Mechanic y desbloquear el logro: 'Blue Fire'"
        ],
        "rewards": {"xp": 18000, "rep": "+0.07 Mechanic", "roubles": "160,000 ₽", "items": ["Núcleo Blue Fire", "Logro: Blue Fire"]}
    },

    # =========================================================================
    # CHAPTER 8: BOREAS (6 MISIONES)
    # =========================================================================
    {
        "id": "boreas_01",
        "chapter_id": 8,
        "chapter_name": "Chapter 8: Boreas",
        "title": "Boreas - Paradigm Shipping Signal",
        "trader": "Mechanic",
        "map": "Ground Zero",
        "level_req": 20,
        "briefing": (
            "En el edificio principal de TerraGroup en Ground Zero se encuentra el afiche publicitario de Paradigm Shipping "
            "con los planos del rompehielos nuclear 'Boreas', atrapado en el hielo del Golfo de Finlandia."
        ),
        "objectives": [
            "Encontrar el afiche de Paradigm Shipping en la sede de TerraGroup en Ground Zero (o tener Intel Center 3)",
            "Hablar con Mechanic sobre la posibilidad de escapar por vía marítima ártica",
            "Obtener las directivas de enlace radial"
        ],
        "rewards": {"xp": 8800, "rep": "+0.03 Mechanic", "roubles": "60,000 ₽", "items": ["Tarjeta de Acceso", "Radiobaliza Militar"]}
    },
    {
        "id": "boreas_02",
        "chapter_id": 8,
        "chapter_name": "Chapter 8: Boreas",
        "title": "Boreas - Repairing Woods Beacon",
        "trader": "Mechanic",
        "map": "Woods",
        "level_req": 22,
        "briefing": (
            "La torre de comunicaciones cerca del búnker Scav en Woods tiene la antena necesaria para sintonizar el transpondedor del Boreas. "
            "Lleva un juego de herramientas (Toolset) y repara la consola bajo la torre."
        ),
        "objectives": [
            "Llevar un Toolset a la torre de radio cerca del Scav Bunker en Woods",
            "Reparar el equipo de transmisión bajo la torre",
            "Sobrevivir y extraer de Woods"
        ],
        "rewards": {"xp": 9400, "rep": "+0.04 Mechanic", "roubles": "65,000 ₽", "items": ["Toolset", "Batería Militar"]}
    },
    {
        "id": "boreas_03",
        "chapter_id": 8,
        "chapter_name": "Chapter 8: Boreas",
        "title": "Boreas - AMG-10 Hydraulic Fluid",
        "trader": "Prapor",
        "map": "Reserve",
        "level_req": 24,
        "briefing": (
            "Para reparar las turbinas del aerodeslizador de rescate que te llevará al buque, "
            "debes buscar bidones de fluido hidráulico militar de aviación AMG-10 en los sótanos de Reserve."
        ),
        "objectives": [
            "Infiltrarse en el sótano del edificio Black Bishop y hangares de Reserve",
            "Encontrar y extraer 2 bidones de fluido hidráulico AMG-10",
            "Sobrevivir y extraer de Reserve"
        ],
        "rewards": {"xp": 10500, "rep": "+0.04 Prapor", "roubles": "75,000 ₽", "items": ["Fluido AMG-10", "Filtro Militar"]}
    },
    {
        "id": "boreas_04",
        "chapter_id": 8,
        "chapter_name": "Chapter 8: Boreas",
        "title": "Boreas - BTR Transit Deal",
        "trader": "BTR Driver",
        "map": "Streets of Tarkov",
        "level_req": 26,
        "briefing": (
            "El conductor del blindado BTR conoce las rutas costeras y el acceso a los muelles del norte. "
            "Negocia el salvoconducto transportando suministros pesados o cumpliendo los requisitos de Skier."
        ),
        "objectives": [
            "Contactar al conductor del BTR en Streets of Tarkov o Woods",
            "Entregar los pagos o municiones de 7.62x54mm BT requeridas",
            "Asegurar el corredor hacia el embarcadero de Shoreline"
        ],
        "rewards": {"xp": 12000, "rep": "+0.05 BTR Driver", "roubles": "90,000 ₽", "items": ["Pase del BTR", "Mochila Attack 2"]}
    },
    {
        "id": "boreas_05",
        "chapter_id": 8,
        "chapter_name": "Chapter 8: Boreas",
        "title": "Boreas - Hovercraft Extraction Pier",
        "trader": "Peacekeeper",
        "map": "Shoreline",
        "level_req": 28,
        "briefing": (
            "El aerodeslizador táctico aguarda en el muelle de Shoreline. "
            "Paga la tarifa de transporte de 400,000 Roubles al timonel para abordar y zarpar hacia el buque Boreas."
        ),
        "objectives": [
            "Llegar al muelle de Shoreline con 400,000 Roubles",
            "Activar el tránsito marítimo del aerodeslizador",
            "Desbloquear el acceso oficial al mapa Icebreaker (Boreas)"
        ],
        "rewards": {"xp": 16000, "rep": "+0.06 Peacekeeper", "roubles": "$ 1,200 USD", "items": ["Keycard de Boreas", "Visor Térmico"]}
    },
    {
        "id": "boreas_06",
        "chapter_id": 8,
        "chapter_name": "Chapter 8: Boreas",
        "title": "Boreas - Boarding The Nuclear Icebreaker",
        "trader": "Mechanic",
        "map": "Icebreaker",
        "level_req": 30,
        "briefing": (
            "¡A bordo del Boreas! Navega por los 14 niveles del rompehielos nuclear, desde las cubiertas heladas "
            "hasta la sala de reactores y el helipuerto, enfrentando al temible boss 'The Wedge' y su escuadrón Black Division."
        ),
        "objectives": [
            "Infiltrarse en el buque Boreas (Mapa Icebreaker)",
            "Llegar al puente de mando (Nivel 9) y sala de reactores (Nivel -2)",
            "Sobrevivir al combate y extraer en helicóptero",
            "Desbloquear el logro oficial: 'Boreas'"
        ],
        "rewards": {"xp": 25000, "rep": "+0.08 Mechanic", "roubles": "250,000 ₽", "items": ["Fusil MCX SPEAR", "Placas Black Division", "Logro: Boreas"]}
    },

    # =========================================================================
    # CHAPTER 9: THE TICKET (6 MISIONES)
    # =========================================================================
    {
        "id": "ticket_01",
        "chapter_id": 9,
        "chapter_name": "Chapter 9: The Ticket",
        "title": "The Ticket - Encrypted Contact with Mr. Kerman",
        "trader": "Fence",
        "map": "Refugio",
        "level_req": 25,
        "briefing": (
            "A través de la laptop de tu Centro de Inteligencia recibes una transmisión secreta de Mr. Kerman, "
            "el operador en las sombras que controla las rutas finales de extracción fuera del territorio de Tarkov."
        ),
        "objectives": [
            "Poseer Centro de Inteligencia Nivel 1 en el refugio",
            "Establecer comunicación cifrada con Mr. Kerman en la laptop",
            "Aceptar las condiciones preliminares para la obtención del 'Ticket'"
        ],
        "rewards": {"xp": 9500, "rep": "+0.04 Fence", "roubles": "70,000 ₽", "items": ["Laptop Táctica", "Moneda Bitcoin"]}
    },
    {
        "id": "ticket_02",
        "chapter_id": 9,
        "chapter_name": "Chapter 9: The Ticket",
        "title": "The Ticket - Prapor's Hidden Camp",
        "trader": "Prapor",
        "map": "Lighthouse",
        "level_req": 26,
        "briefing": (
            "Si entregaste el maletín en Falling Skies, viaja a las colinas del sur de Lighthouse donde acampan "
            "los comandos de Prapor para recuperar la nota con las claves del candado biométrico."
        ),
        "objectives": [
            "Viajar a Lighthouse y localizar el campamento de Prapor en la colina sur",
            "Recuperar la nota con las secuencias del candado del maletín",
            "Sobrevivir y extraer de Lighthouse"
        ],
        "rewards": {"xp": 10500, "rep": "+0.04 Prapor", "roubles": "80,000 ₽", "items": ["Balas 7.62x51 M62", "Inyector Propital"]}
    },
    {
        "id": "ticket_03",
        "chapter_id": 9,
        "chapter_name": "Chapter 9: The Ticket",
        "title": "The Ticket - Experimental Signal Jammer",
        "trader": "Mechanic",
        "map": "The Lab",
        "level_req": 28,
        "briefing": (
            "Para abrir el maletín de titanio sin detonar su carga destructiva de autodestrucción, "
            "debes ingresar al sector de pruebas de armamento de The Lab y obtener el inhibidor de señal experimental."
        ),
        "objectives": [
            "Infiltrarse en el área de pruebas de armamento de The Lab",
            "Obtener el Experimental Signal Jammer",
            "Sobrevivir y extraer de The Lab"
        ],
        "rewards": {"xp": 14000, "rep": "+0.05 Mechanic", "roubles": "110,000 ₽", "items": ["Inhibidor de Señal", "Tarjeta de Acceso"]}
    },
    {
        "id": "ticket_04",
        "chapter_id": 9,
        "chapter_name": "Chapter 9: The Ticket",
        "title": "The Ticket - Cracking Kruglov's Safe",
        "trader": "Mechanic",
        "map": "Refugio / Mechanic",
        "level_req": 30,
        "briefing": (
            "Con el inhibidor activado, abres el maletín blindado y descubres la tarjeta RFID personal del Dr. Kruglov: "
            "el legendario 'Ticket' que permite el paso autorizado por los puestos fronterizos de la Federación Rusa y la ONU."
        ),
        "objectives": [
            "Vincular el inhibidor y desbloquear el maletín blindado",
            "Obtener la tarjeta RFID de Kruglov ('The Ticket')",
            "Revisar las ofertas de evacuación de Mr. Kerman"
        ],
        "rewards": {"xp": 18000, "rep": "+0.06 Mechanic", "roubles": "150,000 ₽", "items": ["Tarjeta RFID 'Ticket'", "Maletín T.H.I.C.C."]}
    },
    {
        "id": "ticket_05",
        "chapter_id": 9,
        "chapter_name": "Chapter 9: The Ticket",
        "title": "The Ticket - The Four Endings Branch",
        "trader": "Mr. Kerman",
        "map": "Refugio",
        "level_req": 32,
        "briefing": (
            "Llegas a la encrucijada definitiva. Las condiciones de Mr. Kerman definen tu final en Escape from Tarkov: "
            "1. Survivor (Huir en solitario con tu fortuna) | 2. Savior (Rescatar a los civiles y entregar las pruebas) | "
            "3. Fallen (Enfrentar a las fuerzas de asedio) | 4. Debtor (Saldar tu condena trabajando para las sombras)."
        ),
        "objectives": [
            "Evaluar los cuatro caminos narrativos con Mr. Kerman",
            "Seleccionar tu destino final de escape",
            "Preparar el equipamiento para la extracción en la Terminal del Puerto"
        ],
        "rewards": {"xp": 22000, "rep": "+0.08 Global", "roubles": "200,000 ₽", "items": ["Pase de Evacuación", "Equipamiento de Élite"]}
    },
    {
        "id": "ticket_06",
        "chapter_id": 9,
        "chapter_name": "Chapter 9: The Ticket",
        "title": "The Ticket - Final Terminal Extraction",
        "trader": "Mr. Kerman",
        "map": "Port Terminal",
        "level_req": 35,
        "briefing": (
            "La misión cumbre de Escape from Tarkov: llegar a la Terminal del Puerto, insertar la tarjeta RFID en el lector blindado, "
            "repeler la última oleada de enemigos y escapar definitivamente de la zona de exclusión de Norvinsk."
        ),
        "objectives": [
            "Alcanzar las compuertas de la Terminal del Puerto",
            "Insertar la tarjeta RFID 'Ticket' en la consola principal",
            "Sobrevivir al asedio de extracción final",
            "¡Escapar de Tarkov y completar la campaña!"
        ],
        "rewards": {"xp": 50000, "rep": "+1.00 Corona", "roubles": "1,000,000 ₽", "items": ["Contenedor Seguro Kappa", "Trofeo de Escape", "Logro de Campaña: Escape from Tarkov"]}
    },

    # =========================================================================
    # CHAPTER 10: THE LABYRINTH (6 MISIONES)
    # =========================================================================
    {
        "id": "laby_01",
        "chapter_id": 10,
        "chapter_name": "Chapter 10: The Labyrinth",
        "title": "The Labyrinth - Knossos Facility Secrets",
        "trader": "Jaeger",
        "map": "Shoreline",
        "level_req": 25,
        "briefing": (
            "En el sótano inundado del complejo balneario de Shoreline existe una compuerta sellada con el logo de Knossos LLC. "
            "Pregunta a Therapist y Jaeger sobre la instalación experimental subterránea conocida como 'El Laberinto'."
        ),
        "objectives": [
            "Localizar la compuerta blindada de Knossos LLC en el sótano del Resort de Shoreline",
            "Preguntar a Therapist y Jaeger cómo acceder a la instalación subterránea",
            "Sobrevivir y extraer de Shoreline"
        ],
        "rewards": {"xp": 9500, "rep": "+0.04 Jaeger", "roubles": "70,000 ₽", "items": ["Llave de Sótano", "Balas .338 Lapua"]}
    },
    {
        "id": "laby_02",
        "chapter_id": 10,
        "chapter_name": "Chapter 10: The Labyrinth",
        "title": "The Labyrinth - Jaeger's Keycards Gathering",
        "trader": "Jaeger",
        "map": "Cualquier Mapa",
        "level_req": 27,
        "briefing": (
            "Para abrir las esclusas herméticas del Laberinto necesitas llaves maestras especiales: "
            "la llave con el símbolo de Ariadna (Ariadne Symbol Key) y las tarjetas de acceso a la morgue de científicos."
        ),
        "objectives": [
            "Esperar a que Jaeger reúna las tarjetas de acceso o encontrarlas en Scavs",
            "Obtener la 'Ariadne Symbol Key' para abrir las rutas secundarias del búnker",
            "Conseguir las llaves de las cámaras de descontaminación"
        ],
        "rewards": {"xp": 11000, "rep": "+0.04 Jaeger", "roubles": "85,000 ₽", "items": ["Ariadne Symbol Key", "Inyector Zagustin"]}
    },
    {
        "id": "laby_03",
        "chapter_id": 10,
        "chapter_name": "Chapter 10: The Labyrinth",
        "title": "The Labyrinth - Infiltrating the Beast's Lair",
        "trader": "Jaeger",
        "map": "Labyrinth",
        "level_req": 30,
        "briefing": (
            "Ingresa al mapa Labyrinth (110x110m de pasillos claustrofóbicos, trampas de gas y foso de púas). "
            "Localiza los rastros del escuadrón BEAR masacrado y enfrenta las sombras del boss Vengeful Killa y Tagilla."
        ),
        "objectives": [
            "Ingresar a la instalación subterránea de The Labyrinth",
            "Localizar las huellas y los cuerpos caídos del escuadrón BEAR",
            "Evitar las trampas de púas venenosas y pozos tóxicos",
            "Sobrevivir al encuentro inicial"
        ],
        "rewards": {"xp": 15000, "rep": "+0.05 Jaeger", "roubles": "110,000 ₽", "items": ["Antídoto XTG-12", "Armadura Pesada Clase 5"]}
    },
    {
        "id": "laby_04",
        "chapter_id": 10,
        "chapter_name": "Chapter 10: The Labyrinth",
        "title": "The Labyrinth - The Observation Room",
        "trader": "Jaeger",
        "map": "Labyrinth",
        "level_req": 32,
        "briefing": (
            "En el centro del laberinto se encuentra la sala de observación acorazada donde los científicos observaban los experimentos humanos. "
            "Entra al despacho sellado, activa el reproductor de bobina abierta y escucha el mensaje póstumo del director científico."
        ),
        "objectives": [
            "Acceder a la oficina de observación bloqueada en The Labyrinth",
            "Recuperar y escuchar la cinta de audio del científico jefe",
            "Localizar las notas de investigación de Labrys sobre las pizarras"
        ],
        "rewards": {"xp": 18000, "rep": "+0.06 Jaeger", "roubles": "140,000 ₽", "items": ["Cinta de Audio de Científico", "Notas de Labrys"]}
    },
    {
        "id": "laby_05",
        "chapter_id": 10,
        "chapter_name": "Chapter 10: The Labyrinth",
        "title": "The Labyrinth - Delivering the Horrors",
        "trader": "Jaeger",
        "map": "Labyrinth",
        "level_req": 34,
        "briefing": (
            "Debes salir con vida del Laberinto utilizando la extracción 'The Way Up' o la ruta oculta 'Ariadne's Path'. "
            "Lleva la cinta magnética y las muestras biológicas directamente a Jaeger."
        ),
        "objectives": [
            "Extraer de The Labyrinth a través de 'The Way Up' o 'Ariadne's Path'",
            "Entregar la cinta de audio del científico a Jaeger",
            "Confirmar la aniquilación de los sujetos experimentales mutados"
        ],
        "rewards": {"xp": 22000, "rep": "+0.07 Jaeger", "roubles": "180,000 ₽", "items": ["Fusil AXMC .338 Lapua", "Balas AP-20"]}
    },
    {
        "id": "laby_06",
        "chapter_id": 10,
        "chapter_name": "Chapter 10: The Labyrinth",
        "title": "The Labyrinth - Research Report 0.7",
        "trader": "Jaeger",
        "map": "Shoreline / Refugio",
        "level_req": 36,
        "briefing": (
            "Culminación del capítulo: lee el informe de investigación clasificado de la instalación de Knossos LLC. "
            "Revela la verdad sobre el 'Minotauro de Tarkov' y sella para siempre la entrada subterránea."
        ),
        "objectives": [
            "Leer el informe de investigación completo 'Labyrinth Facility Research Report 0.7'",
            "Sellar los accesos subterráneos desde el emisario de Shoreline",
            "Desbloquear el logro oficial: 'Theseus' y completar la trama de The Labyrinth"
        ],
        "rewards": {"xp": 30000, "rep": "+0.10 Jaeger", "roubles": "300,000 ₽", "items": ["Piolet Red Rebel", "Logro: Theseus", "Caja T.H.I.C.C. Items"]}
    }
]


def get_all_storyline_quests() -> List[Dict[str, Any]]:
    """Retorna la lista completa de las 71 misiones principales de la historia."""
    return list(STORYLINE_QUESTS_DATA)


def get_storyline_quests_by_chapter(chapter_id: int) -> List[Dict[str, Any]]:
    """Retorna las misiones pertenecientes a un capítulo específico (1 al 10)."""
    if chapter_id <= 0:
        return get_all_storyline_quests()
    return [q for q in STORYLINE_QUESTS_DATA if q.get("chapter_id") == chapter_id]


_WIKI_CHAPTERS_CACHE: List[Dict[str, Any]] = []


def get_wiki_story_chapters_full() -> List[Dict[str, Any]]:
    """
    Carga y retorna la base de datos completa de los 10 Capítulos de la Historia de la Wiki Oficial
    (con Requirements, Objectives, Guide paso a paso, Related Quest Items, Gallery y Rewards).
    """
    global _WIKI_CHAPTERS_CACHE
    if _WIKI_CHAPTERS_CACHE:
        return _WIKI_CHAPTERS_CACHE

    import json
    import os
    import sys
    from core.config import DATA_DIR, BUNDLE_DIR

    for base_d in (DATA_DIR, os.path.join(BUNDLE_DIR, "data")):
        json_path = os.path.join(base_d, "wiki_story_chapters_full.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    _WIKI_CHAPTERS_CACHE = json.load(f)
                    return _WIKI_CHAPTERS_CACHE
            except Exception:
                pass
    return []


def get_wiki_story_chapter(chapter_number: int) -> Dict[str, Any]:
    """Retorna el diccionario completo de un capítulo específico (1 a 10)."""
    for ch in get_wiki_story_chapters_full():
        if ch.get("chapter_number") == chapter_number:
            return ch
    chapters = get_wiki_story_chapters_full()
    return chapters[0] if chapters else {}

