# 🎯 TarkovScope (v1.0) — Asistente Táctico de Escritorio para Escape from Tarkov

<p align="center">
  <strong>Aplicación de escritorio nativa en Python diseñada para operadores de Escape from Tarkov (PvE & PvP).</strong><br>
  Cero latencia (<1 ms), 100% offline tras primera sincronización, arquitectura limpia y diseño táctico de alto contraste.
</p>

---

## 🚀 Características Principales

### 🛠️ Gunsmith Studio & Modding Interactivo (Workbench)
- **Banco de Armería Militar Dinámico**: El arma cambia visualmente en tiempo real en un plano esquemático táctico al instalar cada accesorio (silenciadores, miras telescópicas/holográficas, cargadores de tambor, empuñaduras, culatas y láseres).
- **Cálculo Balístico Ingame Instantáneo**: Ergonomía (ADS), retroceso vertical y horizontal, masa total (kg) y velocidad de boca en boca de cañón.
- **Catálogo Visual de Ranuras (Quick Slots)**: Selección en 1-clic con imágenes oficiales de cada pieza, impacto de estadísticas y comerciantes.
- **Presets Meta Directos**: Acceso con 1 clic a configuraciones competitivas (*Meta Laser Recoil*, *Budget LL2*, *CQC High Ergo*, *Gunsmith Mechanic*).
- **Exportación Multi-Formato**:
  - `📋 Lista de Compras`: Formato limpio para el portapapeles con comerciantes requeridos (LL1-LL4) y costo total estimado en rublos.
  - `💾 JSON (EFT/SPT)`: Formato estándar `weaponbuilds` para SPT-AKI y editores de perfil.
  - `🔗 Código Base64`: Códigos portables `TTCBUILD:...` para compartir builds al instante.
  - `📥 Importador de Presets`: Carga cualquier build compartida en el taller con un solo clic.

### 🗺️ Ficha Táctica Offline Estilo Wiki para Quests (Zero-Browser)
- **Experiencia 100% Offline**: No requiere abrir el navegador durante las incursiones.
- **Walkthrough Paso a Paso en Español**: Desglosado en 4 fases tácticas (Preparación, Infiltración, Objetivos y Extracción).
- **Plano Topográfico 2D con Retícula Lumínica**: Muestra el sector y POI exacto de la misión sobre el mapa del juego con botón directo al visor a pantalla completa.
- **Fichas de Llaves & Contenedor Seguro**: Datos exactos de aparición de llaves en el mapa, opciones de trueque y compra en comerciantes.
- **Árbol de Progresión**: Prerrequisitos, misiones que desbloquea y estado crítico para el contenedor **KAPPA** y la ruta de **Lightkeeper**.

### 💥 Balística Avanzada & Simulador de Combate (STK)
- Catálogo completo con más de 175 proyectiles y calibres meta (.50 AE, 5.8x42, etc.).
- Simulador de disparos para matar (Shots to Kill - STK) contra armaduras clase 1 a 6.
- Análisis de efectividad en piernas (*Leg Meta*) y simulación contra Bosses de Tarkov.
- Filtro y exclusión inteligente de munición no letal de utilidad (Flares, Zvezda Flashbang).

### 📍 Mapas Tácticos 2D & Radar de Bosses
- Planos topográficos 2D en alta definición de todos los mapas (Customs, Woods, Shoreline, Interchange, Ground Zero, Factory, Reserve, Lighthouse, Streets, Labs e Icebreaker).
- Radares balísticos de spawn de Bosses con porcentajes oficiales calibrados para PvE y PvP (Reshala, Killa, Tagilla, Shturman, Glukhar, Sanitar, Kaban, Kollontay, The Goons, Partisan, Cultists y The Wedge en Icebreaker).
- Capas tácticas de extracciones PMC/Scav, llaves marcadas y cajas fuertes.
- Sistema de colocación y edición de alfileres de usuario (*Pins*) con persistencia en SQLite.

### 📜 Capítulos de Historia & Progresión de Lore
- Los 10 capítulos oficiales de historia con guías paso a paso, imágenes y banners panorámicos.
- Desplazamiento ultra suave acelerado (*Smooth Scroll*) para lectura cómoda sin fatiga.

### 📦 Alijo, Crafteos FiR & Comerciantes
- Inventario completo de los comerciantes en sus niveles LL1 a LL4.
- Tracker de Alijo / Junkbox para acumular objetos con estado *Found in Raid (FiR)* para misiones futuras.
- Guía de crafteos de Hideout y recetas místicas del Círculo Cultista.

---

## 🏛️ Arquitectura y Tecnologías

El proyecto sigue una separación estricta de responsabilidades (Clean Architecture & SOLID):

- **`core/`**: Lógica de negocio pura, cálculo de stats balísticos, exportadores, esquemas SQLite y sincronización GraphQL. Cero dependencias de interfaz gráfica (100% testeable).
- **`ui/`**: Capa de presentación visual construida con CustomTkinter, modales tácticos, renderizado en lotes (*batch rendering*) y paleta táctica unificada (`THEME`).
- **`tests/`**: Suite exhaustiva de pruebas unitarias y de integración (58 tests automáticos).

---

## 💻 Instalación y Uso

### 1. Requisitos Previos
- Python 3.10 o superior instalado.

### 2. Clonar el Repositorio
```bash
git clone https://github.com/TU_USUARIO/TarkovScope.git
cd TarkovScope
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Iniciar la Aplicación
```bash
python TarkovScope.py
```

---

## 🧪 Ejecución de Pruebas Unitarias

Para correr la suite de pruebas unitarias:
```bash
python -m unittest discover -s tests -v
```

Para verificar compilación estricta de sintaxis:
```bash
python -m compileall .
```

---

## 📄 Licencia

Este proyecto es una herramienta de código abierto desarrollada para la comunidad de Escape from Tarkov. Todos los nombres, marcas e imágenes pertenecen a Battlestate Games.
