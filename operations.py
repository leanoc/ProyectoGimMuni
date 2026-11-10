import random
import os
import sqlite3
import database
from database import execute_query
from config import MINIMUM_AGE
import validators
import notifications


EXPORT_COLUMNS = {
    "Curso": ("id_curso", "nombre", "criterio", "edad_minima", "cupo_maximo"),
    "Comision": ("id_comision", "codigo", "cupo_total", "cupo_seleccion", "id_curso"),
    "Persona": (
        "id_persona", "dni", "nombre", "apellido", "fecha_nac",
        "direccion", "localidad", "telefono", "email", "sexo",
    ),
    "Inscripcion": (
        "id_inscripcion", "fecha_hora", "estado", "id_persona", "id_comision",
    ),
}


def _send_enrollment_email(inscription_id: int, confirmed: bool = False) -> str:
    """Envía el aviso de inscripción o confirmación para una inscripción existente."""
    enrollment = execute_query(
        """
        SELECT p.nombre, p.apellido, p.email, cur.nombre, com.codigo
        FROM Inscripcion i
        JOIN Persona p ON p.id_persona = i.id_persona
        JOIN Comision com ON com.id_comision = i.id_comision
        JOIN Curso cur ON cur.id_curso = com.id_curso
        WHERE i.id_inscripcion = ?
        """,
        (inscription_id,),
        fetch=True,
    )
    if not enrollment:
        return "AVISO: no se encontraron los datos para enviar el correo."

    first_name, last_name, email, course_name, commission_code = enrollment[0]
    full_name = f"{first_name} {last_name}"
    if confirmed:
        subject = f"Confirmación de vacante: {course_name}"
        body = (
            f"Hola {full_name}:\n\n"
            f"Te confirmamos que formas parte del curso {course_name}, "
            f"comisión {commission_code}.\n\n"
            "Gimnasio Municipal"
        )
        description = "de confirmación"
    else:
        subject = f"Inscripción recibida: {course_name}"
        body = (
            f"Hola {full_name}:\n\n"
            f"Recibimos tu inscripción al curso {course_name}, "
            f"comisión {commission_code}. La adjudicación de vacantes "
            "se realizará según el criterio del curso.\n\n"
            "Gimnasio Municipal"
        )
        description = "de inscripción"

    sent, detail = notifications.send_email(email or "", subject, body)
    if sent:
        return f"Correo {description} enviado a {full_name}."
    return f"AVISO: no se pudo enviar correo a {full_name}: {detail}"


def get_export_data(
    table_name: str,
    columns: tuple[str, ...],
) -> tuple[tuple[str, ...], list[tuple]]:
    """Devuelve encabezados y filas de columnas permitidas de una tabla."""
    if table_name not in EXPORT_COLUMNS:
        raise ValueError("La tabla seleccionada no está habilitada para exportación.")
    if not columns or any(column not in EXPORT_COLUMNS[table_name] for column in columns):
        raise ValueError("Seleccione al menos una columna válida para exportar.")

    selected_columns = ", ".join(f'"{column}"' for column in columns)
    rows = execute_query(
        f'SELECT {selected_columns} FROM "{table_name}" ORDER BY 1',
        fetch=True,
    )
    return columns, rows


def get_movement_history():
    """Retorna los movimientos más recientes primero, sin datos personales sensibles."""
    return execute_query(
        """
        SELECT fecha_hora, entidad, accion, detalle
        FROM Movimiento
        ORDER BY id_movimiento DESC
        """,
        fetch=True,
    )


def backup_database(destination: str) -> str:
    """Crea una copia íntegra de la base de datos en la ruta indicada."""
    source_path = os.path.normcase(os.path.abspath(database.DB_PATH))
    destination_path = os.path.normcase(os.path.abspath(destination))
    if source_path == destination_path:
        raise ValueError("El destino no puede ser el archivo de la base de datos activa.")

    source = database.connect_db()
    backup = None
    try:
        backup = sqlite3.connect(destination)
        source.backup(backup)
    finally:
        if backup is not None:
            backup.close()
        source.close()
    return destination

# --- VALIDACIONES Y DISPONIBILIDAD DE CUPOS ---

def check_commission_availability(id_comision: int, cursor=None):
    """
    Verifica la disponibilidad de cupos en la comisión y a nivel global del curso
    ANTES de proceder con una inscripción o reasignación.
    Retorna (True, None) si hay vacantes, o (False, mensaje) si los cupos están al máximo.
    """
    close_conn = False
    if cursor is None:
        conn = database.connect_db()
        cursor = conn.cursor()
        close_conn = True

    try:
        cursor.execute(
            """
            SELECT c.cupo_total, c.id_curso, cur.nombre, c.codigo, cur.cupo_maximo
            FROM Comision c
            JOIN Curso cur ON c.id_curso = cur.id_curso
            WHERE c.id_comision = ?
            """,
            (id_comision,)
        )
        comm_data = cursor.fetchone()
        if not comm_data:
            return False, "La comisión indicada no existe."

        cupo_comision, id_curso, nombre_curso, codigo_comision, cupo_maximo_curso = comm_data

        cursor.execute("SELECT COUNT(*) FROM Inscripcion WHERE id_comision = ?", (id_comision,))
        enrolled_comm = cursor.fetchone()[0]

        if enrolled_comm >= cupo_comision:
            return False, f"Inscripción rechazada: Cupo completo en la comisión {codigo_comision} ({enrolled_comm}/{cupo_comision})."

        max_course_quota = cupo_maximo_curso if cupo_maximo_curso is not None else 0

        cursor.execute(
            """
            SELECT COUNT(i.id_inscripcion)
            FROM Inscripcion i
            JOIN Comision c ON i.id_comision = c.id_comision
            WHERE c.id_curso = ?
            """,
            (id_curso,)
        )
        enrolled_course = cursor.fetchone()[0]

        if enrolled_course >= max_course_quota:
            return False, f"Inscripción rechazada: Cupo global del curso {nombre_curso} agotado ({enrolled_course}/{max_course_quota})."

        return True, None
    finally:
        if close_conn:
            database.disconnect_db(cursor.connection)

