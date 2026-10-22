# Manual de Procedimientos - Sistema de Inscripción y Sorteo
## Gimnasio Municipal 🏊‍♂️🏋️‍♀️
### **Versión 3.0.0 (Interfaz Gráfica de Escritorio con Tkinter)**
**Desarrollado por: L. M. OCARIZ ARRIETA**

---

## 1. Introducción y Objetivo

El presente manual describe los procedimientos operativos para el correcto uso del **Sistema de Inscripción y Sorteo del Gimnasio Municipal**, actualizado con su **interfaz gráfica moderna de escritorio (GUI)** construida íntegramente con Python y Tkinter/ttk.

El sistema permite gestionar de forma visual e intuitiva el ciclo de vida de los cursos deportivos (Natación, Gimnasia Acuática, Fútbol, Atletismo u otros), el control estricto de cupos y vacantes por comisión, el padrón general de postulantes y la adjudicación transparente de vacantes titulares (mediante Sorteo Aleatorio o por estricto Orden de Llegada FIFO) y sus respectivas Listas de Espera con promoción automática.

---

## 2. Requisitos del Entorno y Puesta en Marcha

### Requisitos Técnicos
- **Sistema Operativo:** Windows, Linux o macOS.
- **Lenguaje:** Python 3.10 o superior (compatible con Python 3.12 y 3.13).
- **Interfaz Gráfica:** `tkinter` y `tkinter.ttk` (incluidos de forma estándar con Python).
- **Base de Datos:** SQLite 3 (integrada de forma nativa en Python, sin requerir instalación de servidores externos).
- **Dependencias externas:** Ninguna. Se apoya exclusivamente en la librería estándar de Python (`tkinter`, `sqlite3`, `unittest`, `datetime`, `re`, `random`).

### Puesta en Marcha

1. Abra una terminal de comandos (PowerShell, CMD o Bash) en la carpeta raíz del proyecto:
   ```bash
   cd "g:\2026\Curso de programación\Programador\Proyecto\GimnasioMunicipal"
   ```
2. Ejecute la aplicación principal:
   ```bash
   python principal.py
   ```
   *La ventana se ajustará al tamaño de pantalla disponible y abrirá centrada. Si una vista, tabla o diálogo supera el espacio visible, utilice sus barras de desplazamiento para acceder al resto del contenido.*

3. *(Opcional)* Carga de datos de prueba:
   Si desea poblar rápidamente la base con datos de prueba realistas para demostración:
   ```bash
   python seed.py
   ```

4. Verificación de integridad con pruebas unitarias:
   ```bash
   python -m unittest test_gym.py
   ```

---

## 3. Modelo de Datos y Reglas de Negocio

El sistema garantiza consistencia e integridad referencial en la base de datos relacional SQLite (`system.db`) mediante las siguientes entidades y reglas:

1. **Tabla Curso:**
   - Define el nombre de la actividad y su criterio de selección (`Sorteo` o `Orden de llegada`).
2. **Tabla Comision:**
   - Asociada a un curso (`id_curso`). Define el `cupo_total` (límite máximo de inscriptos permitidos en la comisión) y el `cupo_seleccion` (cupo de titulares admitidos).
   - *Regla:* El cupo de selección no puede superar al cupo total.
3. **Tabla Persona:**
   - Almacena DNI, nombre, apellido, fecha de nacimiento, dirección, localidad, teléfono y correo electrónico.
   - **Restricción UNIQUE en DNI:** No se permite duplicar números de DNI en el padrón.
   - **Edad Mínima Obligatoria:** Regulada por `config.py` (por defecto 16 años).
4. **Tabla Inscripcion:**
   - Relaciona a una persona con una comisión (`id_persona UNIQUE`, regla 1:1, una persona solo puede participar en un curso/comisión simultáneamente).
   - `estado = 0`: Postulante en **Lista de Espera**.
   - `estado = 1`: Postulante **Titular Admitido**.
   - Claves foráneas con **ON DELETE CASCADE** para mantener la consistencia al eliminar cursos o comisiones.

---

## 4. Estructura de la Interfaz Gráfica (Navegación)

La aplicación cuenta con una **Barra Lateral Izquierda (Sidebar)** de diseño oscuro profesional que permite acceder en cualquier momento a las 5 vistas funcionales:

