# Manual de Procedimientos - Sistema de Inscripción y Sorteo
## Gimnasio Municipal 🏊‍♂️🏋️‍♀️

---

## 1. Introducción y Objetivo

El presente manual describe los procedimientos operativos para el correcto uso del **Sistema de Inscripción y Sorteo del Gimnasio Municipal**. 

El sistema permite gestionar de forma íntegra el ciclo de vida de los cursos deportivos (Natación, Gimnasia Acuática u otros), sus comisiones, los datos personales de los postulantes y el control riguroso de cupos, asignaciones y listas de espera.

---

## 2. Requisitos del Entorno y Puesta en Marcha

### Requisitos Técnicos
- **Lenguaje:** Python 3.10 o superior (compatible con Python 3.12).
- **Base de Datos:** SQLite 3 (integrada de forma nativa en Python, sin requerir servidores externos).
- **Dependencias externas:** Ninguna. Se apoya exclusivamente en la librería estándar de Python (`sqlite3`, `unittest`, `datetime`, `re`, `random`).

### Puesta en Marcha
1. Abra una terminal de comandos en la carpeta raíz del proyecto:
   ```bash
   cd "d:\2026\Curso de programación\Programador\Proyecto\GimnasioMunicipal"
   ```
2. Ejecute la aplicación principal:
   ```bash
   python principal.py
   ```
3. Ejecute la suite de pruebas unitarias para validar la integridad del sistema:
   ```bash
   python test_gym.py
   ```
4. *(Opcional)* Archivo `seed.py`:
   - Es una herramienta práctica de utilidad para poblar rápidamente la base con datos masivos de prueba.
   - El sistema opera de manera óptima tanto con la base vacía, a medias o con los cupos al máximo.

---

## 3. Modelo de Datos y Reglas de Negocio

El sistema garantiza consistencia mediante las siguientes restricciones relacionales:

1. **Tabla Curso:**
   - Define el nombre de la actividad y su criterio de selección (`Sorteo` o `Orden de llegada`).
2. **Tabla Comision:**
   - Asociada a un curso (`id_curso`). Define el `cupo_total` (límite máximo de inscriptos permitidos en la comisión) y el `cupo_seleccion` (cupo de titulares admitidos).
3. **Tabla Persona:**
   - Almacena DNI, nombre, apellido, fecha de nacimiento, dirección, localidad, teléfono y correo electrónico.
   - **Restricción UNIQUE en DNI:** No se permite duplicar DNIs en el padrón.
   - **Edad Mínima Obligatoria:** Regulada por `config.py` (por defecto 16 años).
4. **Tabla Inscripcion:**
   - Relaciona a una persona con una comisión (`id_persona UNIQUE`, regla 1:1, una persona solo puede participar en un curso).
   - `estado = 0`: Postulante en **Lista de Espera**.
   - `estado = 1`: Postulante **Titular Admitido**.
   - Claves foráneas con **ON DELETE CASCADE** para mantener la integridad referencial.

---

## 4. Procedimientos Operativos por Módulo

El sistema cuenta con un Menú Principal estructurado en 4 módulos accesibles por teclado:

```text
================================
  SISTEMA INSCRIPCIÓN Y SORTEO  
================================
1. Ver Cursos e Inscriptos
2. Ver Comisiones y Vacantes
3. Gestión de Personas e Inscripciones
4. Sorteo y Asignación de Cupos
0. Salir
```

---

### Módulo 1: Gestión y Consulta de Cursos (CRUD)

Permite administrar la oferta deportiva del gimnasio.

#### 1.1 Ver Cursos e Inscriptos
- **Paso 1:** Seleccione la opción `1` del submenú de cursos.
- **Paso 2:** El sistema listará todos los cursos registrados junto a su criterio.
- **Paso 3:** Ingrese el ID del curso deseado para visualizar el detalle de inscriptos, comisión a la que pertenecen, fecha/hora y su condición (`ADMITIDO` o `EN ESPERA`).