# --- ALTAS Y VALIDACIONES DE INSCRIPCIÓN ---

def get_person_by_dni(dni):
    """Obtiene el ID y datos básicos de una persona por su DNI."""
    query = "SELECT id_persona, dni, nombre, apellido, fecha_nac FROM Persona WHERE dni = ?"
    return execute_query(query, (str(dni).strip(),), fetch=True)

def get_person_by_id(id_persona: int):
    """Obtiene todos los atributos de una persona por su ID."""
    query = """
        SELECT id_persona, dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email, sexo
        FROM Persona WHERE id_persona = ?
    """
    return execute_query(query, (id_persona,), fetch=True)

def _register_applicant(cursor, id_persona: int, id_comision: int):
    """
    Valida e inscribe a una persona:
    1. Que cumpla la edad mínima estipulada en config.py.
    2. Que no posea una inscripción previa en ningún curso (relación 1:1).
    3. Que la comisión no supere su cupo total permitido.
    4. Que el curso no supere su capacidad total dinámica (suma de sus comisiones).
    """
    cursor.execute("SELECT fecha_nac FROM Persona WHERE id_persona = ?", (id_persona,))
    person_data = cursor.fetchone()
    if not person_data:
        return False, "La persona no existe en el padrón."

    # Obtener edad_minima del curso
    cursor.execute(
        """
        SELECT cur.edad_minima
        FROM Comision c
        JOIN Curso cur ON c.id_curso = cur.id_curso
        WHERE c.id_comision = ?
        """,
        (id_comision,)
    )
    curso_data = cursor.fetchone()
    edad_min = curso_data[0] if curso_data else MINIMUM_AGE

    if not validators.validate_minimum_age(person_data[0], edad_min):
        return False, f"Inscripción rechazada: La edad mínima obligatoria es de {edad_min} años."

    cursor.execute("SELECT id_inscripcion FROM Inscripcion WHERE id_persona = ?", (id_persona,))
    if cursor.fetchone():
        return False, "Inscripción rechazada: La persona ya posee un curso asignado."

    # Validación previa de cupos usando la función modular
    has_quota, quota_msg = check_commission_availability(id_comision, cursor=cursor)
    if not has_quota:
        return False, quota_msg

    cursor.execute(
        """
        SELECT c.cupo_total, cur.nombre
        FROM Comision c
        JOIN Curso cur ON c.id_curso = cur.id_curso
        WHERE c.id_comision = ?
        """,
        (id_comision,)
    )
    comm_info = cursor.fetchone()
    cupo_comision, nombre_curso = comm_info[0], comm_info[1]

    cursor.execute("SELECT COUNT(*) FROM Inscripcion WHERE id_comision = ?", (id_comision,))
    enrolled_comm = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO Inscripcion (id_persona, id_comision, estado) VALUES (?, ?, 0)",
        (id_persona, id_comision)
    )
    return True, f"Inscripción confirmada en {nombre_curso} ({enrolled_comm + 1}/{cupo_comision})."

def register_applicant(id_persona: int, id_comision: int):
    """Inscribe una persona existente, confirmando la operación solo si pasa las validaciones."""
    conn = database.connect_db()
    try:
        result = _register_applicant(conn.cursor(), id_persona, id_comision)
        if result[0]:
            conn.commit()
        else:
            conn.rollback()
        return result
    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, f"Error de integridad en BD: {error}"
    finally:
        database.disconnect_db(conn)

