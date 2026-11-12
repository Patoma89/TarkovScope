"""
====================================================================
TTC (Tactical Tarkov Companion) - Story & Lore Encyclopedia
Crónica narrativa continua de Escape from Tarkov dividida por los
10 Capítulos Oficiales, con Índice de lectura rápida a la izquierda
y documento editorial ilustrado con banners e imágenes a la derecha.
====================================================================
"""
import customtkinter as ctk
from typing import Dict, Any, List, Optional
from core.config import THEME
from ui.theme import ui_font
from ui.image_utils import (
    get_story_chapter_icon_ctk,
    get_story_chapter_banner_ctk,
    get_story_gallery_ctk_image,
    get_story_gallery_full_pil,
)
from ui.theme import C_AMBER, C_BG_DEEP, C_BG_PANEL_ALT2, C_BG_ROW_ALT, C_BLUE, C_BORDER_SOFT, C_EMERALD, C_RED, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_TEXT_SOFT, C_WHITE

# Píxeles que avanza la rueda del mouse por cada muesca en el lector continuo (≈ scroll de navegador)
LORE_WHEEL_PX_PER_NOTCH = 110

LORE_NARRATIVE_CHAPTERS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Chapter 1: Tour",
        "subtitle_es": "El Colapso de Ground Zero y el Cerco Militar de Norvinsk",
        "date_str": "Prólogo — Inicio del Conflicto",
        "banner_file": "tour_banner.png",
        "icon_file": "tour_icon.png",
        "accent": C_BLUE,
        "narrative_es": (
            "Todo comienza en el corazón financiero de Tarkov: Ground Zero. A principios de la década de 2010, la Federación Rusa y la Unión Europea "
            "establecieron la Zona Económica Especial (ZEE) de Norvinsk para atraer inversiones tecnológicas y biotecnológicas extranjeras. Sin embargo, "
            "el conglomerado multinacional TerraGroup Inc. utilizó sus privilegios aduaneros y sobornos millonarios para adquirir complejos subterráneos "
            "militares soviéticos y laboratorios químicos por toda la ciudad.\n\n"
            "Cuando las agencias de contrainteligencia rusas detectaron el ingreso ilegal de armamento experimental, contenedores blindados y agentes patógenos, "
            "el conflicto diplomático escaló en cuestión de horas hacia una guerra encubierta entre dos compañías militares privadas: USEC (contratada por TerraGroup "
            "para destruir pruebas y proteger a sus ejecutivos) y BEAR (creada por Moscú para recuperar la evidencia a cualquier costo). En medio de la evacuación "
            "masiva, el centro corporativo de Ground Zero quedó sitiado y la ONU junto a las Fuerzas Armadas Rusas levantaron un cordón militar infranqueable alrededor "
            "de toda la provincia.\n\n"
            "Abandonado por tu propio mando tras la emboscada inicial, tu única salida consiste en abrirte paso entre los rascacielos destruidos de Skyside, "
            "establecer contacto con los comerciantes que controlan el mercado negro local —empezando por Therapist, Ragman, Skier y Prapor— y descubrir las rutas "
            "de tránsito que conectan las calles de Tarkov con la terminal portuaria de Shoreline y el resto de la región."
        ),
        "images": [
            ("Tutorial_By_xTycho_b8ad1c79.jpg", "Zona de impacto inicial y evacuación en Ground Zero"),
            ("Tour_Shoreline_Tower_c5b0e04b.jpg", "Torre de vigilancia del perímetro militar en la Terminal de Shoreline"),
        ],
    },
    {
        "id": 2,
        "title": "Chapter 2: Batya",
        "subtitle_es": "El Escuadrón Especial BEAR 'Bogatyr' y el Legado de Voevoda",
        "date_str": "Operaciones Especiales BEAR",
        "banner_file": "batya_banner.png",
        "icon_file": "batya_icon.png",
        "accent": C_EMERALD,
        "narrative_es": (
            "Entre las unidades de élite desplegadas en los primeros días del bloqueo destacó el legendario destacamento especial BEAR 'Bogatyr', comandado "
            "por un veterano oficial conocido bajo el indicativo 'Batya' (Voevoda). A diferencia de los mercenarios comunes, el escuadrón Bogatyr tenía una misión "
            "directa del alto mando de inteligencia: rastrear las células de mando de TerraGroup y proteger los nodos estratégicos de comunicaciones en Reserve, "
            "Woods y Shoreline.\n\n"
            "A medida que las comunicaciones con el exterior fueron saboteadas por pulsos electromagnéticos y traiciones internas, el escuadrón Bogatyr fue cazado "
            "sistemáticamente por francotiradores renegados y emboscadas de los cultistas nocturnos. Sus puestos de avanzada —como el puesto oculto en los bosques "
            "y el campamento improvisado en Lighthouse— quedaron sembrados de grabaciones de audio, placas de identificación (dogtags) y diarios personales de sus "
            "integrantes: Strelets, Taran, Moreman y el propio Voevoda.\n\n"
            "Seguir el rastro de 'Batya' con la ayuda de Jaeger y el conductor del BTR revela la cruda verdad sobre cómo los mejores soldados de ambos bandos fueron "
            "sacrificados como peones en una partida geopolítica mucho más oscura de lo que figuraba en sus órdenes oficiales."
        ),
        "images": [
            ("ZB-013_Building_b97236d0.jpg", "Fortificación subterránea y bastión en Customs"),
            ("Bogatyrs_patch_Lighthouse_BEAR_camp_7868def9.jpg", "Campamento táctico del escuadrón BEAR Bogatyr en Lighthouse"),
        ],
    },
    {
        "id": 3,
        "title": "Chapter 3: Falling Skies",
        "subtitle_es": "El Avión Derribado en Woods y el Maletín Blindado",
        "date_str": "El Incidente Aéreo de Priozersk",
        "banner_file": "falling_skies_banner.png",
        "icon_file": "falling_skies_icon.png",
        "accent": C_AMBER,
        "narrative_es": (
            "Cuando la directiva de TerraGroup comprendió que el cerco militar sobre Tarkov era total, ordenó una evacuación aérea desesperada desde el aeródromo "
            "privado llevando consigo los discos duros maestros, registros contables y el codiciado maletín blindado del ejecutivo Kruglov. Sin embargo, al cruzar "
            "el espacio aéreo sobre la reserva forestal de Priozersk (Woods), la aeronave fue alcanzada por un misil antiaéreo y se estrelló abriendo un surco de "
            "fuego entre los árboles.\n\n"
            "El siniestro desató una carrera contrarreloj entre Mechanic, Prapor y las facciones armadas de la región. En el lugar del impacto y en el convoy de "
            "escolta abandonado en Shoreline quedaron dispersas memorias USB encriptadas, la caja negra de transcripción de cabina y el maletín acorazado.\n\n"
            "Este capítulo marca la primera gran encrucijada moral de la historia de Tarkov: entregar el maletín blindado a Prapor consolida tu alianza con el "
            "aparato militar ruso, mientras que conservarlo en tu poder despierta el interés de Mr. Kerman —un misterioso hacker y bróker de información— pero te "
            "obliga a pagar un alto precio futuro ante los hombres de Prapor."
        ),
        "images": [
            ("Woods_Showcase_12_25956bfa.jpg", "Fuselaje del avión corporativo estrellado en el bosque de Woods"),
            ("FallingSkiesGWagonUSBSpawn_7373180c.jpg", "Vehículo blindado del convoy ejecutivo abandonado en Shoreline"),
        ],
    },
    {
        "id": 4,
        "title": "Chapter 4: Accidental Witness",
        "subtitle_es": "La Conspiración de Kozlov, Reshala y el Silencio Comprado",
        "date_str": "Crónica Criminal de Tarkov",
        "banner_file": "accidental_witness_banner.png",
        "icon_file": "accidental_witness_icon.png",
        "accent": "#EC4899",
        "narrative_es": (
            "No todas las víctimas de la caída de Tarkov eran soldados o científicos; muchos ciudadanos comunes quedaron atrapados al descubrir por accidente lo "
            "que ocurría detrás de los muros industriales. Tal fue el caso de Kozlov, un hombre ordinario cuya habitación en los dormitorios de Customs y su "
            "automóvil vandalizado en el patio se convirtieron en el epicentro de una cacería humana.\n\n"
            "Kozlov y su círculo cercano —incluyendo a su mensajero Pasha y a Anastasia— presenciaron los tratos sucios entre los agentes de seguridad corporativos "
            "y el sindicato criminal liderado por Reshala y Skier. A través de notas escondidas en buzones de Streets of Tarkov, apartamentos clausurados y el "
            "escondite personal del propio Reshala, la investigación reconstruye cómo el crimen organizado local funcionaba como el brazo ejecutor de TerraGroup "
            "para desaparecer testigos incómodos y traficar suministros médicos robados.\n\n"
            "Seguir las pistas de 'Accidental Witness' expone la brutalidad cotidiana del asedio urbano: en una ciudad sin ley, saber demasiado es una sentencia "
            "de muerte inmediata."
        ),
        "images": [
            ("Accidental_Witness_Car_636f5c10.jpg", "El automóvil blanco vandalizado en el patio de Dorms en Customs"),
            ("Room_110_Door_25ea743f.jpg", "Habitación 110 de los dormitorios donde comenzó la persecución de Kozlov"),
        ],
    },
    {
        "id": 5,
        "title": "Chapter 5: They Are Already Here",
        "subtitle_es": "La Secta del Ojo del Mundo y los Rituales Cultistas",
        "date_str": "Archivos Ocultistas de Norvinsk",
        "banner_file": "they_are_already_here_banner.png",
        "icon_file": "they_are_already_here_icon.png",
        "accent": "#06B6D4",
        "narrative_es": (
            "En la oscuridad de los bosques de Woods, los pantanos de Shoreline y las habitaciones marcadas con sangre en Customs y Reserve comenzó a extenderse "
            "un culto apocalíptico conocido como los adoradores del 'Ojo del Mundo' (Eye of the World). Vestidos con túnicas oscuras y portando dagas impregnadas "
            "en neurotoxinas letales, los Cultistas operan en absoluto silencio entre las 22:00 y las 06:00 horas.\n\n"
            "Lejos de ser simples lunáticos, las notas del sacerdote cultista y las cintas de audio halladas en cámaras de tortura demuestran que la secta posee "
            "vínculos profundos con antiguos experimentos psicotrópicos y estaciones de retransmisión satelital (ARRS) abandonadas en la región. Para ellos, el "
            "cataclismo de Tarkov es el inicio de una 'Gran Purificación' destinada a borrar la corrupción tecnológica moderna.\n\n"
            "Investigar sus altares rituales, reactivar la estación ARRS bajo el asedio de sus guerreros y recuperar la memoria USB maestra constituye una pieza "
            "clave para reunir las pruebas mayores (Major Evidence) sobre el verdadero alcance de los experimentos en Norvinsk."
        ),
        "images": [
            ("They_Are_Already_Here_Customs_Activation_Locatio_a2e92213.jpg", "Altar y manuscrito del Ojo del Mundo en la habitación marcada"),
            ("They_Are_Already_Here_Reserve_Activation_Locatio_a53a5f5a.jpg", "Cámara ritual subterránea en los búnkeres de Reserve"),
        ],
    },
    {
        "id": 6,
        "title": "Chapter 6: The Unheard",
        "subtitle_es": "El Combustible Catalítico, el Proyecto Purificación y los Silenciados",
        "date_str": "Expedientes Clasificados TerraGroup",
        "banner_file": "the_unheard_banner.png",
        "icon_file": "the_unheard_icon.png",
        "accent": "#A855F7",
        "narrative_es": (
            "Detrás de los estimulantes de combate y las vacunas experimentales de TerraGroup existía un programa aún más reservado: la síntesis del compuesto "
            "catalizador y el protocolo conocido en los documentos internos como 'La Purificación'. Los registros ocultos en el puesto de seguridad de TerraGroup "
            "en Streets of Tarkov y en los laboratorios médicos revelan la historia del científico A.P. y de aquellos investigadores que intentaron alertar al "
            "mundo antes de ser silenciados ('The Unheard').\n\n"
            "A través de transcripciones clínicas, bitácoras de transporte ferroviario y muestras ocultas en bóvedas subterráneas, se descubre que TerraGroup "
            "planeaba utilizar un agente bioquímico de dispersión masiva para eliminar cualquier rastro biológico de sus fallos genéticos en la población de "
            "Tarkov en caso de perder el control político de la Zona Económica Especial."
        ),
        "images": [
            ("TerraGroup_security_post_Building_b3d1ad32.jpg", "Puesto de seguridad corporativo de TerraGroup en Streets of Tarkov"),
            ("TerraGroup_security_armory_Way_1_88d9db5f.jpg", "Interior de las oficinas de vigilancia y archivos clasificados"),
        ],
    },
    {
        "id": 7,
        "title": "Chapter 7: Blue Fire",
        "subtitle_es": "El Objeto #1156 y la Detonación Electromagnética (EMP)",
        "date_str": "Protocolo de Contención Tecnológica",
        "banner_file": "blue_fire_banner.png",
        "icon_file": "blue_fire_icon.png",
        "accent": "#3B82F6",
        "narrative_es": (
            "¿Por qué colapsaron simultáneamente todas las redes eléctricas, radares militares y comunicaciones digitales de Tarkov la noche en que comenzó el "
            "asedio? La respuesta se esconde tras el nombre en clave 'Blue Fire' y el misterioso dispositivo catalogado como 'Ítem #1156'.\n\n"
            "Los panfletos de emergencia de EMERCOM y los fragmentos electrónicos recuperados en el concesionario fortificado de LexOs y en los laboratorios de "
            "The Lab confirman que se detonó un generador experimental de pulso electromagnético (EMP) de alta densidad. Este pulso no solo dejó ciegos a los "
            "satélites de reconocimiento y derribó aeronaves en tránsito, sino que fue diseñado para aislar electrónicamente a Tarkov del resto del planeta "
            "mientras las unidades de limpieza de Black Division borraban los servidores centrales.\n\n"
            "Junto a Mechanic, el jugador debe infiltrarse en las salas de servidores de The Lab para hackear la red interna y recuperar los planos del "
            "dispositivo que dejó a toda una ciudad sumida en la Edad de Piedra moderna."
        ),
        "images": [
            ("Blue_Fire_Woods_Activation_Location_Container_a70be920.jpg", "Contenedor de suministros de EMERCOM con directivas de emergencia"),
            ("Blue_Fire_Woods_Activation_Location_c1b2d20e.jpg", "Documento confidencial sobre el dispositivo EMP e Ítem #1156"),
        ],
    },
    {
        "id": 8,
        "title": "Chapter 8: Boreas",
        "subtitle_es": "Paradigm Shipping y el Asalto al Rompehielos Nuclear",
        "date_str": "Operación Ártica en la Costa",
        "banner_file": "boreas_banner.png",
        "icon_file": "boreas_icon.png",
        "accent": "#0EA5E9",
        "narrative_es": (
            "Cuando las rutas terrestres y aéreas quedaron bloqueadas, TerraGroup activó su centro de mando flotante: el buque rompehielos 'Boreas', operado por "
            "su subsidiaria marítima fantasma Paradigm Shipping. Anclado entre los hielos de la costa norte, el Boreas funcionaba como centro de procesamiento "
            "de datos criptográficos y plataforma de evacuación para los altos mandos corporativos.\n\n"
            "Sin embargo, una señal de socorro captada desde la torre celular de Woods y el Centro de Inteligencia revela que algo salió terriblemente mal a "
            "bordo. Tras negociar un transporte en aerodeslizador con los contrabandistas y el conductor del BTR, el operador aborda el coloso de acero para "
            "encontrar a la tripulación masacrada, las cubiertas tomadas por escuadrones de élite de Black Division y Rogues liderados por 'The Wedge' y 'Knight', "
            "y al último científico superviviente atrincherado tras puertas con código.\n\n"
            "Volar con explosivos SZ-1 el acceso a la superestructura, descongelar con soplete la escotilla del techo del puente, extraer los discos duros del "
            "Compartimento C-1 y organizar el rescate del científico constituyen una de las operaciones tácticas más intensas de toda la campaña."
        ),
        "images": [
            ("Boreas_Equipment_d3869068.jpg", "Repetidor de radio bajo la torre celular de Woods que capta el SOS del Boreas"),
            ("Boreas_Paradigm_Shipping_Directive_d57457ba.jpg", "Directiva marítima secreta de Paradigm Shipping en los almacenes de Lighthouse"),
        ],
    },
    {
        "id": 9,
        "title": "Chapter 9: The Ticket",
        "subtitle_es": "Los 4 Finales de Escape from Tarkov y la Batalla por la Terminal",
        "date_str": "El Clímax — La Huida Definitiva",
        "banner_file": "the_ticket_banner.png",
        "icon_file": "the_ticket_icon.png",
        "accent": "#EAB308",
        "narrative_es": (
            "Toda la travesía en Norvinsk converge en 'The Ticket': la apertura del maletín blindado de Kruglov para obtener la tarjeta RFID maestra ('El Boleto') "
            "que permite cruzar el puesto de control del puerto militar de Terminal entre las 21:00 y las 06:00 horas.\n\n"
            "Dependiendo de tus decisiones morales, tu lealtad hacia Mr. Kerman, Lightkeeper, Fence y Prapor, y la cantidad de pruebas contra TerraGroup que hayas "
            "reunido, la historia se bifurca en cuatro desenlaces canónicos completamente distintos:\n\n"
            "• 1. Final SAVIOR (El Salvador): Aceptas colaborar con Mr. Kerman, reúnes las 8 evidencias mayores (y opcionalmente las 36 menores) de los crímenes "
            "de TerraGroup, alcanzas reputación máxima de honor con Fence (+4.0) y el BTR Driver, y cruzas la Terminal portando el contenedor seguro Alpha-1 "
            "para exponer la verdad ante el mundo entero.\n\n"
            "• 2. Final DEBTOR (El Deudor): Aceptas la oferta de Kerman pero te niegas a entregarle todas las pruebas, recurriendo en su lugar a Lightkeeper. "
            "Para pagar tu pasaje, debes recopilar mapas topográficos de 5 regiones, entregar 100 chapas de PMC y depositar 6 amuletos sagrados de las habitaciones "
            "marcadas en el santuario de la isla del faro.\n\n"
            "• 3. Final SURVIVOR (El Superviviente): Rechazas los juegos de Kerman desde el principio y pactas directamente con Prapor, pagando una fortuna "
            "colosal en rublos (300 a 500 millones) y digitalizando expedientes de laboratorio para obtener una carta de paso firmada por la guarnición militar.\n\n"
            "• 4. Final FALLEN (El Caído): Traicionas el acuerdo con Kerman tras activar la tarjeta y te ves forzado a cumplir las exigencias más duras de Prapor "
            "—entregando contenedores seguros, cargamentos peligrosos y un millón de dólares— para reprogramar los códigos hash a la fuerza.\n\n"
            "En cualquiera de las cuatro rutas, una vez dentro del puerto de Terminal deberás recuperar tu equipo confiscado en la armería, abrirte paso a sangre "
            "y fuego contra los escuadrones de Black Division, drenar la estación de bombeo inundada y alcanzar el muelle de evacuación antes de que el puerto "
            "entero vuele en pedazos."
        ),
        "images": [
            ("Tour_Shoreline_Intercom_ada288d8.jpg", "Lector de tarjetas e intercomunicador de acceso nocturno a la Terminal"),
            ("NoteFromPraporsMenSpawn1_40e10650.jpg", "Rastro de los emisarios de Prapor en el campamento costero"),
        ],
    },
    {
        "id": 10,
        "title": "Chapter 10: The Labyrinth",
        "subtitle_es": "La Instalación Subterránea Knossos LLC y el Horror del Minotauro",
        "date_str": "Epílogo Secreto — Profundidades de Shoreline",
        "banner_file": "the_labyrinth_banner.png",
        "icon_file": "the_labyrinth_icon.png",
        "accent": C_RED,
        "narrative_es": (
            "Bajo los cimientos del ala oeste del balneario Health Resort en Shoreline se oculta el secreto más perturbador de toda la región de Norvinsk: "
            "la instalación subterránea de Knossos LLC, conocida como 'The Labyrinth'. Construida oficialmente como un búnker temático y centro recreativo "
            "de alto nivel para contratistas de TerraGroup, el complejo fue transformado en una prisión laberíntica de ensayos conductuales y armamento biológico.\n\n"
            "Dentro de sus pasillos asfixiantes —divididos en 5 cámaras con trampas mortales de piscinas tóxicas, vapor hirviente, incendios, escopetas "
            "automatizadas y alambre de púas envenenado— merodean versiones psicóticas y letales conocidas como 'Shadow of Tagilla' y 'Vengeful Killa'.\n\n"
            "Contratado por Therapist y Jaeger para investigar el paradero del escuadrón de Leshy y los científicos desaparecidos, el jugador debe descifrar "
            "los acertijos de las cámaras, acceder a la sala de observación acorazada, escuchar la cinta de audio póstuma del director científico y extraer "
            "el Informe de Investigación del Laberinto para sellar definitivamente los horrores de Knossos."
        ),
        "images": [
            ("The_Labyrinth_Transit_Door_9e30b777.jpg", "Puerta blindada de Knossos LLC en el sótano del Health Resort"),
            ("The_Labyrinth_Transit_589d4cbf.jpg", "Descenso hacia los túneles subterráneos de The Labyrinth"),
        ],
    },
]


