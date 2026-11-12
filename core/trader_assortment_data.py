"""
TarkovScope - Base de Datos de Inventario y Barters de Traders (LL1 a LL4)
Contiene los ítems, armas, municiones, protecciones y trueques (barters) oficiales
de la Wiki de Escape from Tarkov que cada comerciante vende según su nivel de lealtad (LL1 a LL4).
"""
from typing import Dict, List, Any

# Requisitos de nivel de jugador, reputación y gasto en rublos para cada LL por Trader
TRADER_LL_REQUIREMENTS: Dict[str, Dict[int, Dict[str, Any]]] = {
    "Prapor": {
        1: {"level": 1, "rep": 0.00, "spend": 0, "title": "Nivel 1 (Inicial)"},
        2: {"level": 15, "rep": 0.20, "spend": "750,000 ₽", "title": "Nivel 2"},
        3: {"level": 26, "rep": 0.35, "spend": "1,500,000 ₽", "title": "Nivel 3"},
        4: {"level": 36, "rep": 0.50, "spend": "2,400,000 ₽", "title": "Corona (LL4 Máximo)"},
    },
    "Therapist": {
        1: {"level": 1, "rep": 0.00, "spend": 0, "title": "Nivel 1 (Inicial)"},
        2: {"level": 13, "rep": 0.15, "spend": "450,000 ₽", "title": "Nivel 2"},
        3: {"level": 24, "rep": 0.30, "spend": "900,000 ₽", "title": "Nivel 3"},
        4: {"level": 35, "rep": 0.60, "spend": "1,600,000 ₽", "title": "Corona (LL4 Máximo)"},
    },
    "Skier": {
        1: {"level": 1, "rep": 0.00, "spend": 0, "title": "Nivel 1 (Inicial)"},
        2: {"level": 15, "rep": 0.20, "spend": "800,000 ₽", "title": "Nivel 2"},
        3: {"level": 28, "rep": 0.35, "spend": "1,600,000 ₽", "title": "Nivel 3"},
        4: {"level": 38, "rep": 0.55, "spend": "2,600,000 ₽", "title": "Corona (LL4 Máximo)"},
    },
    "Peacekeeper": {
        1: {"level": 1, "rep": 0.00, "spend": 0, "title": "Nivel 1 (Inicial)"},
        2: {"level": 14, "rep": 0.00, "spend": "$ 11,000 USD", "title": "Nivel 2"},
        3: {"level": 23, "rep": 0.30, "spend": "$ 25,000 USD", "title": "Nivel 3"},
        4: {"level": 37, "rep": 0.60, "spend": "$ 40,000 USD", "title": "Corona (LL4 Máximo)"},
    },
    "Mechanic": {
        1: {"level": 1, "rep": 0.00, "spend": 0, "title": "Nivel 1 (Inicial)"},
        2: {"level": 20, "rep": 0.15, "spend": "850,000 ₽", "title": "Nivel 2"},
        3: {"level": 30, "rep": 0.30, "spend": "1,700,000 ₽", "title": "Nivel 3"},
        4: {"level": 40, "rep": 0.60, "spend": "2,800,000 ₽", "title": "Corona (LL4 Máximo)"},
    },
    "Ragman": {
        1: {"level": 1, "rep": 0.00, "spend": 0, "title": "Nivel 1 (Inicial)"},
        2: {"level": 17, "rep": 0.20, "spend": "900,000 ₽", "title": "Nivel 2"},
        3: {"level": 32, "rep": 0.40, "spend": "2,200,000 ₽", "title": "Nivel 3"},
        4: {"level": 42, "rep": 0.60, "spend": "3,600,000 ₽", "title": "Corona (LL4 Máximo)"},
    },
    "Jaeger": {
        1: {"level": 1, "rep": 0.00, "spend": 0, "title": "Nivel 1 (Inicial)"},
        2: {"level": 15, "rep": 0.20, "spend": "750,000 ₽", "title": "Nivel 2"},
        3: {"level": 22, "rep": 0.35, "spend": "1,500,000 ₽", "title": "Nivel 3"},
        4: {"level": 33, "rep": 0.50, "spend": "2,300,000 ₽", "title": "Corona (LL4 Máximo)"},
    },
    "Ref": {
        1: {"level": 1, "rep": 0.00, "spend": 0, "title": "Nivel 1 (Arena Inicial)"},
        2: {"level": 15, "rep": 0.20, "spend": "10x GP Coins", "title": "Nivel 2"},
        3: {"level": 25, "rep": 0.35, "spend": "25x GP Coins", "title": "Nivel 3"},
        4: {"level": 35, "rep": 0.50, "spend": "50x GP Coins", "title": "Corona (LL4 Máximo)"},
    },
    "Fence": {
        1: {"level": 1, "rep": 0.00, "spend": 0, "title": "Mercado Negro Scav (Karma Estándar)"},
        2: {"level": 1, "rep": 2.00, "spend": 0, "title": "Karma Positivo (Rep +2.0)"},
        3: {"level": 1, "rep": 4.00, "spend": 0, "title": "Aliado Fiel (Rep +4.0)"},
        4: {"level": 1, "rep": 6.00, "spend": 0, "title": "Pestaña VIP Máxima (Rep +6.0 Corona)"},
    }
}