def register_new_applicant(
    dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email, id_comision,
    sexo="Sin especificar",
):
    """
    Valida cupos y datos ANTES de registrar a la persona y su inscripción
    en una única transacción atómica.
    """
    # 1. Validaciones previas de formato antes de tocar la base de datos
    if not validators.validate_dni(str(dni)):
        return False, "DNI inválido (debe tener entre 7 y 8 dígitos numéricos)."
    if not validators.validate_date(str(fecha_nac)):
        return False, "Fecha de nacimiento inválida en calendario o futura."
    if not validators.validate_email(str(email)):
        return False, "Formato de correo electrónico no válido."
    if sexo not in ("Hombre", "Mujer", "Sin especificar"):
        return False, "Seleccione una opción válida para el sexo."

    conn = database.connect_db()
    try:
        cursor = conn.cursor()

        # Validar edad mínima con la configurada en el curso
        cursor.execute(
            """
            SELECT cur.edad_minima
            FROM Comision c
            JOIN Curso cur ON c.id_curso = cur.id_curso
            WHERE c.id_comision = ?
            """,
            (id_comision,)
        )
        curso_data = cursor.fetchone()
        edad_min = curso_data[0] if curso_data else MINIMUM_AGE
        
        if not validators.validate_minimum_age(str(fecha_nac), edad_min):
            return False, f"Inscripción rechazada: La edad mínima obligatoria es de {edad_min} años."

        # 2. Verificar disponibilidad de cupos de la comisión y curso de antemano
        has_quota, quota_msg = check_commission_availability(id_comision, cursor=cursor)
        if not has_quota:
            return False, quota_msg

        # 3. Comprobar si el DNI ya existe en el sistema
        cursor.execute("SELECT id_persona FROM Persona WHERE dni = ?", (str(dni).strip(),))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("SELECT id_inscripcion FROM Inscripcion WHERE id_persona = ?", (existing[0],))
            if cursor.fetchone():
                return False, "Inscripción rechazada: La persona ya posee un curso asignado."
            id_persona = existing[0]
            if sexo != "Sin especificar":
                cursor.execute(
                    "UPDATE Persona SET sexo = ? WHERE id_persona = ?",
                    (sexo, id_persona),
                )
        else:
            cursor.execute(
                """
                INSERT INTO Persona (dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email, sexo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (str(dni).strip(), nombre.strip(), apellido.strip(), str(fecha_nac).strip(),
                 direccion.strip(), localidad.strip(), telefono.strip(), str(email).strip(), sexo)
            )
            id_persona = cursor.lastrowid

        # 4. Inscribir formalmente
        result = _register_applicant(cursor, id_persona, id_comision)
        if result[0]:
            conn.commit()
            cursor.execute(
                "SELECT id_inscripcion FROM Inscripcion WHERE id_persona = ? AND id_comision = ?",
                (id_persona, id_comision),
            )
            inscription_id = cursor.fetchone()[0]
            result = (True, f"{result[1]} {_send_enrollment_email(inscription_id)}")
        else:
            conn.rollback()
        return result
    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, f"Error de integridad en BD: {error}"
    finally:
        database.disconnect_db(conn)

# --- CRUD TABLA PERSONA ---

def update_person(
    id_persona: int, dni: str, nombre: str, apellido: str, fecha_nac: str,
    direccion: str, localidad: str, telefono: str, email: str,
    sexo: str = "Sin especificar",
):
    """
    Actualiza la información de un registro guardado en la tabla Persona.
    Permite modificar cualquier campo garantizando que DNI sea único (UNIQUE)
    y que la fecha cumpla con la edad mínima.
    """
    if not validators.validate_dni(str(dni)):
        return False, "DNI inválido (debe contener entre 7 y 8 números)."
    if not validators.validate_date(str(fecha_nac)):
        return False, "Fecha de nacimiento inválida o futura."
    if not validators.validate_minimum_age(str(fecha_nac), MINIMUM_AGE):
        return False, f"La persona debe tener al menos {MINIMUM_AGE} años cumplidos."
    if not validators.validate_email(str(email)):
        return False, "Formato de correo electrónico no válido."
    if sexo not in ("Hombre", "Mujer", "Sin especificar"):
        return False, "Seleccione una opción válida para el sexo."
    if not (validators.validate_not_empty(nombre) and validators.validate_not_empty(apellido)):
        return False, "El nombre y el apellido no pueden estar vacíos."

    conn = database.connect_db()
    try:
        cursor = conn.cursor()
        # Verificar que el nuevo DNI no pertenezca a otra persona
        cursor.execute("SELECT id_persona FROM Persona WHERE dni = ? AND id_persona != ?", (str(dni).strip(), id_persona))
        if cursor.fetchone():
            return False, f"El DNI {dni} ya se encuentra registrado por otra persona."

        cursor.execute(
            """
            UPDATE Persona
            SET dni = ?, nombre = ?, apellido = ?, fecha_nac = ?, direccion = ?, localidad = ?, telefono = ?, email = ?, sexo = ?
            WHERE id_persona = ?
            """,
            (str(dni).strip(), nombre.strip(), apellido.strip(), str(fecha_nac).strip(),
             direccion.strip(), localidad.strip(), telefono.strip(), str(email).strip(), sexo, id_persona)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            return False, "No se encontró a la persona solicitada para actualizar."

        conn.commit()
        return True, "Datos personales actualizados correctamente."
    except sqlite3.IntegrityError as error:
        conn.rollback()
        return False, f"Error de integridad (posible DNI duplicado): {error}"
    finally:
        database.disconnect_db(conn)

def delete_person(id_persona: int):
    """
    Elimina a una persona y su inscripción asociada por cascada.
    Si era titular admitido, promueve automáticamente al siguiente de la lista de espera.
    """
    conn = database.connect_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.nombre, p.apellido, p.dni, i.id_inscripcion, i.estado, i.id_comision, com.codigo, cur.nombre
            FROM Persona p
            LEFT JOIN Inscripcion i ON p.id_persona = i.id_persona
            LEFT JOIN Comision com ON i.id_comision = com.id_comision
            LEFT JOIN Curso cur ON com.id_curso = cur.id_curso
            WHERE p.id_persona = ?
            """,
            (id_persona,)
        )
        data = cursor.fetchone()
        if not data:
            conn.rollback()
            return False, "Persona no encontrada en la base de datos."

        p_nom, p_ape, p_dni, insc_id, estado, comm_id, comm_code, course_name = data

        # Borrado en cascada
        cursor.execute("DELETE FROM Persona WHERE id_persona = ?", (id_persona,))

        promoted_msg = ""
        promoted_id = None
        if estado == 1 and comm_id:
            cursor.execute(
                """
                SELECT i.id_inscripcion, p.nombre, p.apellido, p.dni
                FROM Inscripcion i
                JOIN Persona p ON i.id_persona = p.id_persona
                WHERE i.id_comision = ? AND i.estado = 0
                ORDER BY datetime(i.fecha_hora) ASC, i.id_inscripcion ASC
                LIMIT 1
                """,
                (comm_id,)
            )
            next_app = cursor.fetchone()
            if next_app:
                next_id, n_nom, n_ape, n_dni = next_app
                cursor.execute("UPDATE Inscripcion SET estado = 1 WHERE id_inscripcion = ?", (next_id,))
                promoted_id = next_id
                promoted_msg = f" Su vacante en {comm_code} fue otorgada a {n_nom} {n_ape} (DNI {n_dni}) de la lista de espera."

        conn.commit()
        if promoted_id is not None:
            promoted_msg += f" {_send_enrollment_email(promoted_id, confirmed=True)}"
        return True, f"Baja realizada para {p_nom} {p_ape} (DNI {p_dni}).{promoted_msg}"
    except sqlite3.Error as error:
        conn.rollback()
        return False, f"Error de base de datos al eliminar persona: {error}"
    finally:
        database.disconnect_db(conn)

