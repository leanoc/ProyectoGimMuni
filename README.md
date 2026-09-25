# Sistema de Inscripción y Sorteo - Gimnasio Municipal 🏊‍♂️🏋️‍♀️

Una aplicación de consola (CLI) desarrollada en Python para gestionar las inscripciones y la asignación de cupos de los cursos del Gimnasio Municipal (Natación y Gimnasia Acuática). 

El sistema incluye validaciones de edad, control de duplicados y adjudicación de lugares mediante sorteo aleatorio o por orden de llegada, utilizando SQLite como base de datos.

## 🚀 Características Principales

- **Gestión de Inscripciones:** Registro de personas con validación estricta de DNI, edad mínima (configurable) y formato de correo electrónico.
- **Control de Cupos Dinámico:** Verificación en tiempo real de la disponibilidad de cupos por comisión y por curso general.
- **Regla de Inscripción Única:** El sistema bloquea automáticamente los intentos de inscripción a múltiples cursos por una misma persona.
- **Algoritmos de Adjudicación:**
  - *Natación:* Asignación de vacantes mediante sorteo aleatorio automatizado.
  - *Gimnasia Acuática:* Asignación estricta por orden de llegada (FIFO).
- **Entorno Persistente:** Base de datos relacional robusta gestionada con SQLite (`system.db`).

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
   Si deseas probar el sistema con datos falsos (159 inscriptos generados automáticamente), ejecuta:
   ```bash
   python seed.py
   ```

## 🧪 Pruebas Unitarias (Testing)

El proyecto cuenta con un entorno de pruebas automatizadas (Unit Testing) para garantizar la fiabilidad de las validaciones y de la lógica de la base de datos.

Para correr los tests, ejecuta:
```bash
python test_gym.py
```
*Los tests utilizan una base de datos temporal para no alterar los datos reales de tu sistema.*

## 📂 Estructura del Proyecto

- `principal.py`: Punto de entrada de la aplicación.
- `menuprincipal.py` / `submenu.py`: Lógica de interfaz interactiva de consola.
- `operations.py`: Lógica de negocio, consultas SQL y algoritmos de adjudicación.
- `database.py`: Conexión y configuración de las tablas SQLite.
- `validators.py`: Funciones auxiliares para validar datos de entrada (DNI, fechas, correos).
- `config.py`: Variables de entorno y configuración general (ej. edad mínima).
- `test_gym.py`: Suite de pruebas unitarias.
- `seed.py`: Script para cargar datos masivos de prueba.
