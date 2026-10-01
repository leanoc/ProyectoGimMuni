# Sistema de Inscripción y Sorteo - Gimnasio Municipal 🏊‍♂️🏋️‍♀️

Una aplicación de consola (CLI) desarrollada en Python para gestionar las inscripciones y la asignación de cupos de los cursos del Gimnasio Municipal (Natación y Gimnasia Acuática). 

El sistema incluye validaciones de edad, control de duplicados, operaciones CRUD completas por cada tabla relacional, verificación previa de cupos y adjudicación de lugares mediante sorteo aleatorio o por orden de llegada, utilizando SQLite como base de datos.

## 🚀 Características Principales

- **Gestión de Inscripciones con Verificación Previa de Cupos:** Verifica la disponibilidad de vacantes de la comisión y del curso antes de solicitar o insertar datos del postulante. Si una comisión está completa, informa de inmediato sin requerir cargas infructuosas.
- **Operaciones CRUD por Tabla Relacional:**
  - **Cursos:** Consulta, creación, actualización de nombre/criterio y baja con eliminación en cascada.
  - **Comisiones:** Consulta de ocupación en tiempo real, creación, ampliación/modificación de cupos y baja.
  - **Personas:** Consulta, búsqueda por DNI, actualización de registros guardados (con validación de DNI UNIQUE y edad mínima) y baja.
  - **Inscripciones:** Alta atómica, reasignación/cambio de comisión y cancelación.
- **Visualización de Listas de Espera:** Consulta detallada y ordenada de los postulantes en espera (`estado = 0`) para cada comisión con su respectivo orden de mérito/llegada (`#01`, `#02`...).
- **Regla de Inscripción Única:** Bloquea de forma automática los intentos de inscripción a múltiples cursos por una misma persona (relación 1:1).
- **Bajas y Reemplazo Automático:** Al dar de baja a una persona admitida como titular, el siguiente inscripto de la lista de espera por fecha y hora ocupa su lugar automáticamente.
- **Algoritmos de Adjudicación:**
  - *Natación:* Asignación de vacantes mediante sorteo aleatorio automatizado.
  - *Gimnasia Acuática:* Asignación estricta por orden de llegada (FIFO).
- **Entorno Persistente:** Base de datos relacional robusta gestionada con SQLite (`system.db`).

## 📖 Manual de Procedimientos

Para consultar la guía detallada de operación paso a paso, flujos de trabajo y matriz de errores, consulte el archivo:
👉 [**Manual de Procedimientos (MANUAL_DE_PROCEDIMIENTOS.md)**](MANUAL_DE_PROCEDIMIENTOS.md)

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.x (Puro, sin dependencias externas pesadas).
- **Base de Datos:** SQLite (Módulo `sqlite3` nativo de Python).
- **Testing:** `unittest` (Módulo nativo de Python).

## ⚙️ Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/leanoc/ProyectoGimMuni.git
   cd ProyectoGimMuni
   ```

2. **Ejecutar el sistema:**
   No requiere instalar librerías adicionales. Simplemente ejecuta el archivo principal:
   ```bash
   python principal.py
   ```

3. **Poblar la base de datos (Opcional):**
   Si deseas probar el sistema con datos de prueba, ejecuta el script auxiliar:
   ```bash
   python seed.py
   ```
   *Nota: El sistema funciona de manera óptima tanto con los cupos vacíos, a medias o al máximo.*

## 🧪 Pruebas Unitarias (Testing)

El proyecto cuenta con un entorno de pruebas automatizadas (17 tests) para garantizar la fiabilidad de las validaciones, el CRUD y la lógica de negocio.

Para correr los tests, ejecuta:
```bash
python test_gym.py
```
*Los tests utilizan una base de datos temporal para no alterar los datos reales de tu sistema.*

## 📂 Estructura del Proyecto

- `principal.py`: Punto de entrada de la aplicación.
- `menuprincipal.py`: Menú principal del sistema.
- `submenu.py`: Submenús interactivos para cursos, comisiones, personas/inscripciones y sorteos.
- `operations.py`: Lógica de negocio, consultas SQL, validaciones previas de cupo y CRUD.
- `database.py`: Conexión y configuración de las tablas SQLite.
- `validators.py`: Funciones auxiliares para validar datos de entrada (DNI, fechas, correos, campos requeridos).
- `config.py`: Variables de configuración general (ej. edad mínima obligatoria).
- `test_gym.py`: Suite de 17 pruebas unitarias automatizadas.
- `seed.py`: Script auxiliar para carga masiva de prueba.
- `MANUAL_DE_PROCEDIMIENTOS.md`: Documento formal de procedimientos y uso del sistema.