# --- CRUD TABLA CURSO ---

def get_all_courses():
    """Retorna todos los cursos."""
    return execute_query("SELECT id_curso, nombre, criterio, edad_minima, cupo_maximo FROM Curso", fetch=True)

def get_course_by_id(id_curso: int):
    """Retorna los datos de un curso por ID."""
    return execute_query("SELECT id_curso, nombre, criterio, edad_minima, cupo_maximo FROM Curso WHERE id_curso = ?", (id_curso,), fetch=True)

def create_course(nombre: str, criterio: str, edad_minima: int = 16, cupo_maximo: int = 50):
    """Crea un nuevo curso en el sistema."""
    if not (validators.validate_not_empty(nombre) and validators.validate_not_empty(criterio)):
        return False, "El nombre y el criterio no pueden estar vacíos."
    criterio_clean = criterio.strip()
    if criterio_clean not in ["Sorteo", "Orden de llegada"]:
        return False, "El criterio debe ser 'Sorteo' o 'Orden de llegada'."

    conn = database.connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_curso FROM Curso WHERE LOWER(nombre) = LOWER(?)", (nombre.strip(),))
        if cursor.fetchone():
            return False, f"Ya existe un curso registrado con el nombre '{nombre.strip()}'."

        cursor.execute("INSERT INTO Curso (nombre, criterio, edad_minima, cupo_maximo) VALUES (?, ?, ?, ?)", (nombre.strip(), criterio_clean, edad_minima, cupo_maximo))
        conn.commit()
        return True, f"Curso '{nombre.strip()}' creado con éxito (ID: {cursor.lastrowid})."
    except sqlite3.Error as err:
        conn.rollback()
        return False, f"Error al crear curso: {err}"
    finally:
        database.disconnect_db(conn)