```text
┌─────────────────────────────────┬───────────────────────────────────────────────────────┐
│ 🏊‍♂️ 🏋️‍♀️ GIMNASIO MUNICIPAL        │                                                       │
│ Sistema de Inscripción & Sorteos│  VISTA ACTIVA (Encabezado, Buscador, Acciones)        │
├─────────────────────────────────┤                                                       │
│ 📊  Dashboard / Resumen         │  [ Tabla de Datos / Tarjetas / Formularios ]          │
│ 📚  Cursos y Deportes           │                                                       │
│ 👥  Comisiones y Cupos          │                                                       │
│ 📝  Personas e Inscripción      │                                                       │
│ 🎲  Sorteos y Adjudicación      │                                                       │
├─────────────────────────────────┤                                                       │
│ Versión 3.0.0 (Tkinter)         │                                                       │
│ Dev: L. M. OCARIZ ARRIETA       │                                                       │
└─────────────────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 5. Procedimientos Operativos por Módulo

### Módulo 1: Panel de Control (Dashboard)

Ofrece un resumen ejecutivo en tiempo real del estado del gimnasio y accesos directos.

#### Procedimiento:
1. Haga clic en **📊 Dashboard / Resumen** en el menú lateral.
2. **Tarjetas de Métricas (KPIs):** Observe los 5 indicadores actualizados:
   - *Cursos Activos*
   - *Comisiones Totales*
   - *Inscriptos Totales*
   - *Titulares Admitidos*
   - *En Lista de Espera*
3. **Accesos Rápidos:** Puede abrir directamente los modales para:
   - Inscribir Postulante.
   - Nuevo Curso.
   - Nueva Comisión.
4. **Tabla de Ocupación Global:** Visualice el estado de cada comisión con sus porcentajes y barras de ocupación.
5. Presione el botón **🔄 Actualizar Datos** en la esquina superior derecha cada vez que desee forzar un refresco general.

---

### Módulo 2: Cursos y Deportes (CRUD)

Permite administrar la oferta deportiva del gimnasio y revisar quiénes están inscriptos en cada actividad.

#### 2.1 Ver y Filtrar Cursos
- Ingrese a **📚 Cursos y Deportes**.
- Escriba en la caja de búsqueda `🔍 Buscar curso:` para filtrar en tiempo real por nombre de curso o criterio.

#### 2.2 Consultar Inscriptos de un Curso
1. Seleccione un curso de la tabla haciendo clic sobre su fila.
2. Haga clic en el botón **👥 Ver Inscriptos** (o haga doble clic sobre la fila).
3. Se abrirá una ventana emergente que lista a todos los inscriptos en ese curso, detallando DNI, Nombre, Apellido, Comisión, Fecha de inscripción y su condición coloreada (**ADMITIDO** en verde o **EN ESPERA** en naranja).

#### 2.3 Crear Nuevo Curso
1. Haga clic en el botón **➕ Nuevo Curso**.
2. Complete el nombre del curso (ej. *Natación Inicial*, *Fútbol Juvenil*).
3. Seleccione el criterio de adjudicación:
   - `Sorteo`: Asignación aleatoria de vacantes titulares.
   - `Orden de llegada`: Asignación estricta por orden cronológico (FIFO).
4. Haga clic en **Guardar**. El nuevo curso aparecerá inmediatamente en la tabla.

#### 2.4 Modificar un Curso
1. Seleccione el curso a editar en la tabla.
2. Haga clic en **✏️ Modificar**.
3. Modifique el nombre o el criterio en el diálogo emergente.
4. Confirme con **Guardar**.

#### 2.5 Eliminar un Curso
1. Seleccione el curso que desea dar de baja.
2. Haga clic en **🗑️ Eliminar**.
3. Confirme la advertencia. Se aplicará borrado en cascada para sus comisiones e inscripciones asociadas.

---

### Módulo 3: Comisiones, Cupos y Vacantes

Permite gestionar horarios, regular la capacidad máxima y fiscalizar la lista de espera de cada comisión.

#### 3.1 Consultar Estado y Vacantes de Comisiones
- Ingrese a **👥 Comisiones y Cupos**.
- La tabla exhibe por cada comisión: ID, Código, Curso, Cupo Total, Inscriptos, Vacantes Libres, Titulares Admitidos, Cupo de Selección y Alumnos en Espera.
- El buscador dinámico superior permite filtrar por código de comisión o nombre de curso.

#### 3.2 Visualizar Lista de Espera Cronológica
1. Seleccione una comisión de la tabla.
2. Haga clic en **⏳ Ver Lista de Espera**.
3. Se abrirá una ventana modal con el orden cronológico estricto de los postulantes no seleccionados:
   - Orden de mérito (`#01`, `#02`, `#03`...).
   - DNI, Nombre y Apellido.
   - Teléfono y Correo electrónico de contacto.
   - Fecha y hora exacta de inscripción registrada por el sistema.