#### 1.2 Crear Nuevo Curso
- **Paso 1:** Seleccione la opción `2` (*Crear nuevo curso*).
- **Paso 2:** Ingrese el nombre del curso (ej. `Natación Avanzada`, `Yoga Acuático`).
- **Paso 3:** Seleccione el criterio de adjudicación:
  - `1`: Sorteo (asigna titulares mediante sorteo aleatorio).
  - `2`: Orden de llegada (asigna titulares según orden cronológico FIFO).

#### 1.3 Modificar Curso Existente
- **Paso 1:** Seleccione la opción `3` (*Modificar curso existente*).
- **Paso 2:** Ingrese el ID del curso a editar.
- **Paso 3:** Ingrese el nuevo nombre (o presione `Enter` para conservar el actual).
- **Paso 4:** Seleccione el nuevo criterio o presione `Enter` para conservarlo.

#### 1.4 Eliminar Curso
- **Paso 1:** Seleccione la opción `4` (*Eliminar curso*).
- **Paso 2:** Ingrese el ID del curso.
- **Paso 3:** El sistema solicitará confirmación (`SI/no`) advirtiendo que se eliminarán en cascada las comisiones e inscripciones vinculadas.

---

### Módulo 2: Comisiones y Vacantes (CRUD y Lista de Espera)

Permite gestionar horarios, cupos y consultar postulantes en espera.

#### 2.1 Listar Comisiones y Vacantes
- Muestra el estado en tiempo real de cada comisión:
  - Inscriptos totales vs. Cupo total permitido.
  - Vacantes libres disponibles.
  - Admitidos vs. Cupo de selección.
  - Cantidad de personas actualmente en lista de espera.

#### 2.2 Ver Lista de Espera por Comisión
- **Paso 1:** Seleccione la opción `2` (*Ver lista de espera de una comisión*).
- **Paso 2:** Ingrese el ID de la comisión.
- **Paso 3:** El sistema generará el listado ordenado cronológicamente con la posición en la fila (`#01`, `#02`, etc.), DNI, nombre y fecha/hora exacta de inscripción.

#### 2.3 Crear Nueva Comisión
- **Paso 1:** Seleccione la opción `3` (*Crear nueva comisión*).
- **Paso 2:** Seleccione el ID del curso al que pertenece.
- **Paso 3:** Defina el código (ej. `C3-NAT`, `C3-GIM`).
- **Paso 4:** Ingrese el `cupo total` permitido y el `cupo de selección` (titulares). *Regla: El cupo de selección debe ser menor o igual al cupo total.*

#### 2.4 Modificar Comisión (Código y Ampliación de Cupos)
- Permite actualizar el código y los cupos de una comisión.
- **Control de seguridad:** El sistema impide reducir el cupo total por debajo de la cantidad de alumnos ya inscriptos para evitar inconsistencias.

#### 2.5 Eliminar Comisión
- Permite dar de baja una comisión con confirmación previa.

---

### Módulo 3: Gestión de Personas e Inscripciones

#### 3.1 Registrar Nueva Inscripción (Verificación Previa de Cupos)
Este procedimiento garantiza que **no se pidan datos en vano ni se registren operaciones si no hay vacantes**:
1. El sistema presenta el listado de comisiones indicando cuántas vacantes libres quedan y alertando si alguna está `COMPLETA (SIN CUPO)`.
2. Si todas las comisiones están al máximo de su capacidad, el sistema notifica de inmediato y bloquea la carga sin solicitar datos.
3. El operador selecciona el ID de la comisión deseada.
4. **Verificación previa:** El sistema valida la disponibilidad de la comisión y del curso antes de continuar.
5. El operador ingresa el DNI:
   - Si la persona ya tiene un curso asignado, se rechaza la duplicación.
6. Si pasa las validaciones, se solicitan: Nombre, Apellido, Fecha de Nacimiento (valida edad mínima $\ge 16$ años), Dirección, Localidad, Teléfono y Email.
7. La persona y su inscripción se confirman de forma atómica.