# Catálogo exhaustivo de ítems, armas, munición y barters por comerciante y nivel de afinidad
TRADER_ASSORTMENT_DATA: Dict[str, Dict[int, List[Dict[str, Any]]]] = {
    "Prapor": {
        1: [
            {"name": "AKS-74U 5.45x39", "category": "ARMA", "cost": "24,800 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "aks74u", "desc": "Carabina automática compacta rusa."},
            {"name": "Pistola TT-33 Tokarev 7.62x25", "category": "ARMA", "cost": "11,200 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "p226", "desc": "Pistola clásica de alto calibre."},
            {"name": "Pistola Makarov PM 9x18", "category": "ARMA", "cost": "6,400 ₽", "is_barter": False, "limit": "5 por reset", "image_key": "p226", "desc": "Pistola de mano de emergencia."},
            {"name": "Munición 5.45x39 PS gs (120x)", "category": "MUNICIÓN", "cost": "18,000 ₽", "is_barter": False, "limit": "120 por reset", "image_key": "gs_1", "desc": "Bala con núcleo de acero perforante básico."},
            {"name": "Munición 7.62x39 FMJ (90x)", "category": "MUNICIÓN", "cost": "14,500 ₽", "is_barter": False, "limit": "90 por reset", "image_key": "gs_2", "desc": "Munición soviética estándar de buen daño."},
            {"name": "Granada Defensiva F-1", "category": "GRANADA", "cost": "11,500 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_gp25", "desc": "Granada de fragmentación de largo radio."},
            {"name": "Cargador 6L23 30 tiros 5.45x39", "category": "ACCESORIO", "cost": "2,400 ₽", "is_barter": False, "limit": "6 por reset", "image_key": "p_6l31", "desc": "Cargador estándar de polímero negro para AK-74."},
            {"name": "🔄 Cargador 60 tiros 5.45x39 (6L31)", "category": "BARTER", "cost": "1x Disco Rígido (HDD)", "is_barter": True, "limit": "2 por reset", "image_key": "p_6l31", "desc": "Trueque esencial para la quest 'Ice Cream Cones'."},
            {"name": "🔄 Pistola TT Dorada", "category": "BARTER", "cost": "2x Reloj Roto (Broken Watch)", "is_barter": True, "limit": "1 por reset", "image_key": "p226", "desc": "Edición especial de coleccionista."}
        ],
        2: [
            {"name": "Fusil de Asalto AK-74M 5.45x39", "category": "ARMA", "cost": "42,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "ak74m", "desc": "El fusil reglamentario del ejército ruso con culata plegable."},
            {"name": "Fusil de Asalto AKM 7.62x39", "category": "ARMA", "cost": "46,500 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "rd_704", "desc": "Poder de fuego contundente en calibre 7.62x39."},
            {"name": "Munición 7.62x39 PS (120x)", "category": "MUNICIÓN", "cost": "32,000 ₽", "is_barter": False, "limit": "120 por reset", "image_key": "gs_3", "desc": "Excelente penetración clase 3/4 temprana."},
            {"name": "Granada Ofensiva RGD-5", "category": "GRANADA", "cost": "9,800 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "p_gp25", "desc": "Menor tiempo de espoleta (3.5s) que la F-1."},
            {"name": "Armadura Corporal 6B23-1 (Clase 3)", "category": "ARMADURA", "cost": "38,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_4", "desc": "Protección económica de tórax y estómago."},
            {"name": "🔄 Fusil de Precisión VSS Vintorez", "category": "BARTER", "cost": "2x Filtro Militar (Gas Filter)", "is_barter": True, "limit": "1 por reset", "image_key": "vss_val", "desc": "Arma silenciada integrada letal a corta distancia."},
            {"name": "🔄 Supresor PBS-4 para 5.45x39", "category": "BARTER", "cost": "2x Alicates (Pliers Elite)", "is_barter": True, "limit": "2 por reset", "image_key": "p_pbs4", "desc": "Silenciador ruso de alta durabilidad."}
        ],
        3: [
            {"name": "Fusil AS VAL 9x39 Silenciado", "category": "ARMA", "cost": "85,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "vss_val", "desc": "Fusil de asalto especial para fuerzas Spetsnaz."},
            {"name": "Rifle de Precisión SV-98 7.62x54R", "category": "ARMA", "cost": "58,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "sr_25", "desc": "Cerrojo pesado de largo alcance."},
            {"name": "Munición 9x39 SPP gs (90x)", "category": "MUNICIÓN", "cost": "52,000 ₽", "is_barter": False, "limit": "90 por reset", "image_key": "gs_5", "desc": "Munición subsónica de alta penetración."},
            {"name": "Munición 7.62x54R LPS (80x)", "category": "MUNICIÓN", "cost": "36,000 ₽", "is_barter": False, "limit": "80 por reset", "image_key": "gs_6", "desc": "Capaz de atravesar armaduras Nivel 4 de un impacto."},
            {"name": "Casco Militar 6B47 Ratnik", "category": "CASCO", "cost": "34,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_7", "desc": "Casco ligero con soporte para visión nocturna."},
            {"name": "🔄 Cajas de Munición Ammo Case", "category": "BARTER", "cost": "4x Tarros de Pólvora Azul + 2x Verde", "is_barter": True, "limit": "1 por reset", "image_key": "gs_8", "desc": "Contenedor para ordenar cientos de cartuchos en el stash."},
            {"name": "🔄 Chaleco 6B13 Flora (Clase 4)", "category": "BARTER", "cost": "3x Máscaras de Gas Neopreno", "is_barter": True, "limit": "2 por reset", "image_key": "gs_9", "desc": "Excelente protección de placas cerámicas."}
        ],
        4: [
            {"name": "Ametralladora Pesada PKP Pecheneg", "category": "ARMA", "cost": "185,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "gs_10", "desc": "Cadencia devastadora y cargador de cinta de 100 tiros."},
            {"name": "Munición 7.62x54R BT Perforante", "category": "MUNICIÓN", "cost": "84,000 ₽", "is_barter": False, "limit": "60 por reset", "image_key": "gs_11", "desc": "Tracer militar de máxima penetración clase 5/6."},
            {"name": "Munición 9x39 BP Perforante (60x)", "category": "MUNICIÓN", "cost": "95,000 ₽", "is_barter": False, "limit": "60 por reset", "image_key": "gs_12", "desc": "La munición subsónica más letal del juego."},
            {"name": "Armadura Pesada Korund-VM (Clase 5)", "category": "ARMADURA", "cost": "145,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "gs_13", "desc": "Placas de acero blindado de fácil reparación."},
            {"name": "Mochila Militar 6Sh118 Raid (96L)", "category": "MOCHILA", "cost": "115,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_14", "desc": "La mochila más grande para saquear incursiones completas."},
            {"name": "🔄 Granada de Humo Táctica RDG-2B", "category": "BARTER", "cost": "1x Cerillas (Matches)", "is_barter": True, "limit": "5 por reset", "image_key": "p_gp25", "desc": "Ideal para cubrir extracciones abiertas."},
            {"name": "🔄 Lanzagranadas Acoplado GP-25 Kostyor", "category": "BARTER", "cost": "2x Bitcoin + 1x Llave Militar", "is_barter": True, "limit": "1 por reset", "image_key": "p_gp25", "desc": "Lanzagranadas acoplado para fusiles AK."}
        ]
    },
    "Therapist": {
        1: [
            {"name": "Botiquín AI-2 'Quesito'", "category": "MÉDICO", "cost": "3,800 ₽", "is_barter": False, "limit": "10 por reset", "image_key": "gs_1", "desc": "Cura rápida de 100 HP para extremidades."},
            {"name": "Venda Aséptica Médica", "category": "MÉDICO", "cost": "2,100 ₽", "is_barter": False, "limit": "8 por reset", "image_key": "gs_2", "desc": "Detiene sangrados leves de inmediato."},
            {"name": "Férula Inmovilizadora (Splint)", "category": "MÉDICO", "cost": "1,900 ₽", "is_barter": False, "limit": "8 por reset", "image_key": "gs_3", "desc": "Repara fracturas en brazos y piernas."},
            {"name": "Analgésicos en Tabletas (Analgin)", "category": "MÉDICO", "cost": "4,200 ₽", "is_barter": False, "limit": "5 por reset", "image_key": "gs_4", "desc": "Permite correr con piernas fracturadas."},
            {"name": "Botiquín de Automóvil (Car Kit)", "category": "MÉDICO", "cost": "9,600 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "gs_5", "desc": "220 HP y cura sangrados leves."},
            {"name": "🔄 Botiquín Salewa First Aid", "category": "BARTER", "cost": "2x Encendedores + 1x Cerillas", "is_barter": True, "limit": "3 por reset", "image_key": "gs_6", "desc": "400 HP de salud y cura sangrados graves. Clave para quest."},
            {"name": "🔄 Botella de Agua Pura 0.6L", "category": "PROVISIÓN", "cost": "1x Lata de Frijoles", "is_barter": True, "limit": "5 por reset", "image_key": "gs_7", "desc": "Recupera 60 de hidratación."}
        ],
        2: [
            {"name": "Botiquín Salewa First Aid Kit", "category": "MÉDICO", "cost": "32,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_6", "desc": "El mejor botiquín estándar de 400 HP."},
            {"name": "Botiquín Individual IFAK", "category": "MÉDICO", "cost": "22,500 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_8", "desc": "Botiquín compacto de 1 casilla (300 HP)."},
            {"name": "Kit Quirúrgico CMS (5 usos)", "category": "MÉDICO", "cost": "26,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_9", "desc": "Restaura extremidades destruidas (estómago, brazos, piernas)."},
            {"name": "Bálsamo Labial Vaselina", "category": "MÉDICO", "cost": "18,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_10", "desc": "Efecto analgésico prolongado de 300 segundos."},
            {"name": "Contenedor Lucky Scav Junkbox", "category": "CONTENEDOR", "cost": "1,105,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "gs_11", "desc": "Caja gigante de 196 casillas para guardar todo el loot y barters."},
            {"name": "🔄 Torniquete Hemostático CALOK-B", "category": "BARTER", "cost": "1x Cinta Aislante (Tape)", "is_barter": True, "limit": "4 por reset", "image_key": "gs_12", "desc": "Cura instantánea de sangrados abundantes (3 usos)."}
        ],
        3: [
            {"name": "Botiquín Médico Pesado Grizzly (1800 HP)", "category": "MÉDICO", "cost": "58,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_13", "desc": "Cura todo: fracturas, sangrados leves y graves, y 1800 HP."},
            {"name": "Kit Quirúrgico Avanzado Surv12 (15 usos)", "category": "MÉDICO", "cost": "48,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_14", "desc": "Repara miembros en negro y también fracturas."},
            {"name": "Bálsamo Golden Star 'Estrella Dorada'", "category": "MÉDICO", "cost": "38,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_15", "desc": "El mejor analgésico: 350s de duración y da energía/hidratación."},
            {"name": "Inyector de Morfina", "category": "MÉDICO", "cost": "21,000 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "gs_16", "desc": "Efecto analgésico de 0 segundos de aplicación."},
            {"name": "🔄 Maletín de Objetos (Items Case)", "category": "BARTER", "cost": "20x Botellas de Agua de Ophthalmoscope", "is_barter": True, "limit": "1 por reset", "image_key": "gs_17", "desc": "Expansión masiva de 64 casillas para el alijo."}
        ],
        4: [
            {"name": "Maletín de Inyectores (Injector Case)", "category": "CONTENEDOR", "cost": "285,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "gs_18", "desc": "Almacena hasta 9 estimulantes en 1 sola casilla del contenedor seguro."},
            {"name": "Inyector Propital (Regeneración)", "category": "MÉDICO", "cost": "35,000 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "gs_19", "desc": "Cura 1 HP por segundo durante 300 segundos continuos."},
            {"name": "Inyector Zagustin (Anti-sangrado)", "category": "MÉDICO", "cost": "42,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_20", "desc": "Inmunidad total a sangrados durante todo el combate."},
            {"name": "Inyector SJ6 T&G (Resistencia Infinita)", "category": "MÉDICO", "cost": "48,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_21", "desc": "Sprint continuo sin cansancio para llegar a las mejores salas de loot."},
            {"name": "🔄 Contenedor T.H.I.C.C. Items Case", "category": "BARTER", "cost": "15x Desfibriladores + 15x LEDX", "is_barter": True, "limit": "1 por reset", "image_key": "gs_22", "desc": "El contenedor más valioso del juego (196 slots en 15 casillas)."}
        ]
    },
    "Skier": {
        1: [
            {"name": "Carabina VPO-209 .366 TKM", "category": "ARMA", "cost": "32,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "rd_704", "desc": "Versión civil de AKM con gran daño a distancias cortas."},
            {"name": "Escopeta TOZ-106 20/70", "category": "ARMA", "cost": "8,900 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "saiga_12", "desc": "Escopeta ultracompacta de cerrojo muy barata."},
            {"name": "Tapa de Cajón de Mecanismos Bastion", "category": "ACCESORIO", "cost": "6,400 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_b10m", "desc": "Riel superior Picatinny para montar miras ópticas en fusiles AK."},
            {"name": "Adaptador de Culata Rotor 43 AK", "category": "ACCESORIO", "cost": "9,200 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_moe_stock", "desc": "Permite colocar culatas telescópicas tipo AR en plataformas AK."},
            {"name": "🔄 Mochila Militar VKBO (20 Casillas)", "category": "BARTER", "cost": "2x Paquetes de Cigarrillos Malboro", "is_barter": True, "limit": "2 por reset", "image_key": "gs_1", "desc": "Mochila táctica rusa de camuflaje digital."}
        ],
        2: [
            {"name": "Rifle Kel-Tec RFB 7.62x51 OTAN", "category": "ARMA", "cost": "54,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "sr_25", "desc": "Bullpup semiautomático económico en potente calibre .308."},
            {"name": "Fusil Molot VPO-136 Vepr-KM 7.62x39", "category": "ARMA", "cost": "39,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "rd_704", "desc": "Plataforma AKM semiautomática de gran precisión."},
            {"name": "Munición .366 TKM EKO Perforante (90x)", "category": "MUNICIÓN", "cost": "27,000 ₽", "is_barter": False, "limit": "90 por reset", "image_key": "gs_2", "desc": "Bala con núcleo de zinc de alta velocidad contra blindaje clase 3."},
            {"name": "Guardamanos con Riel UltiMAK M1-B", "category": "ACCESORIO", "cost": "11,500 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_b10m", "desc": "Tubo de gases con riel para colimadores compactos."},
            {"name": "🔄 Fusil Bullpup Desert Tech MDR 5.56x45", "category": "BARTER", "cost": "3x Cadenas de Oro (Gold Chains)", "is_barter": True, "limit": "1 por reset", "image_key": "mk47_mutant", "desc": "Trueque excelente para conseguir un fusil OTAN de alta gama."}
        ],
        3: [
            {"name": "Fusil de Combate DSA SA-58 7.62x51", "category": "ARMA", "cost": "78,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "sr_25", "desc": "FAL moderno con fuego automático y tambores de 50 tiros."},
            {"name": "Carabina CMMG Mk47 Mutant 7.62x39", "category": "ARMA", "cost": "92,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "mk47_mutant", "desc": "La mezcla perfecta: ergonomía de M4 disparando 7.62 ruso."},
            {"name": "Munición .366 TKM AP-M Perforante (60x)", "category": "MUNICIÓN", "cost": "54,000 ₽", "is_barter": False, "limit": "60 por reset", "image_key": "gs_3", "desc": "Penetración 42: liquida objetivos de un impacto al tórax."},
            {"name": "Compensador Lantac Dragon 7.62x39", "category": "ACCESORIO", "cost": "18,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_dtk4m", "desc": "Reducción masiva del retroceso vertical para AK y Mk47."},
            {"name": "🔄 Contenedor de Armas Weapon Case", "category": "BARTER", "cost": "10x Monedas de Plata + 8x Relojes Rotos", "is_barter": True, "limit": "1 por reset", "image_key": "gs_4", "desc": "Caja para organizar hasta 25 fusiles en el inventario."}
        ],
        4: [
            {"name": "Fusil Desert Tech MDR 7.62x51 Meta", "category": "ARMA", "cost": "148,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "sr_25", "desc": "Una de las mejores armas del juego: compacta y letal en .308."},
            {"name": "Fusil FN SCAR-H 7.62x51 FDE", "category": "ARMA", "cost": "135,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "sr_25", "desc": "Fusil de asalto pesado de fuerzas especiales con retroceso predecible."},
            {"name": "Munición 7.62x51 M80 Perforante (100x)", "category": "MUNICIÓN", "cost": "85,000 ₽", "is_barter": False, "limit": "100 por reset", "image_key": "gs_5", "desc": "El estándar de oro para incursiones de alto nivel."},
            {"name": "Silenciador Híbrido Gemtech ONE", "category": "ACCESORIO", "cost": "52,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "p_hybrid46", "desc": "Supresión de sonido multipropósito de titanio."},
            {"name": "🔄 Caja T.H.I.C.C. Weapon Case (Skier)", "category": "BARTER", "cost": "2x Bitcoin + 500x Euros + 2x Tarjeta Acceso", "is_barter": True, "limit": "1 por reset", "image_key": "gs_6", "desc": "Espacio masivo para armamento pesado modificado."}
        ]
    },
    "Peacekeeper": {
        1: [
            {"name": "Pistola Beretta M9A3 9x19", "category": "ARMA", "cost": "$ 125 USD", "is_barter": False, "limit": "4 por reset", "image_key": "p226", "desc": "Pistola militar OTAN moderna y precisa."},
            {"name": "Subfusil HK MP5 9x19", "category": "ARMA", "cost": "$ 295 USD", "is_barter": False, "limit": "2 por reset", "image_key": "mp7a2", "desc": "Subfusil legendario con mínimo retroceso vertical."},
            {"name": "Munición 9x19 PST gzh (150x)", "category": "MUNICIÓN", "cost": "$ 110 USD", "is_barter": False, "limit": "150 por reset", "image_key": "gs_1", "desc": "Proyectil estándar OTAN con penetración balanceada."},
            {"name": "Munición 5.56x45 M855 (120x)", "category": "MUNICIÓN", "cost": "$ 180 USD", "is_barter": False, "limit": "120 por reset", "image_key": "gs_2", "desc": "Bala básica penetrante con punta de acero verde."},
            {"name": "Chaleco Ligero PACA Soft Armor", "category": "ARMADURA", "cost": "$ 190 USD", "is_barter": False, "limit": "3 por reset", "image_key": "gs_3", "desc": "Protección blanda clase 2 contra escopetas y scavs."},
            {"name": "🔄 Carabina Colt M4A1 5.56x45", "category": "BARTER", "cost": "3x Cuchillos Scav (Brown Handle)", "is_barter": True, "limit": "2 por reset", "image_key": "mk47_mutant", "desc": "Trueque clásico muy barato para conseguir una M4 completa."}
        ],
        2: [
            {"name": "Carabina Colt M4A1 5.56x45", "category": "ARMA", "cost": "$ 550 USD", "is_barter": False, "limit": "2 por reset", "image_key": "mk47_mutant", "desc": "La plataforma más modular de Escape from Tarkov."},
            {"name": "Subfusil SIG MPX 9x19", "category": "ARMA", "cost": "$ 420 USD", "is_barter": False, "limit": "2 por reset", "image_key": "mp7a2", "desc": "Excelente ergonomía y estabilidad para combate cercano."},
            {"name": "Munición 5.56x45 M856A1 Trazadora (90x)", "category": "MUNICIÓN", "cost": "$ 240 USD", "is_barter": False, "limit": "90 por reset", "image_key": "gs_4", "desc": "Bala trazadora de gran capacidad contra chalecos clase 4."},
            {"name": "Mira Holográfica EOTech XPS3-0", "category": "ÓPTICA", "cost": "$ 175 USD", "is_barter": False, "limit": "3 por reset", "image_key": "p_exps3", "desc": "Retícula limpia de punto rojo con anillo protector."},
            {"name": "Chaleco Blindado UNTAR Azul (Clase 3)", "category": "ARMADURA", "cost": "$ 320 USD", "is_barter": False, "limit": "2 por reset", "image_key": "gs_5", "desc": "Requerido para múltiples misiones de cascos azules."},
            {"name": "🔄 Supresor SilencerCo Hybrid 46", "category": "BARTER", "cost": "2x Memorias RAM", "is_barter": True, "limit": "2 por reset", "image_key": "p_hybrid46", "desc": "Silenciador multi-calibre adaptable a rifles OTAN."}
        ],
        3: [
            {"name": "Rifle de Precisión KAC SR-25 7.62x51", "category": "ARMA", "cost": "$ 1,100 USD", "is_barter": False, "limit": "2 por reset", "image_key": "sr_25", "desc": "El DMR meta por excelencia en calibre 7.62x51 OTAN."},
            {"name": "Fusil Bullpup DT MDR 5.56x45", "category": "ARMA", "cost": "$ 780 USD", "is_barter": False, "limit": "2 por reset", "image_key": "mk47_mutant", "desc": "Diseño bullpup corto con ergonomía nativa altísima."},
            {"name": "Munición 5.56x45 M855A1 (90x)", "category": "MUNICIÓN", "cost": "$ 410 USD", "is_barter": False, "limit": "90 por reset", "image_key": "gs_6", "desc": "La bala meta de penetración clase 5 en calibre 5.56."},
            {"name": "Munición 7.62x51 BCP FMJ (100x)", "category": "MUNICIÓN", "cost": "$ 350 USD", "is_barter": False, "limit": "100 por reset", "image_key": "gs_7", "desc": "Fuerte daño base y perforación confiable."},
            {"name": "Chaleco Porta-placas Crye AVS (Clase 4)", "category": "ARMADURA", "cost": "$ 890 USD", "is_barter": False, "limit": "2 por reset", "image_key": "gs_8", "desc": "Rig blindado con distribución de bolsillos espaciosa."},
            {"name": "🔄 Cargador de Tambor Magpul D-60 60 tiros", "category": "BARTER", "cost": "2x Filtro de Aire Militar", "is_barter": True, "limit": "2 por reset", "image_key": "p_pmag_d60", "desc": "60 tiros sin recargar para M4A1 y HK416."}
        ],
        4: [
            {"name": "Rifle de Precisión Remington RSASS 7.62x51", "category": "ARMA", "cost": "$ 1,600 USD", "is_barter": False, "limit": "1 por reset", "image_key": "sr_25", "desc": "DMR de francotirador pesado de máxima precisión a 500m."},
            {"name": "Fusil de Asalto SIG MCX .300 Blackout", "category": "ARMA", "cost": "$ 1,250 USD", "is_barter": False, "limit": "2 por reset", "image_key": "mk47_mutant", "desc": "Dispara calibre .300 BLK con alto impacto cercano."},
            {"name": "Munición 7.62x51 M62 Tracer Perforante", "category": "MUNICIÓN", "cost": "$ 750 USD", "is_barter": False, "limit": "60 por reset", "image_key": "gs_9", "desc": "Bala trazadora capaz de perforar blindajes clase 5 y 6."},
            {"name": "Chaleco Blindado Osprey MK4 Assault (Clase 5)", "category": "ARMADURA", "cost": "$ 1,450 USD", "is_barter": False, "limit": "1 por reset", "image_key": "gs_10", "desc": "Armadura de asalto pesada de las fuerzas británicas."},
            {"name": "Visor Nocturno GPNVG-18 Cuádruple Tubo", "category": "VISIÓN NOCTURNA", "cost": "$ 3,200 USD", "is_barter": False, "limit": "1 por reset", "image_key": "gs_11", "desc": "Campo visual panorámico sin efecto de túnel."},
            {"name": "🔄 Maletín T.H.I.C.C. Weapon Case", "category": "BARTER", "cost": "2x Bitcoin + 10x Monedas GP + 1x Tarjeta Labs", "is_barter": True, "limit": "1 por reset", "image_key": "gs_12", "desc": "Almacena más de 40 armas modificadas."}
        ]
    },
    "Mechanic": {
        1: [
            {"name": "Pistola Glock 17 9x19", "category": "ARMA", "cost": "18,500 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p226", "desc": "Pistola austríaca confiable con múltiples miras ópticas."},
            {"name": "Escopeta MP-133 12/70", "category": "ARMA", "cost": "21,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "saiga_12", "desc": "Escopeta de bombeo necesaria para la quest Gunsmith Part 1."},
            {"name": "Empuñadura Táctica Zenit RK-6", "category": "ACCESORIO", "cost": "7,800 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "p_kac_vfg", "desc": "Grip corto que suma +6 de ergonomía."},
            {"name": "Riel Guardamanos Zenit B-10M", "category": "ACCESORIO", "cost": "12,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_b10m", "desc": "Permite acoplar empuñaduras y linternas a la serie AK."},
            {"name": "Mira Punto Rojo Micro T-1", "category": "ÓPTICA", "cost": "16,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_micro_t1", "desc": "Óptica compacta y nítida."},
            {"name": "🔄 Escopeta MP-133 Táctica Modificada", "category": "BARTER", "cost": "1x Disco Rígido + 1x Batería Recargable", "is_barter": True, "limit": "1 por reset", "image_key": "saiga_12", "desc": "Lista con empuñadura y guardamanos para Gunsmith 1."}
        ],
        2: [
            {"name": "Subfusil KRISS Vector 9x19", "category": "ARMA", "cost": "72,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "mp7a2", "desc": "Cadencia extrema de 950 RPM con retroceso nulo."},
            {"name": "Subfusil FN P90 5.7x28", "category": "ARMA", "cost": "68,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "mp7a2", "desc": "Cargador horizontal de 50 tiros perforante."},
            {"name": "Munición 9x19 AP 6.3 Perforante (90x)", "category": "MUNICIÓN", "cost": "48,000 ₽", "is_barter": False, "limit": "90 por reset", "image_key": "gs_1", "desc": "Bala perforadora de chalecos clase 3 y 4."},
            {"name": "Mira Óptica Táctica Vortex Razor HD 1-6x", "category": "ÓPTICA", "cost": "62,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "p_vudu", "desc": "Claridad cristalina para combate a cualquier distancia."},
            {"name": "Culata Ergonómica Magpul CTR", "category": "ACCESORIO", "cost": "19,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_moe_stock", "desc": "Reduce retroceso y maximiza la velocidad de apuntado."},
            {"name": "🔄 Mira Óptica EOTech Vudu 1-6x24", "category": "BARTER", "cost": "2x Placas de Circuitos (Circuit Boards)", "is_barter": True, "limit": "2 por reset", "image_key": "p_vudu", "desc": "La mira variable más codiciada de Tarkov."}
        ],
        3: [
            {"name": "Rifle de Francotirador DVL-10 Urbana .308", "category": "ARMA", "cost": "98,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "sr_25", "desc": "El fusil de cerrojo más silencioso del mundo."},
            {"name": "Fusil de Asalto HK416A5 5.56x45", "category": "ARMA", "cost": "88,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "mk47_mutant", "desc": "850 disparos por minuto con tecnología de pistón de gas."},
            {"name": "Rifle Semiautomático Springfield M1A 7.62x51", "category": "ARMA", "cost": "78,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "sr_25", "desc": "Poder masivo en combate medio y lejano."},
            {"name": "Munición .45 ACP AP Perforante (70x)", "category": "MUNICIÓN", "cost": "44,000 ₽", "is_barter": False, "limit": "70 por reset", "image_key": "gs_2", "desc": "Hace del subfusil UMP-45 una máquina letal."},
            {"name": "Silenciador Avanzado AAC 762 SDN-6", "category": "ACCESORIO", "cost": "42,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_dtk4m", "desc": "Supresión de sonido para calibres .308 y 7.62."},
            {"name": "🔄 Caja de Municiones Ammo Box", "category": "BARTER", "cost": "1x Tarjeta Gráfica Dañada + 2x Relés", "is_barter": True, "limit": "1 por reset", "image_key": "gs_3", "desc": "Capacidad para más de 1200 proyectiles sueltos."}
        ],
        4: [
            {"name": "Mira Térmica Trijicon REAP-IR", "category": "TÉRMICO", "cost": "290,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "p_vudu", "desc": "Detecta la firma de calor de los enemigos a través de la niebla."},
            {"name": "Fusil de Asalto CMMG Mk47 Mutant Meta", "category": "ARMA", "cost": "165,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "mk47_mutant", "desc": "Construcción completa con piezas listas para Gunsmith."},
            {"name": "Caja de Armas (Weapon Case)", "category": "CONTENEDOR", "cost": "650,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "gs_4", "desc": "Espacio para guardar 50 fusiles ocupando solo 10 slots."},
            {"name": "Cargador Tambor X-50 50 tiros 7.62x51", "category": "ACCESORIO", "cost": "55,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "p_x5_drum", "desc": "50 tiros sin recargar para armas como SR-25 o SA-58."},
            {"name": "🔄 Mira Térmica FLIR RS-32", "category": "BARTER", "cost": "10x Tubos de Gas + 5x Cables Militares", "is_barter": True, "limit": "1 por reset", "image_key": "p_vudu", "desc": "Visión infrarroja continua sin retraso de fotogramas."}
        ]
    },
    "Ragman": {
        1: [
            {"name": "Pasamontañas Táctico Balaclava", "category": "EQUIPO", "cost": "3,400 ₽", "is_barter": False, "limit": "5 por reset", "image_key": "gs_1", "desc": "Oculta el brillo de la cara frente a francotiradores."},
            {"name": "Chaleco Táctico Scav Vest", "category": "CHALECO", "cost": "6,500 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "gs_2", "desc": "Rig básico de 6 casillas. Necesario para misiones de matar con Scav Vest."},
            {"name": "Chaleco Táctico Bank Robber", "category": "CHALECO", "cost": "9,800 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "gs_3", "desc": "8 casillas para cargadores y botiquín."},
            {"name": "Mochila MBSS (16 Casillas)", "category": "MOCHILA", "cost": "14,500 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_4", "desc": "Mochila ligera sin penalización de velocidad."},
            {"name": "Casco Kolpak-1S (Clase 2)", "category": "CASCO", "cost": "11,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_5", "desc": "Protección para dispersión de perdigones de escopeta."},
            {"name": "🔄 Mochila Duffle Bag", "category": "BARTER", "cost": "1x Paquete de Fideos", "is_barter": True, "limit": "3 por reset", "image_key": "gs_6", "desc": "Mochila civil barata para incursiones de scavenging."}
        ],
        2: [
            {"name": "Armadura Porta-Placas 6B3TM (Clase 4)", "category": "ARMADURA", "cost": "55,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_7", "desc": "El chaleco blindado económico por excelencia de inicio de wipe."},
            {"name": "Auriculares Tácticos Sordin Supreme Pro-X", "category": "AURICULARES", "cost": "28,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_8", "desc": "Atenúa detonaciones y amplifica los pasos de enemigos."},
            {"name": "Auriculares Peltor ComTac 2", "category": "AURICULARES", "cost": "24,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_9", "desc": "Compresión acústica balanceada para interiores."},
            {"name": "Mochila Táctica Berkut (20 Casillas)", "category": "MOCHILA", "cost": "24,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_10", "desc": "Espacio suficiente para armas medianas desarmadas."},
            {"name": "Chaleco Táctico Wartech TV-109", "category": "CHALECO", "cost": "26,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "gs_11", "desc": "18 casillas útiles organizadas en 4 slots dobles."},
            {"name": "🔄 Casco 6B47 Camuflado", "category": "BARTER", "cost": "2x Blanqueador (Bleach)", "is_barter": True, "limit": "2 por reset", "image_key": "gs_12", "desc": "Casco militar clase 3 con alta probabilidad de rebote."}
        ],
        3: [
            {"name": "Chaleco Porta-Placas TV-110 (Clase 4)", "category": "ARMADURA", "cost": "88,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_13", "desc": "Rig blindado de 23 casillas, excelente protección y espacio."},
            {"name": "Casco Táctico MSA ACH TC-2001 (Clase 3)", "category": "CASCO", "cost": "44,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_14", "desc": "Permite usar cualquier auricular sin interferencia."},
            {"name": "Mochila Militar Tri-Zip (30 Casillas)", "category": "MOCHILA", "cost": "48,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_15", "desc": "Estructura rígida para trasladar chalecos de enemigos."},
            {"name": "Gafas Tácticas Antidestello Condor", "category": "EQUIPO", "cost": "18,000 ₽", "is_barter": False, "limit": "4 por reset", "image_key": "gs_16", "desc": "Blindaje clase 1 para los ojos capaz de salvarte de perdigones."},
            {"name": "🔄 Chaleco Blindado CPC MOD.1 (Clase 5)", "category": "BARTER", "cost": "3x Rollos de Cordura + 2x Ripstop", "is_barter": True, "limit": "1 por reset", "image_key": "gs_17", "desc": "Uno de los mejores rigs clase 5 del juego."},
            {"name": "🔄 Casco Pesado Altyn con Visera de Acero", "category": "BARTER", "cost": "4x Tarros de Pólvora Militar", "is_barter": True, "limit": "1 por reset", "image_key": "gs_18", "desc": "El casco más temido en combate cuerpo a cuerpo."}
        ],
        4: [
            {"name": "Armadura Pesada Slick Body Armor (Clase 6)", "category": "ARMADURA", "cost": "240,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "gs_19", "desc": "Placas de acero blindado clase 6 con penalización mínima."},
            {"name": "Armadura Hexgrid Plate Carrier (Clase 6)", "category": "ARMADURA", "cost": "260,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "gs_20", "desc": "Material UHMWPE con la mejor tasa de reparación del juego."},
            {"name": "Casco Crye Precision Airframe (Clase 4)", "category": "CASCO", "cost": "125,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "gs_21", "desc": "Soporta protección de mandíbula (Chops) y orejeras adicionales."},
            {"name": "Mochila Militar Attack 2 (35 Casillas)", "category": "MOCHILA", "cost": "85,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "gs_22", "desc": "Gran capacidad con compartimiento vertical para armas largas."},
            {"name": "🔄 Visera Blindada para Casco Altyn (Clase 5)", "category": "BARTER", "cost": "2x Plexiglas + 1x Llave Rara", "is_barter": True, "limit": "1 por reset", "image_key": "gs_23", "desc": "Protección frontal que detiene balas de fusil."},
            {"name": "🔄 Maletín de Ropa y Rigs (Thicc T.H.I.C.C.)", "category": "BARTER", "cost": "10x Botellas de Moonshine + 15x Vodka", "is_barter": True, "limit": "1 por reset", "image_key": "gs_24", "desc": "Ahorra cientos de casillas en el alijo para vestimentas."}
        ]
    },
    "Jaeger": {
        1: [
            {"name": "Rifle Mosin Infantería 7.62x54R", "category": "ARMA", "cost": "38,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "sr_25", "desc": "Poder mortal a larga distancia desde el primer día."},
            {"name": "Rifle Monotiro MP-18 7.62x54R", "category": "ARMA", "cost": "19,500 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "sr_25", "desc": "Opción ultra económica de francotirador silencioso."},
            {"name": "Carabina VPO-215 Gornostay .366 TKM", "category": "ARMA", "cost": "22,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "sr_25", "desc": "Fusil de cerrojo ligero para cazar Scavs."},
            {"name": "Munición 12/70 Magnum Buckshot (60x)", "category": "MUNICIÓN", "cost": "12,000 ₽", "is_barter": False, "limit": "60 por reset", "image_key": "gs_1", "desc": "8 perdigones con 50 de daño cada uno. El rey del Leg Meta."},
            {"name": "🔄 Kit Quirúrgico CMS", "category": "BARTER", "cost": "1x Lata de Arenque + 1x Cinta Blanca", "is_barter": True, "limit": "2 por reset", "image_key": "gs_2", "desc": "Trueque barato para reponer kits de cirugía médica."}
        ],
        2: [
            {"name": "Rifle de Precisión SV-98 7.62x54R", "category": "ARMA", "cost": "52,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "sr_25", "desc": "Cargador desmontable de 10 tiros y disparador suave."},
            {"name": "Carabina de Caza SKS Hunting 7.62x39", "category": "ARMA", "cost": "36,000 ₽", "is_barter": False, "limit": "2 por reset", "image_key": "rd_704", "desc": "Precisión y cadencia semiautomática constante."},
            {"name": "Munición 7.62x54R LPS (90x)", "category": "MUNICIÓN", "cost": "38,000 ₽", "is_barter": False, "limit": "90 por reset", "image_key": "gs_3", "desc": "Penetración contundente contra cascos y chalecos."},
            {"name": "Mira Réflex Holosun HS401G5 con Láser", "category": "ÓPTICA", "cost": "26,000 ₽", "is_barter": False, "limit": "3 por reset", "image_key": "p_micro_t1", "desc": "Punto verde y módulo láser integrado."},
            {"name": "🔄 Cartera Porta-Documentos (Docs Case)", "category": "BARTER", "cost": "1x Estatua de Caballo + 1x Tetriz", "is_barter": True, "limit": "1 por reset", "image_key": "gs_4", "desc": "Guarda llaves, tarjetas, dinero e inteligencia en el contenedor seguro."}
        ],
        3: [
            {"name": "Rifle de Cerrojo Accuracy AXMC .338 Lapua", "category": "ARMA", "cost": "180,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "sr_25", "desc": "El calibre más demoledor del juego: fulmina de un tiro al tórax."},
            {"name": "Munición 12/70 AP-20 Armor Piercing Slug", "category": "MUNICIÓN", "cost": "42,000 ₽", "is_barter": False, "limit": "40 por reset", "image_key": "gs_5", "desc": "Bala única de escopeta con penetración clase 4/5."},
            {"name": "Munición .366 TKM AP-M (Perforante)", "category": "MUNICIÓN", "cost": "46,000 ₽", "is_barter": False, "limit": "50 por reset", "image_key": "gs_6", "desc": "Convierte la VPO-215 en una máquina de matar de un tiro al pecho."},
            {"name": "🔄 Estuche SICC Case (Small Items Case)", "category": "BARTER", "cost": "10x Paracord + 15x Cinta Azul + 1x Rollo Alambre", "is_barter": True, "limit": "1 por reset", "image_key": "gs_7", "desc": "El mejor contenedor de llaves y dogtags para el bolsillo seguro."}
        ],
        4: [
            {"name": "Fusil Semiautomático SWORD Mk-18 Mjölnir .338", "category": "ARMA", "cost": "380,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "sr_25", "desc": "El arma más poderosa de Tarkov: semiautomática en .338 Lapua."},
            {"name": "Munición .338 Lapua Magnum AP Perforante", "category": "MUNICIÓN", "cost": "120,000 ₽", "is_barter": False, "limit": "30 por reset", "image_key": "gs_8", "desc": "Penetración 79: atraviesa cualquier casco clase 6 como manteca."},
            {"name": "Piolet de Escalada Red Rebel Ice Pick", "category": "CUERPO A CUERPO", "cost": "350,000 ₽", "is_barter": False, "limit": "1 por reset", "image_key": "gs_9", "desc": "Permite extraer por Cliff Descent en Reserve y Mountain Pass en Lighthouse."},
            {"name": "🔄 Piolet Red Rebel Ice Pick (Trueque)", "category": "BARTER", "cost": "3x Tanques de Propano + 10x Combustible + 15x Lejía", "is_barter": True, "limit": "1 por reset", "image_key": "gs_9", "desc": "El trueque más codiciado para no arriesgarse en trenes o búnkeres."}
        ]
    },
    "Ref": {
        1: [
            {"name": "Llave de Arena de Tarkov", "category": "LLAVE", "cost": "2x Monedas GP", "is_barter": True, "limit": "2 por reset", "image_key": "gs_1", "desc": "Abre salas exclusivas de la Arena en las calles de Tarkov."},
            {"name": "Pistola Automática Stetchkin APS Arena", "category": "ARMA", "cost": "3x Monedas GP", "is_barter": True, "limit": "2 por reset", "image_key": "p226", "desc": "Pistola automática para combate rápido."},
            {"name": "Caja de Suministros Arena Nivel 1", "category": "CONTENEDOR", "cost": "4x Monedas GP", "is_barter": True, "limit": "3 por reset", "image_key": "gs_2", "desc": "Contiene munición especial y suministros médicos."}
        ],
        2: [
            {"name": "Fusil de Asalto AK-105 Arena Preset", "category": "ARMA", "cost": "6x Monedas GP", "is_barter": True, "limit": "2 por reset", "image_key": "ak74m", "desc": "Carabina modificada con empuñadura y silenciador."},
            {"name": "Armadura Corporal Gladiador Arena (Clase 4)", "category": "ARMADURA", "cost": "7x Monedas GP", "is_barter": True, "limit": "2 por reset", "image_key": "gs_3", "desc": "Armadura de alta movilidad para duelos 1v1."}
        ],
        3: [
            {"name": "Subfusil MP5SD con Tambor 50 tiros", "category": "ARMA", "cost": "10x Monedas GP", "is_barter": True, "limit": "2 por reset", "image_key": "mp7a2", "desc": "Silenciador integral y cargador extendido de torneo."},
            {"name": "Munición 9x19 PBP Gzh Perforante (60x)", "category": "MUNICIÓN", "cost": "8x Monedas GP", "is_barter": True, "limit": "60 por reset", "image_key": "gs_4", "desc": "Perforación superior de armaduras pesadas."}
        ],
        4: [
            {"name": "Fusil de Precisión DVL-10 Campeón Arena", "category": "ARMA", "cost": "18x Monedas GP", "is_barter": True, "limit": "1 por reset", "image_key": "sr_25", "desc": "Preset legendario con mira óptica de torneo y pintura única."},
            {"name": "Chaleco Blindado de Campeón (Clase 5)", "category": "ARMADURA", "cost": "20x Monedas GP", "is_barter": True, "limit": "1 por reset", "image_key": "gs_5", "desc": "Material de polietileno ultraligero con resistencia extrema."}
        ]
    },
    "Fence": {
        1: [
            {"name": "Armas de Scav Usadas (Durabilidad 50-70%)", "category": "ARMA", "cost": "15,000 — 40,000 ₽", "is_barter": False, "limit": "Aleatorio", "image_key": "saiga_12", "desc": "Armas dejadas por otros jugadores o bots."},
            {"name": "Municiones Sueltas y Cargadores Mixtos", "category": "MUNICIÓN", "cost": "3,000 — 12,000 ₽", "is_barter": False, "limit": "Aleatorio", "image_key": "gs_1", "desc": "Restos de munición rescatados del campo de batalla."}
        ],
        2: [
            {"name": "Pases de Transporte para el Blindado BTR", "category": "SERVICIO", "cost": "25,000 ₽", "is_barter": False, "limit": "5 por reset", "image_key": "btr_driver", "desc": "Permite enviar el botín directamente a tu alijo desde el BTR en Streets y Woods."},
            {"name": "Descuento del 15% en Extracciones de Pago (V-Ex)", "category": "PASIVO", "cost": "Pasivo Karma +2.0", "is_barter": False, "limit": "Permanente", "image_key": "gs_2", "desc": "Reduce el costo de los coches de extracción a 4,250 ₽."}
        ],
        3: [
            {"name": "Reducción del 30% en Enfriamiento del Scav", "category": "PASIVO", "cost": "Pasivo Karma +4.0", "is_barter": False, "limit": "Permanente", "image_key": "gs_3", "desc": "Permite jugar con tu Player Scav cada 10 minutos."},
            {"name": "Equipo Militar No Reclamado del Seguro", "category": "EQUIPO", "cost": "45,000 — 120,000 ₽", "is_barter": False, "limit": "Aleatorio", "image_key": "gs_4", "desc": "Cascos y chalecos clase 4 y 5 perdidos en incursiones."}
        ],
        4: [
            {"name": "Corona Scav VIP: Acceso al Loot No Asegurado", "category": "TIENDA VIP", "cost": "Precios con 30% Descuento", "is_barter": False, "limit": "Acceso Total", "image_key": "gs_5", "desc": "Pestaña secreta con todo el equipo de PMCs que murieron sin seguro."},
            {"name": "Inmunidad Total: Los Jefes y Scavs son tus Aliados", "category": "PASIVO", "cost": "Pasivo Karma +6.0", "is_barter": False, "limit": "Permanente", "image_key": "gs_6", "desc": "Killa, Tagilla, Reshala y Glukhar te protegen y pelean a tu lado."}
        ]
    }
}


def get_trader_assortment(trader_name: str, loyalty_level: int) -> List[Dict[str, Any]]:
    """Retorna la lista de ítems y trueques para un comerciante y nivel de afinidad."""
    trader_data = TRADER_ASSORTMENT_DATA.get(trader_name, {})
    return trader_data.get(loyalty_level, [])


def get_trader_requirements(trader_name: str, loyalty_level: int) -> Dict[str, Any]:
    """Retorna los requisitos de nivel, reputación y gasto para un nivel de afinidad."""
    reqs = TRADER_LL_REQUIREMENTS.get(trader_name, {})
    return reqs.get(loyalty_level, {"level": 1, "rep": 0.0, "spend": 0, "title": f"Nivel {loyalty_level}"})