class TabLore(ctk.CTkFrame):
    """
    Pestaña de Historia & Lore Oficial (10 Capítulos en documento continuo).
    Columna izquierda: Índice limpio de lectura rápida.
    Columna derecha: Libro / Crónica narrativa continua separada por capítulos con imágenes HD.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.active_chapter_id: int = 1
        self.index_buttons: Dict[int, ctk.CTkButton] = {}
        self.chapter_section_frames: Dict[int, ctk.CTkFrame] = {}
        self._narrative_labels: List[ctk.CTkLabel] = []
        self._resize_job: Optional[str] = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_index_sidebar()
        self._build_continuous_reader()

        self.reader_scroll.bind("<Configure>", self._on_reader_resize)

    # =========================================================================
    # COLUMNA IZQUIERDA: ÍNDICE EDITORIAL LIMPIO
    # =========================================================================
    def _build_index_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=270,
            fg_color=C_BG_DEEP,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        sidebar.grid(row=0, column=0, padx=(0, 12), pady=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(2, weight=1)

        # Cabecera del Índice
        hdr = ctk.CTkFrame(sidebar, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=16, pady=(16, 10), sticky="ew")

        ctk.CTkLabel(
            hdr,
            text="📚 ÍNDICE DE LA HISTORIA",
            font=ui_font(15, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            hdr,
            text="Crónica completa en español • Haz clic en un capítulo para saltar a su sección",
            font=ui_font(11),
            text_color=C_TEXT_DIM,
            wraplength=235,
            justify="left"
        ).pack(anchor="w", pady=(3, 0))

        sep = ctk.CTkFrame(sidebar, height=1, fg_color=C_BG_ROW_ALT)
        sep.grid(row=1, column=0, padx=14, pady=(0, 6), sticky="ew")

        idx_list = ctk.CTkFrame(sidebar, fg_color="transparent")
        idx_list.grid(row=2, column=0, padx=10, pady=(2, 10), sticky="nsew")
        idx_list.grid_columnconfigure(0, weight=1)

        for idx, ch in enumerate(LORE_NARRATIVE_CHAPTERS):
            cid = ch["id"]
            is_act = (cid == self.active_chapter_id)
            icon_ctk = get_story_chapter_icon_ctk(ch["icon_file"], size=(22, 22))

            btn = ctk.CTkButton(
                idx_list,
                text=f"  {cid:02d}.  {ch['title'].replace('Chapter ' + str(cid) + ': ', '')}",
                image=icon_ctk,
                compound="left",
                anchor="w",
                height=38,
                corner_radius=6,
                fg_color="#1E2638" if is_act else "transparent",
                hover_color="#182030",
                border_width=1 if is_act else 0,
                border_color=THEME["accent_gold"] if is_act else C_BG_DEEP,
                text_color=C_WHITE if is_act else C_TEXT_MUTED,
                font=ui_font(13, "bold" if is_act else "normal"),
                command=lambda c_id=cid: self._scroll_to_chapter(c_id)
            )
            btn.grid(row=idx, column=0, padx=2, pady=2, sticky="ew")
            self.index_buttons[cid] = btn

        # Botón para volver arriba del todo
        ctk.CTkButton(
            sidebar,
            text="⬆ Ir al Inicio del Documento",
            height=32,
            corner_radius=6,
            fg_color="#141924",
            hover_color="#1F2738",
            border_width=1,
            border_color="#2D3648",
            text_color=C_TEXT_DIM,
            font=ui_font(11, "bold"),
            command=lambda: self._scroll_to_chapter(1)
        ).grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")

    # =========================================================================
    # COLUMNA DERECHA: DOCUMENTO CONTINUO EXPLICATIVO CON IMÁGENES
    # =========================================================================
    def _build_continuous_reader(self):
        self.reader_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#0B0E14",
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        self.reader_scroll.grid(row=0, column=1, sticky="nsew")
        self.reader_scroll.grid_columnconfigure(0, weight=1)

        # Portada / Introducción General del Documento
        intro_box = ctk.CTkFrame(
            self.reader_scroll,
            fg_color="#111621",
            corner_radius=10,
            border_width=1,
            border_color="#2E384D"
        )
        intro_box.grid(row=0, column=0, padx=20, pady=(18, 12), sticky="ew")
        intro_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            intro_box,
            text="HISTORIA COMPLETA Y LORE DE ESCAPE FROM TARKOV",
            font=ui_font(22, "bold"),
            text_color=THEME["accent_gold"],
            anchor="w"
        ).grid(row=0, column=0, padx=22, pady=(16, 4), sticky="w")

        intro_sub = (
            "Crónica integral en español de los 10 Capítulos de la campaña principal de Escape from Tarkov. "
            "Este documento relata de forma continua qué ocurrió en la región de Norvinsk, los experimentos secretos "
            "de TerraGroup, el surgimiento de las facciones y los cuatro desenlaces posibles para escapar de Tarkov."
        )
        lbl_intro = ctk.CTkLabel(
            intro_box,
            text=intro_sub,
            font=ui_font(13),
            text_color=C_TEXT_MUTED,
            justify="left",
            wraplength=860,
            anchor="w"
        )
        lbl_intro.grid(row=1, column=0, padx=22, pady=(0, 16), sticky="w")
        self._narrative_labels.append(lbl_intro)

        # Renderizar los 10 capítulos en flujo continuo tipo libro
        for idx, ch in enumerate(LORE_NARRATIVE_CHAPTERS, start=1):
            sec = self._create_chapter_article_section(self.reader_scroll, ch, row_idx=idx)
            self.chapter_section_frames[ch["id"]] = sec

        # Habilitar rueda del ratón sobre todos los elementos del documento para que siempre desplace suave
        self._bind_mousewheel_recursive(self.reader_scroll)
        self.after(60, self._refresh_scrollregion)

    def _refresh_scrollregion(self):
        if not self.winfo_exists():
            return
        try:
            self.update_idletasks()
            canvas = self.reader_scroll._parent_canvas
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
        except Exception:
            pass

    def _bind_mousewheel_recursive(self, widget):
        try:
            widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        except Exception:
            pass
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)

    def _on_mousewheel(self, event):
        """Scroll por píxeles: CTkScrollableFrame usa yscrollincrement=1, así que 'units' = 1 px.
        Se avanza LORE_WHEEL_PX_PER_NOTCH px por cada muesca (delta 120); los touchpads de
        alta resolución (delta menor) escalan proporcionalmente."""
        try:
            canvas = self.reader_scroll._parent_canvas
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
            total_h = max(1, (bbox[3] - bbox[1]) if bbox else 1)
            delta_px = -event.delta * LORE_WHEEL_PX_PER_NOTCH / 120.0
            if abs(delta_px) < 1:
                delta_px = -1.0 if event.delta > 0 else 1.0
            first, _last = canvas.yview()
            canvas.yview_moveto(max(0.0, min(1.0, first + delta_px / total_h)))
            return "break"
        except Exception:
            pass

    def _create_chapter_article_section(self, parent, ch: Dict[str, Any], row_idx: int) -> ctk.CTkFrame:
        cid = ch["id"]
        accent = ch.get("accent", THEME["accent_gold"])

        article = ctk.CTkFrame(
            parent,
            fg_color="#0F131C",
            corner_radius=10,
            border_width=1,
            border_color="#232B3C"
        )
        article.grid(row=row_idx, column=0, padx=20, pady=12, sticky="ew")
        article.grid_columnconfigure(0, weight=1)

        cur_r = 0

        # 1. Banner panorámico oficial del capítulo
        banner_ctk = get_story_chapter_banner_ctk(ch.get("banner_file", ""), target_width=860)
        if banner_ctk:
            b_lbl = ctk.CTkLabel(article, text="", image=banner_ctk)
            b_lbl.grid(row=cur_r, column=0, padx=16, pady=(16, 10), sticky="w")
            cur_r += 1

        # 2. Encabezado del Capítulo (Ícono + Título en inglés + Subtítulo narrativo en español)
        hdr_row = ctk.CTkFrame(article, fg_color="transparent")
        hdr_row.grid(row=cur_r, column=0, padx=22, pady=(4, 2), sticky="ew")
        cur_r += 1

        icon_ctk = get_story_chapter_icon_ctk(ch.get("icon_file", ""), size=(34, 34))
        if icon_ctk:
            ctk.CTkLabel(hdr_row, text="", image=icon_ctk).pack(side="left", padx=(0, 10))

        title_col = ctk.CTkFrame(hdr_row, fg_color="transparent")
        title_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            title_col,
            text=ch["title"].upper(),
            font=ui_font(20, "bold"),
            text_color=C_WHITE,
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col,
            text=f"{ch['subtitle_es']}   •   {ch['date_str']}",
            font=ui_font(13, "bold"),
            text_color=accent,
            anchor="w"
        ).pack(anchor="w")

        # Línea divisoria sutil bajo el título
        div = ctk.CTkFrame(article, height=2, fg_color=accent)
        div.grid(row=cur_r, column=0, padx=22, pady=(8, 12), sticky="ew")
        cur_r += 1

        # 3. Texto narrativo continuo del capítulo
        lbl_body = ctk.CTkLabel(
            article,
            text=ch["narrative_es"],
            font=ui_font(14),
            text_color=C_TEXT_SOFT,
            justify="left",
            wraplength=860,
            anchor="w"
        )
        lbl_body.grid(row=cur_r, column=0, padx=24, pady=(0, 14), sticky="w")
        self._narrative_labels.append(lbl_body)
        cur_r += 1

        # 4. Imágenes ilustrativas del capítulo (con clic para ampliar en HD)
        imgs = ch.get("images", [])
        if imgs:
            img_bar = ctk.CTkFrame(article, fg_color="#0A0D13", corner_radius=8, border_width=1, border_color="#1D2534")
            img_bar.grid(row=cur_r, column=0, padx=22, pady=(0, 18), sticky="ew")
            img_bar.grid_columnconfigure(0, weight=1)
            img_bar.grid_columnconfigure(1, weight=1)

            for i_idx, (img_fn, img_cap) in enumerate(imgs[:2]):
                pic_card = ctk.CTkFrame(
                    img_bar,
                    fg_color=C_BG_PANEL_ALT2,
                    corner_radius=6,
                    border_width=1,
                    border_color="#2A3447",
                    cursor="hand2"
                )
                pic_card.grid(row=0, column=i_idx, padx=8, pady=8, sticky="nsew")

                ctk_img = get_story_gallery_ctk_image(img_fn, max_size=(390, 215))
                if ctk_img:
                    p_lbl = ctk.CTkLabel(pic_card, text="", image=ctk_img)
                    p_lbl.pack(padx=6, pady=(6, 4))
                else:
                    p_lbl = ctk.CTkLabel(pic_card, text="", height=120)
                    p_lbl.pack(padx=6, pady=6)

                c_lbl = ctk.CTkLabel(
                    pic_card,
                    text=f"📷 {img_cap} (Clic para ampliar)",
                    font=ui_font(11, "bold"),
                    text_color=C_TEXT_MUTED,
                    wraplength=375,
                    justify="center"
                )
                c_lbl.pack(padx=8, pady=(0, 6))

                for w in (pic_card, p_lbl, c_lbl):
                    w.bind("<Button-1>", lambda e, f=img_fn, cp=img_cap, t=ch["title"]: self._open_lore_zoom(f, cp, t))

        return article

    # =========================================================================
    # SALTO INSTANTÁNEO DESDE EL ÍNDICE AL CAPÍTULO EN EL TEXTO
    # =========================================================================
    def _scroll_to_chapter(self, chapter_id: int):
        self.active_chapter_id = chapter_id
        for cid, btn in self.index_buttons.items():
            is_act = (cid == chapter_id)
            btn.configure(
                fg_color="#1E2638" if is_act else "transparent",
                border_width=1 if is_act else 0,
                border_color=THEME["accent_gold"] if is_act else C_BG_DEEP,
                text_color=C_WHITE if is_act else C_TEXT_MUTED,
                font=ui_font(13, "bold" if is_act else "normal")
            )

        target_widget = self.chapter_section_frames.get(chapter_id)
        if not target_widget:
            return

        try:
            self.update_idletasks()
            canvas = self.reader_scroll._parent_canvas
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
                total_h = max(1, bbox[3] - bbox[1])
            else:
                total_h = max(1, self.reader_scroll.winfo_reqheight())

            if chapter_id == 1:
                canvas.yview_moveto(0.0)
            else:
                y_pos = target_widget.winfo_y()
                if y_pos <= 5:
                    # Fallback en caso de que winfo_y aún no esté consolidado
                    y_pos = target_widget.winfo_rooty() - self.reader_scroll.winfo_rooty()
                fraction = max(0.0, min(1.0, (y_pos - 16) / total_h))
                canvas.yview_moveto(fraction)
        except Exception:
            pass

    def _on_reader_resize(self, _=None):
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(140, self._apply_wrap_width)

    def _apply_wrap_width(self):
        self._resize_job = None
        w = self.reader_scroll.winfo_width()
        if w <= 150:
            return
        wrap_px = max(480, w - 95)
        for lbl in self._narrative_labels:
            try:
                if lbl.winfo_exists():
                    lbl.configure(wraplength=wrap_px)
            except Exception:
                pass
        try:
            self.update_idletasks()
            canvas = self.reader_scroll._parent_canvas
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
        except Exception:
            pass

    def _open_lore_zoom(self, gallery_file: str, caption: str, ch_title: str):
        pil_img = get_story_gallery_full_pil(gallery_file, max_size=(1240, 720))
        if not pil_img:
            return

        top = ctk.CTkToplevel(self)
        top.title(f"TTC — Ilustración de Lore: {ch_title}")
        top.geometry("1260x800")
        top.configure(fg_color="#090B10")
        top.transient(self.winfo_toplevel())
        top.grab_set()

        hdr = ctk.CTkFrame(top, fg_color=C_BG_PANEL_ALT2, corner_radius=0, height=52)
        hdr.pack(fill="x", side="top")

        ctk.CTkLabel(
            hdr,
            text=f"📜 {ch_title}  —  {caption}",
            font=ui_font(14, "bold"),
            text_color=C_TEXT
        ).pack(side="left", padx=16, pady=12)

        ctk.CTkButton(
            hdr,
            text="✕ Cerrar (ESC)",
            width=120,
            height=32,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=top.destroy
        ).pack(side="right", padx=16, pady=10)

        top.bind("<Escape>", lambda e: top.destroy())

        box = ctk.CTkFrame(top, fg_color="#090B10")
        box.pack(fill="both", expand=True, padx=12, pady=12)

        ctk_full = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        ctk.CTkLabel(box, text="", image=ctk_full).pack(expand=True)
