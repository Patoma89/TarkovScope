# 🎯 TarkovScope — Directrices de Desarrollo Pro en Python

Este repositorio sigue directrices de ingeniería de software de nivel Senior para aplicaciones de escritorio en Python.

---

## 🏛️ Arquitectura del Proyecto (Separación Estricta de Capas)

- **`core/` (Lógica de Negocio Pura)**:
  - Nunca importar CustomTkinter ni Tkinter dentro de `core/`.
  - Debe ser 100% testeable mediante tests unitarios en `tests/`.
  - Módulos: `config.py`, `database.py` (esquema y sincronización), `db_connection.py`, `user_data.py` (progreso, marcadores, alijo, perfil), `quest_seed_data.py`, `quest_guides_data.py` (guías offline, POIs, llaves), `weapon_modding_data.py` (armas base, ranuras, accesorios), `weapon_modding_engine.py` (cálculo de stats, exportación JSON/Base64/lista de compras), `weapon_visual_compositor.py` (blueprint esquemático dinámico militar en tiempo real), `datastore.py`, `sync_service.py`, `ballistics.py`, `ammo_complete_data.py`, `story_quests_data.py`, `maps_data.py`, `weapons_data.py`, `bosses_data.py`, `image_cache.py`, `tactical_map_renderer.py`.
- **`ui/` (Capa de Presentación y Gráficos)**:
  - Componentes visuales, pestañas y modales (`theme.py`, `image_utils.py`, `map_viewer_modal.py`, `quest_guide_modal.py` (Dossier Táctico Wiki Offline 4 pestañas), `tab_quests.py` + `tab_quests_assortment.py`, `tab_maps.py`, `tab_ballistics.py` + `tab_ballistics_duel.py` + `ballistics_common.py`, `tab_story_quests.py` + `tab_story_guide.py`, `tab_weapons.py` + `tab_weapons_builder.py` (Modding Studio Interactivo / Workbench), `tab_bosses.py`, `tab_flea.py` + `tab_flea_hideout.py`).
  - Las pestañas grandes se dividen en mixins (`*Mixin`) por responsabilidad; el estado se inicializa en la clase principal.
  - Colores: usar las constantes `C_*` de `ui/theme.py` o `THEME` en vez de literales hexadecimales.
  - Todo diálogo o ventana secundaria debe respetar la paleta táctica activa (`THEME`) y la tipografía nativa (`ui_font`).
- **`TarkovScope.py` (Punto de Entrada & Orquestador UI)**.

---

## 🎨 Convenciones de Interfaz Gráfica (CustomTkinter)

1. **Hilo Principal sin Bloqueos**:
   - Todo trabajo de red (`requests`), I/O pesado o carga de mapas se ejecuta en un thread demonio (`threading.Thread(target=..., daemon=True)`).
   - El retorno a la UI se hace **exclusivamente** mediante `self.after(0, ...)`.
   - Proteger siempre callbacks con `if not self.winfo_exists(): return`.
2. **Cero Popups Nativos**:
   - Queda prohibido el uso de `tkinter.messagebox` y `tkinter.simpledialog`.
   - Utilizar siempre modales CustomTkinter integrados como `AddMarkerDialog` y `MapViewerModal`.
3. **Alto Contraste y Tipografía Nativa**:
   - Usar `ui_font(size, weight)` garantizando `Segoe UI` en Windows.
   - Textos de lectura en blanco nítido (`#F8FAFC`), texto secundario claro (`#CBD5E1`) y dorado oficial (`#D4B886`).
4. **Renderizado en Lotes (Batch Rendering)**:
   - Para listas con muchos elementos en `CTkScrollableFrame`, usar redibujado diferido en bloques (`after(4, ...)`) con `_render_token` para mantener 60 FPS sin lag al scrollear o filtrar.
5. **Caché en Memoria RAM (Zero-Lag)**:
   - Consultas instantáneas (<1 ms) servidas por `DataStore` en memoria RAM.

---

## 🧪 Pruebas Unitarias y Calidad

- Ejecutar la suite completa:
  ```powershell
  python -m unittest discover -s tests -v
  ```
- Verificación de compilación estricta antes de cada entrega:
  ```powershell
  python -m compileall .
  ```

---

## 🧰 Skills Especializadas Disponibles

El proyecto cuenta con skills avanzadas en `.agents/skills/`:
- `project-planner`: Rol de Lead Product Manager y Planificador Estratégico.
- `software-architect`: Rol de Arquitecto de Software Senior.
- `solid-principles-auditor`: Rol de Auditor de Código SOLID.
- `python-gui-customtkinter`: Técnicas avanzadas de CustomTkinter, theming y modales.
- `python-pro-architecture`: SOLID aplicado, SQLite en modo WAL, networking resiliente y JSON atómico.
- `python-testing-qa`: Mocking, aislamiento de BD y testing rápido.
- `python-windows-packaging`: PyInstaller, AppUserModelID y empaquetado.
