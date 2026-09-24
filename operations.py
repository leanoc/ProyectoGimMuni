import random
import sqlite3
from database import execute_query
from config import MINIMUM_AGE
import validators

# --- ALTAS Y VALIDACIONES DE INSCRIPCIÓN ---

def insert_person(dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email):
    """Inserta una persona en la tabla Persona."""
    query = """
        INSERT INTO Persona (dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(query, (dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email))

def get_person_by_dni(dni):
    """Obtiene el ID y datos básicos de una persona por su DNI."""
    query = "SELECT id_persona, dni, nombre, apellido, fecha_nac FROM Persona WHERE dni = ?"
    return execute_query(query, (dni,), fetch=True)

def register_applicant(id_persona: int, id_comision: int):
    """
    Inscribe a una persona validando:
    1. Que cumpla la edad mínima estipulada en config.py.
    2. Que no posea una inscripción previa en ningún curso (relación 1:1).
    3. Que la comisión no supere su cupo total permitido.
    4. Que el curso no supere su capacidad total dinámica (suma de sus comisiones).
    """
    # 1. Validación de edad mínima
    person_data = execute_query(
        "SELECT fecha_nac FROM Persona WHERE id_persona = ?",
        (id_persona,),
        fetch=True
    )
    if not person_data:
        return False, "La persona no existe en el padrón."

    if not validators.validate_minimum_age(person_data[0][0], MINIMUM_AGE):
        return False, f"Inscripción rechazada: La edad mínima obligatoria es de {MINIMUM_AGE} años."

    # 2. Validación de inscripción única por persona
    enrolled = execute_query(
        "SELECT id_inscripcion FROM Inscripcion WHERE id_persona = ?",
        (id_persona,),
        fetch=True
    )
    if enrolled:
        return False, "Inscripción rechazada: La persona ya posee un curso asignado."

    # 3. Validación de comisión y cupo individual
    comm_data = execute_query(
        """
        SELECT c.cupo_total, c.id_curso, cur.nombre
        FROM Comision c
        JOIN Curso cur ON c.id_curso = cur.id_curso
        WHERE c.id_comision = ?
        """,
        (id_comision,),
        fetch=True
    )
    if not comm_data:
        return False, "La comisión indicada no existe."

    cupo_comision, id_curso, nombre_curso = comm_data[0]

    enrolled_comm = execute_query(
        "SELECT COUNT(*) FROM Inscripcion WHERE id_comision = ?",
        (id_comision,),
        fetch=True
    )[0][0]

    if enrolled_comm >= cupo_comision:
        return False, f"Inscripción rechazada: Cupo completo en la comisión ({enrolled_comm}/{cupo_comision})."

    # 4. Validación de cupo total del curso calculado dinámicamente desde SQL
    max_course_quota = execute_query(
        "SELECT SUM(cupo_total) FROM Comision WHERE id_curso = ?",
        (id_curso,),
        fetch=True
    )[0][0]

    enrolled_course = execute_query(
        """
        SELECT COUNT(i.id_inscripcion)
        FROM Inscripcion i
        JOIN Comision c ON i.id_comision = c.id_comision
        WHERE c.id_curso = ?
        """,
        (id_curso,),
        fetch=True
    )[0][0]

    if enrolled_course >= max_course_quota:
        return False, f"Inscripción rechazada: Cupo global del curso {nombre_curso} agotado ({enrolled_course}/{max_course_quota})."

    try:
        execute_query(
            "INSERT INTO Inscripcion (id_persona, id_comision, estado) VALUES (?, ?, 0)",
            (id_persona, id_comision)
        )
        return True, f"Inscripción confirmada en {nombre_curso} ({enrolled_comm + 1}/{cupo_comision})."
    except sqlite3.IntegrityError as e:
        return False, f"Error de integridad en BD: {e}"

# --- CONSULTAS DE LECTURA ---

def get_all_courses():
    """Retorna todos los cursos."""
    return execute_query("SELECT id_curso, nombre, criterio FROM Curso", fetch=True)

def get_all_commissions():
    """Retorna comisiones con sus límites y conteo de inscriptos actuales."""
    query = """
        SELECT c.id_comision, c.codigo, c.cupo_total, c.cupo_seleccion, cur.nombre, cur.criterio,
               (SELECT COUNT(*) FROM Inscripcion i WHERE i.id_comision = c.id_comision) AS inscriptos
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