#### 3.2 Actualizar Información de una Persona Guardada
Permite editar cualquier dato personal de un registro existente:
1. Ingrese el DNI de la persona a modificar.
2. El sistema muestra los datos actuales entre corchetes `[...]`.
3. Para mantener un dato sin cambios, presione `Enter`.
4. Para modificar un dato, ingrese el nuevo valor.
5. **Validaciones automáticas:**
   - Si se cambia el DNI, se comprueba que no pertenezca a otra persona registrada (restricción UNIQUE).
   - Si se cambia la fecha de nacimiento, se recalcula la edad mínima obligatoria.
   - Se validan formatos de correo electrónico y campos obligatorios.

#### 3.3 Reasignar / Cambiar de Comisión a un Inscripto
1. Ingrese el DNI del inscripto.
2. El sistema exhibirá las comisiones disponibles y sus vacantes libres.
3. Ingrese el ID de la nueva comisión de destino.
4. El sistema valida que la nueva comisión tenga cupo disponible.
5. **Regla de reemplazo:** Si la persona era titular admitida en la comisión original, su vacante se asigna de forma automática al primer postulante de la lista de espera de dicha comisión. La persona reasignada ingresa a la nueva comisión en lista de espera.

#### 3.4 Bajas de Inscripción o Persona
Al ingresar el DNI de la persona, el sistema ofrece dos modalidades de baja:
- **Modalidad A (Cancelar solo la inscripción):** Da de baja la participación en el curso pero conserva la ficha de la persona en el padrón para futuros registros.
- **Modalidad B (Eliminar completamente a la persona):** Elimina a la persona y su inscripción en cascada.
- **Promoción automática:** En ambos casos, si la persona dada de baja era titular (`estado = 1`), el siguiente postulante en espera por orden de llegada pasa inmediatamente a ocupar el lugar como titular admitido.

---

### Módulo 4: Sorteo, Adjudicación y Resultados

#### 4.1 Sorteo de Natación
- Ejecuta el algoritmo de asignación aleatoria (`random.sample`) entre todos los inscriptos con `estado = 0` hasta completar el cupo de titulares (`cupo_seleccion`).
- Los no seleccionados permanecen en `estado = 0` conformando la lista de espera.

#### 4.2 Asignación por Orden de Llegada (Gimnasia Acuática)
- Aplica el criterio FIFO (First In, First Out). Ordena a los postulantes por fecha y hora de inscripción y adjudica la titularidad a los primeros hasta agotar el cupo de selección.

#### 4.3 Consultar Titulares Admitidos
- Visualiza por pantalla el listado de personas confirmadas para Natación o Gimnasia Acuática con DNI, nombre, comisión y fecha.

#### 4.4 Ver Listas de Espera Unificadas
- Genera un reporte completo de todas las comisiones, exhibiendo cada postulante en espera con su número de orden (`#01`, `#02`, etc.) para un seguimiento transparente y rápido.

---

## 5. Matriz de Manejo de Errores y Excepciones

| Situación Detectada | Comportamiento del Sistema | Acción Sugerida |
| :--- | :--- | :--- |
| **Comisión con cupo lleno** | El sistema rechaza la inscripción previamente y no solicita datos personales. | Seleccionar otra comisión con vacantes o ampliar el cupo en el Módulo 2. |
| **DNI duplicado en actualización** | El sistema bloquea la modificación con mensaje de integridad referencial. | Verificar el número de DNI ingresado. |
| **Postulante menor de edad** | Se rechaza el alta indicando la edad mínima requerida. | Verificar la fecha de nacimiento ingresada. |
| **Intento de doble inscripción** | El sistema impide que una persona tenga más de una inscripción activa. | Dar de baja la inscripción anterior o reasignar comisión. |
| **Reducción de cupo inviable** | Bloquea la modificación si el nuevo cupo es menor a los alumnos actuales. | Dar de baja postulantes antes de achicar el cupo total. |

---

## 6. Verificación de Integridad mediante Pruebas Automatizadas

El proyecto incluye 17 pruebas unitarias completas en `test_gym.py`. Para ejecutarlas:

```bash
python test_gym.py
```

Salida esperada:
```text
..................
----------------------------------------------------------------------
Ran 17 tests in 0.5s

OK
```

Todas las pruebas se ejecutan sobre una base de datos temporal en memoria/archivo efímero sin alterar los datos reales de `system.db`.