#### 3.3 Crear Nueva Comisión
1. Haga clic en **➕ Nueva Comisión**.
2. Seleccione el curso al que pertenecerá del menú desplegable.
3. Ingrese el código identificador (ej. `C1-NAT`, `C2-FUT`).
4. Indique el **Cupo Total** (límite máximo absoluto de personas admitidas + lista de espera).
5. Indique el **Cupo de Selección** (cantidad de vacantes titulares que ingresarán al curso).
   *Nota: El sistema valida que el cupo de selección sea menor o igual al cupo total.*
6. Presione **Guardar**.

#### 3.4 Modificar Comisión
1. Seleccione la comisión a actualizar y haga clic en **✏️ Modificar**.
2. Puede alterar el código, el cupo total o el cupo de selección.
3. **Protección preventiva:** El sistema rechazará reducir el cupo total a un valor inferior a la cantidad de personas ya inscriptas en dicha comisión.

#### 3.5 Eliminar Comisión
1. Seleccione la comisión y presione **🗑️ Eliminar**.
2. Confirme el mensaje de diálogo para proceder con la baja.

---

### Módulo 4: Padrón de Personas e Inscripciones

Permite realizar inscripciones con **control preventivo de vacantes**, actualizar legajos, reasignar comisiones y gestionar bajas con reemplazo automático.

#### 4.1 Registrar Nueva Inscripción (Verificación Preventiva de Cupos)
Este procedimiento aplica la política *fail-fast* para no solicitar datos innecesarios si no hay lugar:
1. Haga clic en **➕ Inscribir Persona**.
2. En la ventana emergente, el primer paso obligatorio es seleccionar la **Comisión**:
   - El desplegable indica claramente la disponibilidad de cada comisión (ej. `[Vacantes: 5]`).
   - Si la comisión seleccionada se encuentra con cupo lleno, el sistema muestra una advertencia de inmediato y bloquea la operación.
3. Ingrese el **DNI**:
   - El sistema comprueba en tiempo real que el DNI cumpla el formato de 7 u 8 dígitos.
   - Si el DNI ya posee una inscripción activa, se alertará de la duplicación impidiendo avanzar.
4. Complete los datos personales: Nombre, Apellido, Fecha de Nacimiento (`AAAA-MM-DD`), Dirección, Localidad, Teléfono y Email.
5. El sistema calcula la edad automáticamente y valida que cumpla con la edad mínima obligatoria configurada (16 años).
6. Al presionar **Guardar Inscripción**, se crea la persona en el padrón y se genera su inscripción formal con marca de tiempo precisa.

#### 4.2 Modificar Datos Personales
1. Seleccione a la persona en la tabla y haga clic en **✏️ Modificar Persona**.
2. Actualice los datos necesarios en el formulario.
3. **Validaciones automáticas:**
   - Si se cambia el DNI, se comprueba que no pertenezca a otra persona registrada (restricción UNIQUE).
   - Si se altera la fecha de nacimiento, se valida nuevamente la edad mínima.
   - Se validan los formatos de correo electrónico y campos obligatorios.
4. Presione **Guardar Cambios**.

#### 4.3 Reasignar / Cambiar de Comisión
1. Seleccione a la persona y haga clic en **🔄 Cambiar Comisión**.
2. El diálogo exhibirá la comisión actual del alumno y un listado de las demás comisiones con sus vacantes libres.
3. Elija la nueva comisión de destino.
4. **Regla de reemplazo automático:**
   - Si la persona tenía condición de **Titular Admitido**, su vacante original se asignará automáticamente al primer postulante de la lista de espera de esa comisión.
   - El alumno trasladado ingresará en la nueva comisión en condición de lista de espera para preservar el orden y la transparencia.
5. Presione **Confirmar Cambio**.

