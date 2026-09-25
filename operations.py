import random
import sqlite3
import database
from database import execute_query
from config import MINIMUM_AGE
import validators

# --- ALTAS Y VALIDACIONES DE INSCRIPCIÓN ---

def get_person_by_dni(dni):
    """Obtiene el ID y datos básicos de una persona por su DNI."""
    query = "SELECT id_persona, dni, nombre, apellido, fecha_nac FROM Persona WHERE dni = ?"
    return execute_query(query, (dni,), fetch=True)

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

    cursor.execute(
        """
        SELECT c.cupo_total, c.id_curso, cur.nombre
        FROM Comision c
        JOIN Curso cur ON c.id_curso = cur.id_curso
        WHERE c.id_comision = ?
        """,
        (id_comision,)
    )
    comm_data = cursor.fetchone()
    if not comm_data:
        return False, "La comisión indicada no existe."

    cupo_comision, id_curso, nombre_curso = comm_data

    cursor.execute("SELECT COUNT(*) FROM Inscripcion WHERE id_comision = ?", (id_comision,))
    enrolled_comm = cursor.fetchone()[0]

    if enrolled_comm >= cupo_comision:
        return False, f"Inscripción rechazada: Cupo completo en la comisión ({enrolled_comm}/{cupo_comision})."

    cursor.execute(
        "SELECT SUM(cupo_total) FROM Comision WHERE id_curso = ?",
        (id_curso,)
    )
    max_course_quota = cursor.fetchone()[0]
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
    """Crea una persona y su inscripción en una única transacción."""
    conn = database.connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Persona (dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email)
        )
        result = _register_applicant(cursor, cursor.lastrowid, id_comision)
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
    return execute_query(query, (dni,), fetch=True)

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

# --- CONSULTAS DE LECTURA ---

def get_all_courses():
    """Retorna todos los cursos."""
    return execute_query("SELECT id_curso, nombre, criterio FROM Curso", fetch=True)

def get_all_commissions():
    """Retorna comisiones con sus límites y conteo de inscriptos actuales."""
    query = """
        SELECT c.id_comision, c.codigo, c.cupo_total, c.cupo_seleccion, cur.nombre, cur.criterio,
               (SELECT COUNT(*) FROM Inscripcion i WHERE i.id_comision = c.id_comision) AS inscriptos,
               (SELECT COUNT(*) FROM Inscripcion i WHERE i.id_comision = c.id_comision AND i.estado = 1) AS admitidos,
               (SELECT COUNT(*) FROM Inscripcion i WHERE i.id_comision = c.id_comision AND i.estado = 0) AS en_espera
        FROM Comision c
        JOIN Curso cur ON c.id_curso = cur.id_curso
    """
    return execute_query(query, fetch=True)

def get_all_persons():
    """Retorna el listado de personas registradas."""
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