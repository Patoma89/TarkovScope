"""
TarkovScope - Base de Conocimiento del Universo y Lore de Escape from Tarkov
Cronología oficial de la región de Norvinsk, facciones (BEAR, USEC, TerraGroup,
Black Division, Scavs, Cultistas), trasfondo de comerciantes, jefes (Bosses),
proyectos clasificados y series canónicas (Raid & Chronicles of Ryzhy).
"""
from typing import Any, Dict, List


LORE_UNIVERSE_SECTIONS: List[Dict[str, Any]] = [
    {
        "id": 101,
        "short_title": "Cronología de Norvinsk",
        "title": "01. Cronología Completa de Norvinsk (2008 – Presente)",
        "subtitle_es": "Desde la Zona Económica Especial hasta el Bloqueo Militar Total",
        "date_str": "Línea Temporal Oficial — Contract Wars → Escape from Tarkov",
        "accent": "#38BDF8",
        "highlights": [
            ("2008 – 2010", "Creación de la Zona Económica Especial (ZEE) de Norvinsk con exenciones aduaneras entre Rusia y la UE."),
            ("2012 – 2014", "TerraGroup Labs se instala en Tarkov y compra búnkeres militares soviéticos bajo fachada biotecnológica."),
            ("2015", "Estalla el escándalo político y la Guerra de los Contratos (Contract Wars) entre USEC y BEAR."),
            ("Apagón EMP", "Detonación del Objeto #1156 ('Blue Fire'): colapsan redes eléctricas, radares y comunicaciones."),
            ("Cuarentena", "La ONU y las Fuerzas Armadas Rusas sellan Norvinsk; comienza Escape from Tarkov."),
        ],
        "narrative_es": (
            "La historia de Escape from Tarkov comienza mucho antes del primer disparo en Ground Zero. A finales de la década de 2000, "
            "la ciudad portuaria de Tarkov —situada en la región ficticia de Norvinsk, al noroeste de Rusia cerca de la frontera con Finlandia— "
            "fue designada como Zona Económica Especial (ZEE) para atraer capital europeo y modernizar el comercio báltico.\n\n"
            "El conglomerado multinacional TerraGroup Inc., a través de su división científica TerraGroup Labs, aprovechó los privilegios fiscales "
            "y una red de sobornos a funcionarios locales para adquirir complejos industriales, hospitales y antiguos búnkeres militares soviéticos "
            "(como los de Reserve y el subsuelo de Shoreline). Oficialmente desarrollaban fármacos y tecnología agrícola; en secreto, ejecutaban "
            "experimentos neuroquímicos, armamento biológico y síntesis de estimulantes militares.\n\n"
            "Cuando las agencias de inteligencia rusas intentaron auditar las instalaciones, TerraGroup contrató a la PMC occidental USEC para bloquear "
            "el acceso y destruir archivos comprometedores. En respuesta, el gobierno ruso autorizó en secreto la creación de BEAR para infiltrarse en "
            "Tarkov y recuperar la evidencia sin involucrar oficialmente al ejército regular. Lo que empezó como escaramuzas encubiertas escaló a las "
            "llamadas 'Contract Wars' (la guerra abierta entre PMC).\n\n"
            "El punto de no retorno ocurrió cuando un dispositivo electromagnético experimental ('Blue Fire' / Objeto #1156) dejó a toda la provincia "
            "sin electricidad ni comunicaciones satelitales. Aprovechando el caos, la ONU y las Fuerzas Armadas Rusas levantaron un perímetro militar "
            "infranqueable alrededor de Norvinsk, atrapando a civiles, operadores de PMC abandonados por sus mandos y bandas armadas que dieron origen "
            "al conflicto actual."
        ),
    },
    {
        "id": 102,
        "short_title": "Facciones y Actores",
        "title": "02. Facciones Armadas y Actores de Tarkov",
        "subtitle_es": "BEAR, USEC, TerraGroup, Black Division, Scavs, Raiders, Rogues y Cultistas",
        "date_str": "Orden de Batalla Regional",
        "accent": "#10B981",
        "highlights": [
            ("BEAR", "Battle Encounter Assault Regiment: fuerza paramilitar rusa creada por decreto secreto para investigar a TerraGroup."),
            ("USEC", "United Security: PMC angloamericana formada por veteranos occidentales para proteger activos de TerraGroup."),
            ("Black Division", "Unidad de operaciones negras de élite al servicio directo de la cúpula de TerraGroup para 'limpiar' testigos."),
            ("Scavs / Raiders", "Civiles saqueadores ('Dikie') y ex-operadores militares armados que custodian Labs y Reserve."),
            ("Rogues", "Ex-operadores USEC desertores que tomaron la Planta de Tratamiento de Agua en Lighthouse."),
            ("Cultistas", "Secta apocalíptica nocturna ('El Ojo del Mundo') armada con dagas envenenadas."),
        ],
        "narrative_es": (
            "• BEAR (Battle Encounter Assault Regiment): Fundada en secreto mediante un decreto del gobierno ruso, recluta exclusivamente ex-soldados "
            "de fuerzas especiales (Spetsnaz, VDV, Alpha). Su objetivo original era capturar pruebas físicas de los crímenes de TerraGroup; tras el "
            "bloqueo, sus unidades quedaron aisladas y luchan por sobrevivir y escapar.\n\n"
            "• USEC (United Security): Nacida de la fusión de dos contratistas militares privados occidentales, fue contratada por TerraGroup para "
            "proteger sus laboratorios y silenciar a investigadores disidentes. Al colapsar la cadena de mando corporativa, muchos USEC fueron "
            "abandonados a su suerte, mientras que otros desertaron.\n\n"
            "• Black Division: El brazo armado clandestino de más alto nivel dentro de TerraGroup. No responden ante los mandos regulares de USEC "
            "y su misión es eliminar cualquier evidencia, servidor o sobreviviente (incluidos empleados propios) en lugares críticos como The Lab, "
            "el rompehielos Boreas y la Terminal.\n\n"
            "• Scavs, Scav Raiders y Rogues: Los Scavs ('Dikie', salvajes) son residentes locales que formaron pandillas para saquear la ciudad "
            "tras la evacuación fallida. Los Raiders son ex-militares y ex-PMC altamente equipados que operan en The Lab y los búnkeres de Reserve. "
            "Los Rogues son un grupo desertor de USEC que se atrincheró en la planta potabilizadora de Lighthouse y mantiene treguas tensas con Scavs.\n\n"
            "• Cultistas (El Ojo del Mundo): Una secta religiosa extremista que opera únicamente de noche (22:00 a 06:00). Creen que el colapso de "
            "Tarkov es una purificación sagrada y marcan círculos rituales en Woods, Customs, Shoreline y Reserve."
        ),
    },
    {
        "id": 103,
        "short_title": "Comerciantes y Ocultos",
        "title": "03. Comerciantes y Figuras en la Sombra",
        "subtitle_es": "Quién controla realmente el mercado negro, la información y las salidas de Norvinsk",
        "date_str": "Red Clandestina de Tarkov",
        "accent": "#EAB308",
        "highlights": [
            ("Prapor & Therapist", "El oficial de suministros del bloque militar ruso y la médica jefa del Hospital Central que protege a civiles."),
            ("Fence", "El intermediario anónimo que coordina la red de Scavs y el karma en las sombras."),
            ("Peacekeeper", "Oficial de suministros de la ONU que vende armamento OTAN a cambio de inteligencia y dólares."),
            ("Lightkeeper", "El enigmático guardián de la Isla del Faro; decide quién vive, quién negocia y quién cruza Norvinsk."),
            ("Mr. Kerman", "Bróker de datos y hacker maestro que busca exponer los crímenes de TerraGroup al mundo."),
        ],
        "narrative_es": (
            "Los comerciantes de Tarkov no son simples vendedores: representan los engranajes políticos y criminales que mantienen viva la zona "
            "de exclusión.\n\n"
            "• Prapor (Pavel Yegorovich): Suboficial encargado de los depósitos militares soviéticos en Norvinsk. Suministra armamento ruso a "
            "cambio de favores y mantiene vínculos directos con la guarnición militar que custodia la Terminal.\n\n"
            "• Therapist (Elvira Khabibullina): Jefa del departamento de trauma del Hospital Central de Tarkov. Es una de las pocas figuras "
            "genuinamente preocupadas por los civiles atrapados, aunque no duda en financiar operaciones armadas para investigar experimentos.\n\n"
            "• Skier (Alexander Kiselyov) & Ragman (Abramyan Arshavir): Skier controla el contrabando portuario y las bandas de Customs; Ragman "
            "dirigía el centro comercial Ultra (Interchange) antes de la caída y hoy domina el comercio de blindajes y equipamiento táctico.\n\n"
            "• Peacekeeper (Tadeusz Pilsudski): Oficial de logística del contingente de paz de la ONU en Shoreline. Utiliza el bloqueo como "
            "negocio personal y fuente de inteligencia occidental.\n\n"
            "• Mechanic (Sergey Samoylov) & Jaeger (Kharitonov): Mechanic es un genio técnico obsesionado con los servidores de TerraGroup y la "
            "ingeniería de armas; Jaeger es un guardabosques veterano que vigila Priozersk (Woods) y desprecia el saqueo indiscriminado.\n\n"
            "• Lightkeeper & Mr. Kerman: Lightkeeper habita el faro aislado de Lighthouse protegido por Zryachiy y campos minados; actúa como "
            "árbitro supremo entre facciones. Mr. Kerman, por su parte, opera desde las sombras digitales intentando reunir las pruebas finales "
            "contra TerraGroup."
        ),
    },
    {
        "id": 104,
        "short_title": "Lore de los Bosses",
        "title": "04. Historia de los Jefes (Bosses) de Norvinsk",
        "subtitle_es": "Los señores de la guerra que dominan cada sector de la ciudad sitiada",
        "date_str": "Dossier de Inteligencia Táctica",
        "accent": "#EF4444",
        "highlights": [
            ("Reshala", "El 'Dealmaker': capo local que controla los dormitorios de Customs y negocia con Skier y TerraGroup."),
            ("Killa & Tagilla", "Hermanos ex-atletas/trabajadores: Killa tomó el Mall Ultra (Interchange) y Tagilla la planta química de Factory."),
            ("Sanitar", "Ex-médico e investigador de TerraGroup Labs que experimenta con estimulantes en el Health Resort de Shoreline."),
            ("Kaban & Kollontay", "Kaban es un ex-empresario mafioso en Streets; Kollontay es un ex-oficial corrupto de la policía MVD."),
            ("The Goons", "Knight, Big Pipe y Birdeye: escuadrón desertor de élite que caza operadores entre mapas."),
            ("Zryachiy & Partisan", "Zryachiy custodia el Faro de Lightkeeper; Partisan caza a operadores con bajo karma en los bosques."),
        ],
        "narrative_es": (
            "Cada mapa de Tarkov cayó bajo el control de figuras brutales con historias entrelazadas:\n\n"
            "• Reshala: Antiguo empresario criminal convertido en el principal intermediario de contrabando en Customs. Sus cuatro guardias "
            "(los hermanos Zavodskoy) protegen sus rutas entre Dorms y la estación de servicio.\n\n"
            "• Killa y Tagilla: Hermanos unidos por una violencia implacable. Killa se apropió del centro comercial Ultra (Interchange) "
            "armado con su RPK-16 y casco Maska; Tagilla domina los túneles industriales de Factory con su mazo de soldador y máscara de acero.\n\n"
            "• Sanitar: Antiguo científico médico de TerraGroup que quedó atrapado en Shoreline. Adicto a sus propios cócteles experimentales, "
            "usa el Health Resort y los muelles como laboratorio improvisado.\n\n"
            "• Glukhar y Shturman: Glukhar es un ex-oficial naval disciplinado que tomó la base militar de Reserve con seis guardias tácticos; "
            "Shturman es el francotirador que controla el aserradero de Woods y custodia cajas fuertes de contrabando.\n\n"
            "• Kaban y Kollontay (Streets of Tarkov): Kaban fortificó el concesionario LexOs con ametralladoras pesadas; Kollontay, antiguo "
            "oficial antidisturbios del Ministerio del Interior (MVD), gobierna la Academia MVD y el centro comercial Klimov.\n\n"
            "• The Goons, Zryachiy y Partisan: Knight, Big Pipe y Birdeye formaban parte de operaciones especiales occidentales antes de "
            "desertar. Zryachiy es el francotirador silencioso del faro al servicio de Lightkeeper, mientras que Partisan actúa como un "
            "cazador solitario que castiga a quienes rompen el código moral del campo de batalla."
        ),
    },
    {
        "id": 105,
        "short_title": "Proyectos TerraGroup",
        "title": "05. Proyectos Clasificados de TerraGroup",
        "subtitle_es": "Project 62, The Lab, Knossos LLC (The Labyrinth) y el Objeto #1156",
        "date_str": "Archivos Desclasificados",
        "accent": "#A855F7",
        "highlights": [
            ("Project 62", "Programa bioquímico de estimulantes de combate (SJ1, SJ6, M.U.L.E., Obdolbos) con severos efectos secundarios."),
            ("The Lab", "Complejo subterráneo secreto bajo el centro de Tarkov donde se realizaban pruebas químicas y de armamento."),
            ("Knossos LLC", "Instalación 'The Labyrinth' bajo el Health Resort de Shoreline dedicada a pruebas psicológicas extremas."),
            ("Objeto #1156", "Dispositivo EMP ('Blue Fire') que aisló electrónicamente a toda la región de Norvinsk."),
        ],
        "narrative_es": (
            "El motor oculto detrás de toda la guerra en Tarkov es la tecnología ilegal desarrollada por TerraGroup Labs:\n\n"
            "• The Lab y Project 62: Bajo las calles céntricas se construyó un búnker científico autosuficiente. Allí se sintetizaron "
            "los estimulantes de combate capaces de anular el dolor, multiplicar la resistencia y alterar la coagulación sanguínea, aunque "
            "provocando adicción extrema, fallos orgánicos y psicosis en sujetos de prueba.\n\n"
            "• Knossos LLC (The Labyrinth): Situado bajo el ala oeste del balneario Health Resort en Shoreline, fue disfrazado como un club "
            "recreativo privado para ejecutivos. En realidad albergaba cámaras de estrés letal y experimentos conductuales extremos.\n\n"
            "• Paradigm Shipping & Boreas: Para evacuar sus servidores cuando el bloqueo se cerró, TerraGroup usó la naviera fantasma "
            "Paradigm Shipping y el rompehielos nuclear Boreas en la costa ártica, operación que terminó en masacre a bordo.\n\n"
            "• Objeto #1156 ('Blue Fire'): El arma de pulso electromagnético diseñada para borrar rastros digitales y cortar la comunicación "
            "de Norvinsk con el resto del mundo durante la fase final de limpieza."
        ),
    },
    {
        "id": 106,
        "short_title": "Raid & Ryzhy",
        "title": "06. Series Canónicas: 'Raid' y 'Chronicles of Ryzhy'",
        "subtitle_es": "Las historias audiovisuales oficiales integradas en el canon de Tarkov",
        "date_str": "Canon Cinematográfico BSG",
        "accent": "#EC4899",
        "highlights": [
            ("Raid (Skif y Mike)", "Un escuadrón BEAR liderado por Skif se ve forzado a colaborar con el USEC Mike para recuperar un maletín de TerraGroup."),
            ("La Traición", "Tras sobrevivir al asedio de Factory y los Scavs, Black Division ejecuta una emboscada para eliminar testigos."),
            ("Chronicles of Ryzhy", "Sigue a un Scav excéntrico llamado Ryzhy atrapado en los juegos de los Cultistas, Arena y el submundo de Tarkov."),
        ],
        "narrative_es": (
            "Battlestate Games expandió el universo de Tarkov mediante dos series live-action oficiales que conectan directamente con el juego:\n\n"
            "• Escape from Tarkov: Raid: Relata la misión de un pequeño grupo de operadores BEAR (entre ellos Skif y su escuadrón) enviados a "
            "recuperar un contenedor blindado de TerraGroup. Aislados y perseguidos tanto por Scavs armados como por unidades USEC, Skif "
            "termina formando una alianza improbable con Mike, un operador USEC herido.\n\n"
            "Tras abrirse paso por las instalaciones industriales de Factory y derrotar a oleadas enemigas, la serie muestra la crudeza real "
            "del conflicto: incluso cuando cumplen la misión, fuerzas superiores de limpieza (Black Division) intervienen para asegurarse de "
            "que nadie salga con vida ni revele lo que había dentro del contenedor.\n\n"
            "• The Chronicles of Ryzhy: Con un tono más oscuro y surrealista, sigue a Ryzhy, un habitante excéntrico de Tarkov que sobrevive "
            "en el submundo Scav y termina capturado y manipulado por los Cultistas y los organizadores clandestinos de la Arena. Su historia "
            "profundiza en la locura cotidiana de la ciudad sitiada, la influencia de los rituales del Ojo del Mundo y la presencia de figuras "
            "como Kaban y los gladiadores de Arena."
        ),
    },
]