def update_course(id_curso: int, nombre: str, criterio: str, edad_minima: int = 16, cupo_maximo: int = 50):
    """Modifica los atributos de un curso existente."""
    if not (validators.validate_not_empty(nombre) and validators.validate_not_empty(criterio)):
        return False, "El nombre y el criterio no pueden estar vacíos."
    criterio_clean = criterio.strip()
    if criterio_clean not in ["Sorteo", "Orden de llegada"]:
        return False, "El criterio debe ser 'Sorteo' o 'Orden de llegada'."

    conn = database.connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_curso FROM Curso WHERE LOWER(nombre) = LOWER(?) AND id_curso != ?", (nombre.strip(), id_curso))
        if cursor.fetchone():
            return False, f"Ya existe otro curso con el nombre '{nombre.strip()}'."

        cursor.execute(
            "UPDATE Curso SET nombre = ?, criterio = ?, edad_minima = ?, cupo_maximo = ? WHERE id_curso = ?",
            (nombre.strip(), criterio_clean, edad_minima, cupo_maximo, id_curso)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            return False, "No se encontró el curso a modificar."
        conn.commit()
        return True, "Curso actualizado con éxito."
    except sqlite3.Error as err:
        conn.rollback()
        return False, f"Error al actualizar curso: {err}"
    finally:
        database.disconnect_db(conn)

def delete_course(id_curso: int):
    """Elimina un curso y sus comisiones e inscripciones vinculadas."""
    conn = database.connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM Curso WHERE id_curso = ?", (id_curso,))
        course = cursor.fetchone()
        if not course:
            return False, "El curso seleccionado no existe."
        course_name = course[0]

        cursor.execute("DELETE FROM Curso WHERE id_curso = ?", (id_curso,))
        conn.commit()
        return True, f"Curso '{course_name}' y todas sus dependencias fueron eliminados correctamente."
    except sqlite3.Error as err:
        conn.rollback()
        return False, f"Error al eliminar curso: {err}"
    finally:
        database.disconnect_db(conn)

# --- CRUD TABLA COMISION ---

def get_all_commissions():
    """Retorna comisiones con sus límites y conteo de inscriptos actuales."""
    query = """
        SELECT c.id_comision, c.codigo, c.cupo_total, c.cupo_seleccion, cur.nombre, cur.criterio,
               (SELECT COUNT(*) FROM Inscripcion i WHERE i.id_comision = c.id_comision) AS inscriptos,
               (SELECT COUNT(*) FROM Inscripcion i WHERE i.id_comision = c.id_comision AND i.estado = 1) AS admitidos,
               (SELECT COUNT(*) FROM Inscripcion i WHERE i.id_comision = c.id_comision AND i.estado = 0) AS en_espera,
               c.id_curso, cur.edad_minima
        FROM Comision c
        JOIN Curso cur ON c.id_curso = cur.id_curso
        ORDER BY c.id_comision ASC
    """
    return execute_query(query, fetch=True)

def get_commission_by_id(id_comision: int):
    """Retorna los datos de una comisión puntual."""
    query = """
        SELECT c.id_comision, c.codigo, c.cupo_total, c.cupo_seleccion, c.id_curso, cur.nombre
        FROM Comision c
        JOIN Curso cur ON c.id_curso = cur.id_curso
        WHERE c.id_comision = ?
    """
    return execute_query(query, (id_comision,), fetch=True)

def create_commission(codigo: str, cupo_total: int, cupo_seleccion: int, id_curso: int):
    """Crea una nueva comisión validando cupos y curso asociado."""
    if not validators.validate_not_empty(codigo):
        return False, "El código de comisión no puede estar vacío."
    if cupo_total <= 0:
        return False, "El cupo total debe ser un número positivo mayor a 0."
    if cupo_seleccion <= 0 or cupo_seleccion > cupo_total:
        return False, f"El cupo de selección debe ser mayor a 0 y menor o igual al cupo total ({cupo_total})."

    conn = database.connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_curso FROM Curso WHERE id_curso = ?", (id_curso,))
        if not cursor.fetchone():
            return False, "El curso seleccionado no existe."

        cursor.execute("SELECT id_comision FROM Comision WHERE codigo = ?", (codigo.strip(),))
        if cursor.fetchone():
            return False, f"Ya existe una comisión con el código '{codigo.strip()}'."

        cursor.execute(
            """
            INSERT INTO Comision (codigo, cupo_total, cupo_seleccion, id_curso)
            VALUES (?, ?, ?, ?)
            """,
            (codigo.strip(), cupo_total, cupo_seleccion, id_curso)
        )
        conn.commit()
        return True, f"Comisión '{codigo.strip()}' creada exitosamente."
    except sqlite3.Error as err:
        conn.rollback()
        return False, f"Error al crear comisión: {err}"
    finally:
        database.disconnect_db(conn)

def update_commission(id_comision: int, codigo: str, cupo_total: int, cupo_seleccion: int, id_curso: int):
    """Actualiza código, cupos y curso de una comisión."""
    if not validators.validate_not_empty(codigo):
        return False, "El código de comisión no puede estar vacío."
    if cupo_total <= 0:
        return False, "El cupo total debe ser mayor a 0."
    if cupo_seleccion <= 0 or cupo_seleccion > cupo_total:
        return False, f"El cupo de selección debe ser mayor a 0 y menor o igual al cupo total ({cupo_total})."

    conn = database.connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_curso FROM Curso WHERE id_curso = ?", (id_curso,))
        if not cursor.fetchone():
            return False, "El curso especificado no existe."

        cursor.execute("SELECT id_comision FROM Comision WHERE codigo = ? AND id_comision != ?", (codigo.strip(), id_comision))
        if cursor.fetchone():
            return False, f"El código '{codigo.strip()}' ya es utilizado por otra comisión."

        # Validar si el nuevo cupo_total es menor a los inscriptos actuales
        cursor.execute("SELECT COUNT(*) FROM Inscripcion WHERE id_comision = ?", (id_comision,))
        inscriptos_actuales = cursor.fetchone()[0]
        if cupo_total < inscriptos_actuales:
            return False, f"No se puede reducir el cupo total a {cupo_total}: hay {inscriptos_actuales} inscriptos activos."

        cursor.execute(
            """
            UPDATE Comision
            SET codigo = ?, cupo_total = ?, cupo_seleccion = ?, id_curso = ?
            WHERE id_comision = ?
            """,
            (codigo.strip(), cupo_total, cupo_seleccion, id_curso, id_comision)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            return False, "No se encontró la comisión para actualizar."

        conn.commit()
        return True, "Comisión actualizada exitosamente."
    except sqlite3.Error as err:
        conn.rollback()
        return False, f"Error al actualizar comisión: {err}"
    finally:
        database.disconnect_db(conn)

def delete_commission(id_comision: int):
    """Elimina una comisión y sus inscripciones dependientes."""
    conn = database.connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo FROM Comision WHERE id_comision = ?", (id_comision,))
        comm = cursor.fetchone()
        if not comm:
            return False, "La comisión indicada no existe."
        code = comm[0]

        cursor.execute("DELETE FROM Comision WHERE id_comision = ?", (id_comision,))
        conn.commit()
        return True, f"Comisión '{code}' eliminada correctamente."
    except sqlite3.Error as err:
        conn.rollback()
        return False, f"Error al eliminar comisión: {err}"
    finally:
        database.disconnect_db(conn)

# --- GESTIÓN DE INSCRIPCIONES Y LISTA DE ESPERA ---

def get_waiting_list_by_commission(id_comision: int):
    """
    Retorna la lista de espera (estado = 0) para una comisión,
    ordenada estrictamente por fecha_hora ascendente e id_inscripcion.
    """
    query = """
        SELECT p.dni, p.nombre, p.apellido, com.codigo, i.fecha_hora, cur.nombre, i.id_inscripcion
        FROM Inscripcion i
        JOIN Persona p ON i.id_persona = p.id_persona
        JOIN Comision com ON i.id_comision = com.id_comision
        JOIN Curso cur ON com.id_curso = cur.id_curso
        WHERE i.id_comision = ? AND i.estado = 0
        ORDER BY datetime(i.fecha_hora) ASC, i.id_inscripcion ASC
    """
    return execute_query(query, (id_comision,), fetch=True)

def change_commission_registration(dni: str, new_id_comision: int):
    """
    Cambia a una persona de comisión verificando previamente la disponibilidad de cupos
    en la comisión de destino.
    """
    conn = database.connect_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT i.id_inscripcion, i.id_comision, i.estado, p.id_persona, p.nombre, p.apellido, com.codigo
            FROM Inscripcion i
            JOIN Persona p ON i.id_persona = p.id_persona
            JOIN Comision com ON i.id_comision = com.id_comision
            WHERE p.dni = ?
            """,
            (str(dni).strip(),)
        )
        insc = cursor.fetchone()
        if not insc:
            conn.rollback()
            return False, "No se encontró una inscripción para el DNI indicado."

        id_inscripcion, old_comm_id, old_estado, id_persona, p_nom, p_ape, old_code = insc

        if old_comm_id == new_id_comision:
            conn.rollback()
            return False, "La persona ya se encuentra inscripta en dicha comisión."

        # Verificar disponibilidad de cupos en la comisión destino
        has_quota, quota_msg = check_commission_availability(new_id_comision, cursor=cursor)
        if not has_quota:
            conn.rollback()
            return False, quota_msg

        # Reasignar a la nueva comisión y poner en espera (estado = 0)
        cursor.execute(
            "UPDATE Inscripcion SET id_comision = ?, estado = 0 WHERE id_inscripcion = ?",
            (new_id_comision, id_inscripcion)
        )

        # Si era titular, promover al siguiente en espera en la comisión origen
        promoted_msg = ""
        promoted_id = None
        if old_estado == 1:
            cursor.execute(
                """
                SELECT i.id_inscripcion, p.nombre, p.apellido, p.dni
                FROM Inscripcion i
                JOIN Persona p ON i.id_persona = p.id_persona
                WHERE i.id_comision = ? AND i.estado = 0
                ORDER BY datetime(i.fecha_hora) ASC, i.id_inscripcion ASC
                LIMIT 1
                """,
                (old_comm_id,)
            )
            next_app = cursor.fetchone()
            if next_app:
                next_id, n_nom, n_ape, n_dni = next_app
                cursor.execute("UPDATE Inscripcion SET estado = 1 WHERE id_inscripcion = ?", (next_id,))
                promoted_id = next_id
                promoted_msg = f" Su vacante en {old_code} fue asignada a {n_nom} {n_ape} (DNI {n_dni})."

        conn.commit()
        if promoted_id is not None:
            promoted_msg += f" {_send_enrollment_email(promoted_id, confirmed=True)}"
        return True, f"Reasignación confirmada para {p_nom} {p_ape}. Pasa a la nueva comisión en lista de espera.{promoted_msg}"
    except sqlite3.Error as err:
        conn.rollback()
        return False, f"Error al cambiar comisión: {err}"
    finally:
        database.disconnect_db(conn)

def cancel_registration_by_dni(dni: str):
    """
    Cancela la inscripción de una persona (titular o en espera).
    Si era titular, promueve al siguiente de la lista de espera.
    """
    conn = database.connect_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT i.id_inscripcion, i.estado, i.id_comision, com.codigo, cur.nombre, p.nombre, p.apellido
            FROM Inscripcion i
            JOIN Persona p ON i.id_persona = p.id_persona
            JOIN Comision com ON i.id_comision = com.id_comision
            JOIN Curso cur ON com.id_curso = cur.id_curso
            WHERE p.dni = ?
            """,
            (str(dni).strip(),)
        )
        insc = cursor.fetchone()
        if not insc:
            conn.rollback()
            return False, "No se encontró una inscripción para el DNI indicado."

        id_inscripcion, estado, id_comision, comm_code, course_name, p_nom, p_ape = insc

        cursor.execute("DELETE FROM Inscripcion WHERE id_inscripcion = ?", (id_inscripcion,))

        promoted_msg = ""
        promoted_id = None
        if estado == 1:
            cursor.execute(
                """
                SELECT i.id_inscripcion, p.nombre, p.apellido, p.dni
                FROM Inscripcion i
                JOIN Persona p ON i.id_persona = p.id_persona
                WHERE i.id_comision = ? AND i.estado = 0
                ORDER BY datetime(i.fecha_hora) ASC, i.id_inscripcion ASC
                LIMIT 1
                """,
                (id_comision,)
            )
            next_app = cursor.fetchone()
            if next_app:
                next_id, n_nom, n_ape, n_dni = next_app
                cursor.execute("UPDATE Inscripcion SET estado = 1 WHERE id_inscripcion = ?", (next_id,))
                promoted_id = next_id
                promoted_msg = f" Su vacante titular fue asignada a {n_nom} {n_ape} (DNI {n_dni}) de la lista de espera."

        conn.commit()
        if promoted_id is not None:
            promoted_msg += f" {_send_enrollment_email(promoted_id, confirmed=True)}"
        return True, f"Inscripción cancelada para {p_nom} {p_ape} en {course_name} ({comm_code}).{promoted_msg}"
    except sqlite3.Error as err:
        conn.rollback()
        return False, f"Error al cancelar inscripción: {err}"
    finally:
        database.disconnect_db(conn)

def get_admitted_registration_by_dni(dni):
    """Obtiene los datos de la inscripción admitida de una persona por DNI."""
    query = """
        SELECT p.dni, p.nombre, p.apellido, cur.nombre, com.codigo, i.fecha_hora
        FROM Inscripcion i
        JOIN Persona p ON i.id_persona = p.id_persona
        JOIN Comision com ON i.id_comision = com.id_comision
        JOIN Curso cur ON com.id_curso = cur.id_curso
        WHERE p.dni = ? AND i.estado = 1
    """
    return execute_query(query, (str(dni).strip(),), fetch=True)

def deregister_admitted_applicant(dni):
    """Da de baja a una persona admitida y promueve al siguiente de su comisión."""
    conn = database.connect_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.id_persona, p.nombre, p.apellido, cur.nombre, com.codigo, com.id_comision
            FROM Inscripcion i
            JOIN Persona p ON i.id_persona = p.id_persona
            JOIN Comision com ON i.id_comision = com.id_comision
            JOIN Curso cur ON com.id_curso = cur.id_curso
            WHERE p.dni = ? AND i.estado = 1
            """,
            (dni,)
        )
        admitted = cursor.fetchone()
        if not admitted:
            conn.rollback()
            return False, "No se encontró una inscripción admitida para ese DNI."

        person_id, first_name, last_name, course_name, commission_code, commission_id = admitted
        cursor.execute("DELETE FROM Persona WHERE id_persona = ?", (person_id,))

        cursor.execute(
            """
            SELECT i.id_inscripcion, p.nombre, p.apellido, p.dni
            FROM Inscripcion i
            JOIN Persona p ON i.id_persona = p.id_persona
            WHERE i.id_comision = ? AND i.estado = 0
            ORDER BY datetime(i.fecha_hora) ASC, i.id_inscripcion ASC
            LIMIT 1
            """,
            (commission_id,)
        )
        next_applicant = cursor.fetchone()
        if next_applicant:
            inscription_id, next_first_name, next_last_name, next_dni = next_applicant
            cursor.execute(
                "UPDATE Inscripcion SET estado = 1 WHERE id_inscripcion = ?",
                (inscription_id,)
            )
            message = (
                f"Baja confirmada para {first_name} {last_name} en {course_name} "
                f"({commission_code}). El lugar fue asignado a {next_first_name} "
                f"{next_last_name} (DNI {next_dni}), siguiente por fecha y hora de inscripción."
            )
        else:
            message = (
                f"Baja confirmada para {first_name} {last_name} en {course_name} "
                f"({commission_code}). No había inscriptos pendientes en esta comisión."
            )

        conn.commit()
        if next_applicant:
            message += f" {_send_enrollment_email(inscription_id, confirmed=True)}"
        return True, message
    except sqlite3.Error as error:
        conn.rollback()
        return False, f"Error de base de datos al procesar la baja: {error}"
    finally:
        database.disconnect_db(conn)

def delete_person_by_dni(dni: str):
    """Elimina a una persona por su DNI promoviendo a la lista de espera si era admitida."""
    person = get_person_by_dni(dni)
    if not person:
        return False, "No se encontró una persona con ese DNI."
    return delete_person(person[0][0])

# --- CONSULTAS DE LECTURA GENERALES ---

def get_all_persons():
    """Retorna el listado completo de personas registradas."""
    return execute_query("SELECT id_persona, dni, nombre, apellido, fecha_nac FROM Persona", fetch=True)

def get_enrolled_by_course(course_id: int):
    """Lista inscriptos de un curso indicando estado (0 = Espera, 1 = Admitido)."""
    query = """
        SELECT p.dni, p.nombre, p.apellido, com.codigo, i.fecha_hora, i.estado
        FROM Inscripcion i
        JOIN Persona p ON i.id_persona = p.id_persona
        JOIN Comision com ON i.id_comision = com.id_comision
        WHERE com.id_curso = ?
        ORDER BY com.codigo ASC, i.fecha_hora ASC
    """
    return execute_query(query, (course_id,), fetch=True)

def get_admitted_by_course(course_id: int):
    """Lista únicamente a los titulares admitidos (estado = 1) de un curso."""
    query = """
        SELECT p.dni, p.nombre, p.apellido, com.codigo, i.fecha_hora
        FROM Inscripcion i
        JOIN Persona p ON i.id_persona = p.id_persona
        JOIN Comision com ON i.id_comision = com.id_comision
        WHERE com.id_curso = ? AND i.estado = 1
        ORDER BY com.codigo ASC, i.fecha_hora ASC
    """
    return execute_query(query, (course_id,), fetch=True)

# --- ADJUDICACIONES Y SORTEO ---

def run_lottery_assignment():
    """Ejecuta sorteo aleatorio para comisiones con criterio 'Sorteo'."""
    commissions = execute_query(
        """
        SELECT c.id_comision, c.cupo_seleccion, c.codigo, cur.nombre 
        FROM Comision c 
        JOIN Curso cur ON c.id_curso = cur.id_curso 
        WHERE cur.criterio = 'Sorteo'
        """,
        fetch=True
    )
    total_assigned = 0
    details = []

    for comm_id, cupo_max, codigo, nombre_curso in commissions:
        selected_count = execute_query(
            "SELECT COUNT(*) FROM Inscripcion WHERE id_comision = ? AND estado = 1",
            (comm_id,),
            fetch=True
        )[0][0]

        vacantes = cupo_max - selected_count
        if vacantes <= 0:
            continue

        inscriptions = execute_query(
            "SELECT id_inscripcion FROM Inscripcion WHERE id_comision = ? AND estado = 0",
            (comm_id,),
            fetch=True
        )

        if not inscriptions:
            continue

        candidate_ids = [row[0] for row in inscriptions]
        k = min(len(candidate_ids), vacantes)
        winners = random.sample(candidate_ids, k)

        for w_id in winners:
            execute_query("UPDATE Inscripcion SET estado = 1 WHERE id_inscripcion = ?", (w_id,))
        email_results = [
            _send_enrollment_email(w_id, confirmed=True) for w_id in winners
        ]
        total_assigned += k
        details.append(
            f"Comisión {codigo} ({nombre_curso}): {k} titular(es) asignado(s).\n"
            + "\n".join(f"  - {result}" for result in email_results)
        )

    return total_assigned, details

def run_fifo_assignment():
    """Asignación estricta por orden de llegada (FIFO)."""
    commissions = execute_query(
        """
        SELECT c.id_comision, c.cupo_seleccion, c.codigo, cur.nombre 
        FROM Comision c 
        JOIN Curso cur ON c.id_curso = cur.id_curso 
        WHERE cur.criterio = 'Orden de llegada'
        """,
        fetch=True
    )
    total_assigned = 0
    details = []

    for comm_id, cupo_max, codigo, nombre_curso in commissions:
        selected_count = execute_query(
            "SELECT COUNT(*) FROM Inscripcion WHERE id_comision = ? AND estado = 1",
            (comm_id,),
            fetch=True
        )[0][0]

        vacantes = cupo_max - selected_count
        if vacantes <= 0:
            continue

        inscriptions = execute_query(
            "SELECT id_inscripcion FROM Inscripcion WHERE id_comision = ? AND estado = 0 ORDER BY fecha_hora ASC",
            (comm_id,),
            fetch=True
        )

        if not inscriptions:
            continue

        assigned_ids = [row[0] for row in inscriptions[:vacantes]]

        for a_id in assigned_ids:
            execute_query("UPDATE Inscripcion SET estado = 1 WHERE id_inscripcion = ?", (a_id,))
        email_results = [
            _send_enrollment_email(a_id, confirmed=True) for a_id in assigned_ids
        ]
        total_assigned += len(assigned_ids)
        details.append(
            f"Comisión {codigo} ({nombre_curso}): {len(assigned_ids)} titular(es) asignado(s).\n"
            + "\n".join(f"  - {result}" for result in email_results)
        )

    return total_assigned, details

def get_all_persons_with_enrollment():
    """
    Retorna todas las personas con su inscripción asociada (si la tienen):
    id_persona, dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email,
    id_inscripcion, id_comision, codigo_comision, id_curso, nombre_curso, estado, fecha_inscripcion
    """
    query = """
        SELECT p.id_persona, p.dni, p.nombre, p.apellido, p.fecha_nac,
               p.direccion, p.localidad, p.telefono, p.email,
               i.id_inscripcion, i.id_comision, com.codigo, 
               cur.id_curso, cur.nombre, i.estado, i.fecha_hora, p.sexo
        FROM Persona p
        LEFT JOIN Inscripcion i ON p.id_persona = i.id_persona
        LEFT JOIN Comision com ON i.id_comision = com.id_comision
        LEFT JOIN Curso cur ON com.id_curso = cur.id_curso
        ORDER BY p.apellido ASC, p.nombre ASC
    """
    return execute_query(query, fetch=True)

def get_dashboard_stats():
    """Retorna métricas clave para el panel de control del sistema."""
    cursos = execute_query("SELECT COUNT(*) FROM Curso", fetch=True)[0][0]
    comisiones = execute_query("SELECT COUNT(*) FROM Comision", fetch=True)[0][0]
    inscriptos = execute_query("SELECT COUNT(*) FROM Inscripcion", fetch=True)[0][0]
    admitidos = execute_query("SELECT COUNT(*) FROM Inscripcion WHERE estado = 1", fetch=True)[0][0]
    en_espera = execute_query("SELECT COUNT(*) FROM Inscripcion WHERE estado = 0", fetch=True)[0][0]
    personas = execute_query("SELECT COUNT(*) FROM Persona", fetch=True)[0][0]
    return {
        "cursos": cursos,
        "comisiones": comisiones,
        "inscriptos": inscriptos,
        "admitidos": admitidos,
        "en_espera": en_espera,
        "personas": personas,
    }


def get_course_statistics():
    """Retorna inscriptos, estados y vacantes titulares agrupados por curso."""
    return execute_query(
        """
        SELECT cur.nombre,
               COALESCE(reg.inscriptos, 0),
               COALESCE(reg.admitidos, 0),
               COALESCE(reg.en_espera, 0),
               COALESCE(com.comisiones, 0),
               COALESCE(com.cupos_titulares, 0),
               COALESCE(cur.cupo_maximo, 0),
               COALESCE(com.cupo_comisiones, 0)
        FROM Curso cur
        LEFT JOIN (
            SELECT id_curso, COUNT(*) AS comisiones,
                   SUM(cupo_seleccion) AS cupos_titulares,
                   SUM(cupo_total) AS cupo_comisiones
            FROM Comision
            GROUP BY id_curso
        ) com ON com.id_curso = cur.id_curso
        LEFT JOIN (
            SELECT c.id_curso,
                   COUNT(i.id_inscripcion) AS inscriptos,
                   SUM(CASE WHEN i.estado = 1 THEN 1 ELSE 0 END) AS admitidos,
                   SUM(CASE WHEN i.estado = 0 THEN 1 ELSE 0 END) AS en_espera
            FROM Comision c
            LEFT JOIN Inscripcion i ON i.id_comision = c.id_comision
            GROUP BY c.id_curso
        ) reg ON reg.id_curso = cur.id_curso
        ORDER BY cur.nombre COLLATE NOCASE
        """,
        fetch=True,
    )


def get_gender_statistics():
    """Retorna totales para las tres categorías estadísticas de sexo."""
    counts = dict(
        execute_query(
            """
            SELECT sexo, COUNT(*)
            FROM Persona p
            JOIN Inscripcion i ON i.id_persona = p.id_persona
            GROUP BY sexo
            """,
            fetch=True,
        )
    )
    return [
        (category, counts.get(category, 0))
        for category in ("Hombre", "Mujer", "Sin especificar")
    ]