import random
import sqlite3
import database
from database import execute_query
from config import MINIMUM_AGE
import validators

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
            SELECT c.cupo_total, c.id_curso, cur.nombre, c.codigo
            FROM Comision c
            JOIN Curso cur ON c.id_curso = cur.id_curso
            WHERE c.id_comision = ?
            """,
            (id_comision,)
        )
        comm_data = cursor.fetchone()
        if not comm_data:
            return False, "La comisión indicada no existe."

        cupo_comision, id_curso, nombre_curso, codigo_comision = comm_data

        cursor.execute("SELECT COUNT(*) FROM Inscripcion WHERE id_comision = ?", (id_comision,))
        enrolled_comm = cursor.fetchone()[0]

        if enrolled_comm >= cupo_comision:
            return False, f"Inscripción rechazada: Cupo completo en la comisión {codigo_comision} ({enrolled_comm}/{cupo_comision})."

        cursor.execute("SELECT SUM(cupo_total) FROM Comision WHERE id_curso = ?", (id_curso,))
        sum_cupos = cursor.fetchone()[0]
        max_course_quota = sum_cupos if sum_cupos is not None else 0

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
        SELECT id_persona, dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email
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

    if not validators.validate_minimum_age(person_data[0], MINIMUM_AGE):
        return False, f"Inscripción rechazada: La edad mínima obligatoria es de {MINIMUM_AGE} años."

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
    dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email, id_comision
):
    """
    Valida cupos y datos ANTES de registrar a la persona y su inscripción
    en una única transacción atómica.
    """
    # 1. Validaciones previas de formato y edad mínima antes de tocar la base de datos
    if not validators.validate_dni(str(dni)):
        return False, "DNI inválido (debe tener entre 7 y 8 dígitos numéricos)."
    if not validators.validate_date(str(fecha_nac)):
        return False, "Fecha de nacimiento inválida en calendario o futura."
    if not validators.validate_minimum_age(str(fecha_nac), MINIMUM_AGE):
        return False, f"Inscripción rechazada: La edad mínima obligatoria es de {MINIMUM_AGE} años."
    if not validators.validate_email(str(email)):
        return False, "Formato de correo electrónico no válido."

    conn = database.connect_db()
    try:
        cursor = conn.cursor()

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
        else:
            cursor.execute(
                """
                INSERT INTO Persona (dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (str(dni).strip(), nombre.strip(), apellido.strip(), str(fecha_nac).strip(),
                 direccion.strip(), localidad.strip(), telefono.strip(), str(email).strip())
            )
            id_persona = cursor.lastrowid

        # 4. Inscribir formalmente
        result = _register_applicant(cursor, id_persona, id_comision)
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

# --- CRUD TABLA PERSONA ---

def update_person(id_persona: int, dni: str, nombre: str, apellido: str, fecha_nac: str, direccion: str, localidad: str, telefono: str, email: str):
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
            SET dni = ?, nombre = ?, apellido = ?, fecha_nac = ?, direccion = ?, localidad = ?, telefono = ?, email = ?
            WHERE id_persona = ?
            """,
            (str(dni).strip(), nombre.strip(), apellido.strip(), str(fecha_nac).strip(),
             direccion.strip(), localidad.strip(), telefono.strip(), str(email).strip(), id_persona)
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
                promoted_msg = f" Su vacante en {comm_code} fue otorgada a {n_nom} {n_ape} (DNI {n_dni}) de la lista de espera."

        conn.commit()
        return True, f"Baja realizada para {p_nom} {p_ape} (DNI {p_dni}).{promoted_msg}"
    except sqlite3.Error as error:
        conn.rollback()
        return False, f"Error de base de datos al eliminar persona: {error}"
    finally:
        database.disconnect_db(conn)

# --- CRUD TABLA CURSO ---

def get_all_courses():
    """Retorna todos los cursos."""
    return execute_query("SELECT id_curso, nombre, criterio FROM Curso", fetch=True)

def get_course_by_id(id_curso: int):
    """Retorna los datos de un curso por ID."""
    return execute_query("SELECT id_curso, nombre, criterio FROM Curso WHERE id_curso = ?", (id_curso,), fetch=True)

def create_course(nombre: str, criterio: str):
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

        cursor.execute("INSERT INTO Curso (nombre, criterio) VALUES (?, ?)", (nombre.strip(), criterio_clean))
        conn.commit()
        return True, f"Curso '{nombre.strip()}' creado con éxito (ID: {cursor.lastrowid})."
    except sqlite3.Error as err:
        conn.rollback()
        return False, f"Error al crear curso: {err}"
    finally:
        database.disconnect_db(conn)

def update_course(id_curso: int, nombre: str, criterio: str):
    """Modifica el nombre y/o criterio de un curso existente."""
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
            "UPDATE Curso SET nombre = ?, criterio = ? WHERE id_curso = ?",
            (nombre.strip(), criterio_clean, id_curso)
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
               c.id_curso
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
                promoted_msg = f" Su vacante en {old_code} fue asignada a {n_nom} {n_ape} (DNI {n_dni})."

        conn.commit()
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
                promoted_msg = f" Su vacante titular fue asignada a {n_nom} {n_ape} (DNI {n_dni}) de la lista de espera."

        conn.commit()
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

def run_swimming_lottery():
    """Ejecuta sorteo aleatorio para comisiones con criterio 'Sorteo' (Natación)."""
    commissions = execute_query(
        """
        SELECT c.id_comision, c.cupo_seleccion 
        FROM Comision c 
        JOIN Curso cur ON c.id_curso = cur.id_curso 
        WHERE cur.criterio = 'Sorteo'
        """,
        fetch=True
    )

    for comm_id, cupo_max in commissions:
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

def run_water_gym_assignment():
    """Asignación estricta por orden de llegada (FIFO) para Gimnasia Acuática."""
    commissions = execute_query(
        """
        SELECT c.id_comision, c.cupo_seleccion 
        FROM Comision c 
        JOIN Curso cur ON c.id_curso = cur.id_curso 
        WHERE cur.criterio = 'Orden de llegada'
        """,
        fetch=True
    )

    for comm_id, cupo_max in commissions:
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