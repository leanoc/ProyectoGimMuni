# Sistema de Inscripción y Sorteo - Gimnasio Municipal 🏊‍♂️🏋️‍♀️
### **Versión 3.0.0 (Interfaz Gráfica de Escritorio con Tkinter)**
**Desarrollado por: L. M. OCARIZ ARRIETA**

---

Una aplicación de escritorio completa y moderna desarrollada en Python con **Tkinter nativo y ttk** para gestionar las inscripciones y la adjudicación de cupos de los cursos y disciplinas del Gimnasio Municipal (Natación, Gimnasia Acuática, Fútbol, Atletismo u otros deportes).

El sistema incluye una interfaz gráfica moderna estructurada con barra lateral de navegación (Sidebar), panel de métricas en tiempo real (Dashboard), operaciones CRUD completas con diálogos interactivos, verificación fail-fast preventiva de vacantes, asignación por sorteo aleatorio o por orden de llegada (FIFO), y base de datos relacional SQLite sin dependencias externas obligatorias.

---

## 🚀 Características Principales (Versión 3)

- **Interfaz Gráfica Moderna con Tkinter & ttk (100% nativa de Python):**
  - Panel lateral de navegación (*Sidebar*) con diseño oscuro profesional, selector activo y firma del autor.
  - *Dashboard* interactivo con tarjetas de indicadores clave (*KPIs*) actualizadas en vivo (Cursos activos, comisiones, inscriptos, titulares admitidos y postulantes en lista de espera).
  - Tablas estilizadas (*ttk.Treeview*) con buscador reactivo en tiempo real y filtrado dinámico.
  - Diálogos modales accesibles para altas, modificaciones, confirmaciones de baja y visualizadores de listas.
  - Ventana, vistas y diálogos adaptables a pantallas de menor resolución, con desplazamiento cuando el contenido excede el espacio disponible.
  - Tablas con desplazamiento horizontal para consultar todas las columnas en ventanas angostas.

- **Gestión Integral de Cursos (CRUD):**
  - Creación, modificación y eliminación en cascada de cursos y deportes.
  - Configuración personalizada de criterio de adjudicación (*Sorteo* o *Orden de llegada*), edad mínima requerida y cupo máximo global.
  - Visualizador modal de postulantes inscriptos por curso.

- **Comisiones y Monitoreo de Cupos:**
  - Consulta en tiempo real de ocupación: Inscriptos vs. Cupo Total, Admitidos vs. Cupo de Selección, y Vacantes Libres.
  - Visualizador cronológico detallado de la **Lista de Espera** con numeración de orden de mérito/llegada (`#01`, `#02`...), DNI, nombre y fecha/hora exacta.

- **Padrón de Personas e Inscripciones:**
  - **Verificación Previa Fail-Fast:** Al seleccionar una comisión, el sistema comprueba la disponibilidad inmediata de cupos antes de permitir la carga de datos personales.
  - Control riguroso de unicidad de DNI y regla de curso único (1:1, una persona solo puede participar en una comisión).
  - Cálculo automático de edad con validación contra la edad mínima obligatoria configurada.
  - Cambio y reasignación de comisiones con verificación preventiva de vacantes.
  - Bajas con **promoción automática**: al dar de baja a un titular admitido, el primer postulante en lista de espera asciende a titular inmediatamente.

- **Módulo de Sorteos y Adjudicación:**
  - Paneles diferenciados para **Sorteo Aleatorio** y **Orden de Llegada (FIFO)** con confirmación previa y reporte detallado de adjudicados.
  - Inspector de resultados con filtro de condición (Titulares admitidos / En lista de espera).

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.10+ (100% estándar, sin requerir paquetes externos pesados).
- **Interfaz Gráfica (GUI):** `tkinter` y `tkinter.ttk` (nativo de la librería estándar).
- **Base de Datos:** SQLite 3 (Módulo nativo `sqlite3`).
- **Pruebas Automatizadas:** `unittest` (suite de pruebas de lógica de negocio y adaptación del diseño a distintas resoluciones).

---

## ⚙️ Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/leanoc/ProyectoGimMuni.git
   cd ProyectoGimMuni
   ```

2. **Ejecutar la aplicación (GUI):**
   Al no depender de librerías externas pesadas, basta con ejecutar el archivo principal:
   ```bash
   python principal.py
   ```

3. **Cargar datos de prueba (Opcional):**
   Si deseas poblar rápidamente el sistema con datos de demostración:
   ```bash
   python seed.py
   ```

---

## 🧪 Pruebas Unitarias (Testing)

El proyecto cuenta con pruebas automatizadas para verificar integridad de datos, validaciones de cupo, lógica de negocio, bajas en cascada y ajuste/centrado de ventanas según el tamaño de pantalla:

```bash
python -m unittest discover -v
```

---

## 📂 Estructura del Proyecto

```text
GimnasioMunicipal/
├── gui/                         # Paquete de la interfaz gráfica Tkinter
│   ├── __init__.py              # Exportador del punto de entrada GUI
│   ├── app.py                   # Ventana principal, navegación y controlador
│   ├── theme.py                 # Paleta de colores, tipografías y estilos ttk
│   ├── components/
│   │   └── dialogs.py           # Diálogos modales (Cursos, Comisiones, Inscripción, etc.)
│   └── views/
│       ├── dashboard_view.py    # Vista del panel de control y resumen
│       ├── courses_view.py      # Vista de gestión de cursos (CRUD)
│       ├── commissions_view.py  # Vista de comisiones y vacantes
│       ├── persons_view.py      # Vista de padrón de personas e inscripciones
│       └── selections_view.py   # Vista de sorteos y adjudicaciones
├── principal.py                 # Punto de entrada de la aplicación
├── operations.py                # Lógica de negocio, consultas SQL y operaciones
├── database.py                  # Conexión y esquema relacional SQLite
├── validators.py                # Validadores de entrada (DNI, fechas, emails, etc.)
├── config.py                    # Configuración global
├── test_gym.py                  # Pruebas automatizadas de la lógica de negocio
├── test_gui_layout.py           # Pruebas de adaptación geométrica de ventanas
├── seed.py                      # Script auxiliar de población de datos
├── MANUAL_DE_PROCEDIMIENTOS.md  # Manual operativo paso a paso
└── ErroresEncontrados.md        # Registro histórico de mejoras y requerimientos
```

---
*Gimnasio Municipal - Sistema de Inscripción y Sorteo | Dev: L. M. OCARIZ ARRIETA*