#### 4.4 Bajas y Cancelaciones con Promoción Automática
1. Seleccione a la persona y haga clic en **❌ Dar de Baja**.
2. El sistema presentará dos modalidades de baja para elegir:
   - **Opción A (Cancelar solo la inscripción):** Da de baja la participación en el curso pero conserva la ficha de la persona en el padrón para futuros ciclos.
   - **Opción B (Eliminar completamente del sistema):** Elimina el registro personal y su inscripción de la base de datos.
3. **Promoción de Lista de Espera:** Si la persona dada de baja era titular (`estado = 1`), el siguiente postulante en espera por orden cronológico pasa inmediatamente a ocupar la titularidad como admitido, notificando su nombre por pantalla.

---

### Módulo 5: Sorteos y Adjudicación de Cupos

Este módulo centraliza la asignación de vacantes titulares y la inspección general de resultados.

#### 5.1 Ejecución del Sorteo Aleatorio
1. Ingrese a **🎲 Sorteos y Adjudicación**.
2. En el panel izquierdo (*Sorteo Aleatorio Automatizado*), seleccione en el desplegable el curso que opera bajo criterio de sorteo (ej. *Natación*).
3. Haga clic en el botón **🎲 Ejecutar Sorteo Aleatorio**.
4. El sistema verificará los cupos de selección de cada comisión del curso, seleccionará al azar (`random.sample`) entre los inscriptos en espera hasta agotar las vacantes disponibles y los ascenderá a condición de admitidos.
5. Se presentará un diálogo resumen con el total de adjudicados y los resultados se reflejarán instantáneamente en la tabla inferior.

#### 5.2 Adjudicación por Orden de Llegada (FIFO)
1. En el panel derecho (*Adjudicación por Orden de Llegada*), seleccione el curso configurado con criterio por llegada (ej. *Gimnasia Acuática*).
2. Haga clic en el botón **⏱️ Asignar por Orden de Llegada**.
3. El sistema ordenará estrictamente por `fecha_hora` a los inscriptos de cada comisión y asignará la titularidad a los primeros hasta cubrir el cupo de selección establecido.
4. Los restantes postulantes permanecerán ordenados en lista de espera.

#### 5.3 Inspector de Resultados y Listas de Espera
En la parte inferior de la vista se encuentra el inspector general:
- **Filtrar por Curso:** Seleccione un curso específico o `Todos los cursos`.
- **Filtrar por Condición:**
  - `Todos`: Muestra el padrón completo del curso.
  - `Solo Admitidos (Titulares)`: Lista a quienes tienen vacante asegurada.
  - `Solo en Lista de Espera`: Lista a los postulantes ordenados cronológicamente a la espera de una vacante.
- Presione **🔄 Actualizar** para refrescar la consulta.

---

## 6. Matriz de Manejo de Errores y Excepciones

| Situación Detectada | Comportamiento del Sistema en la GUI | Acción Sugerida |
| :--- | :--- | :--- |
| **Comisión con cupo completo** | Al seleccionar la comisión, el modal avisa que no hay cupo y bloquea el botón de guardar. | Seleccionar otra comisión con vacantes o ampliar el cupo en el módulo de comisiones. |
| **DNI duplicado en alta o edición** | Ventana emergente de advertencia informando que el DNI ya se encuentra registrado. | Verificar el número de documento ingresado. |
| **Postulante menor de 16 años** | Ventana de advertencia indicando la edad calculada y el mínimo requerido. | Verificar la fecha de nacimiento ingresada (`AAAA-MM-DD`). |
| **Intento de doble inscripción** | El sistema detecta que la persona ya tiene un curso y rechaza la operación. | Utilizar la opción de reasignación de comisión o dar de baja la inscripción previa. |
| **Reducción de cupo inviable** | Bloquea la edición si el nuevo cupo total es menor a la cantidad de personas inscriptas. | Dar de baja postulantes antes de achicar el cupo total de la comisión. |

---

## 7. Verificación de Integridad mediante Pruebas Automatizadas

El proyecto incluye 17 pruebas unitarias completas en `test_gym.py` que validan todas las reglas de negocio, operaciones de base de datos, lógica de cupos y reemplazos automáticos sin tocar la base real de producción (`system.db`).

Para correrlas en cualquier momento:
```bash
python -m unittest test_gym.py
```

Salida esperada:
```text
.................
----------------------------------------------------------------------
Ran 17 tests in 1.2s

OK
```
