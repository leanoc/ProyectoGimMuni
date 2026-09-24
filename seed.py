import datetime
import database

FIRST_NAMES = [
    "Juan", "Maria", "Carlos", "Lucia", "Martin", "Sofia", "Agustin", "Valeria",
    "Esteban", "Camila", "Franco", "Julieta", "Diego", "Paula", "Nicolas",
    "Florencia", "Gonzalo", "Mariana", "Lucas", "Belen", "Federico", "Rocio"
]

LAST_NAMES = [
    "Perez", "Gomez", "Lopez", "Diaz", "Rodriguez", "Fernandez", "Alvarez",
    "Romero", "Torres", "Suarez", "Benitez", "Acosta", "Medina", "Herrera",
    "Aguirre", "Gimenez", "Castro", "Molina", "Ortiz", "Silva", "Nuñez"
]

CITIES = ["La Plata", "Berisso", "Ensenada", "Tolosa", "City Bell"]

def setup_base_data(cursor):
    """Inserta Cursos y Comisiones iniciales."""
    cursor.execute("SELECT COUNT(*) FROM Curso")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO Curso (id_curso, nombre, criterio) VALUES (?, ?, ?)",
            [
                (1, "Natación", "Sorteo"),
                (2, "Gimnasia Acuática", "Orden de llegada")
            ]
        )

    cursor.execute("SELECT COUNT(*) FROM Comision")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO Comision (id_comision, codigo, cupo_total, cupo_seleccion, id_curso) VALUES (?, ?, ?, ?, ?)",
            [
                (1, "C1-NAT", 30, 25, 1),
                (2, "C2-NAT", 30, 25, 1),
                (3, "C1-GIM", 50, 30, 2),
                (4, "C2-GIM", 50, 30, 2)
            ]
        )

def seed_database(total_persons=159):
    """Carga 159 personas mayores de 15 años e inscripciones secuenciales."""
    database.create_tables()
    conn = database.connect_db()
    cursor = conn.cursor()

    try:
        setup_base_data(cursor)

        # Plan de distribución: C1=30, C2=30, C3=50, C4=49 (Suma 159 de 160 cupos posibles)
        distribution_plan = [1] * 30 + [2] * 30 + [3] * 50 + [4] * 49

        base_time = datetime.datetime(2026, 3, 1, 8, 0, 0)
        base_dni = 40000000

        persons_data = []
        inscriptions_data = []

        for index in range(total_persons):
            dni = str(base_dni + index)
            first_name = FIRST_NAMES[index % len(FIRST_NAMES)]
            last_name = LAST_NAMES[index % len(LAST_NAMES)]
            
            # Asegurar edades entre 18 y 45 años para cumplir holgadamente la regla de edad
            birth_year = 1980 + (index % 25)
            birth_month = (index % 12) + 1
            birth_day = (index % 28) + 1
            birth_date = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"
            
            address = f"Calle {index + 1} N° {100 + index}"
            city = CITIES[index % len(CITIES)]
            phone = f"221{5000000 + index}"
            email = f"persona_{dni}@test.com"

            persons_data.append((
                dni, first_name, last_name, birth_date,
                address, city, phone, email
            ))

        cursor.executemany(
            """
            INSERT OR IGNORE INTO Persona 
            (dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            persons_data
        )

        cursor.execute("SELECT id_persona FROM Persona ORDER BY id_persona ASC LIMIT ?", (total_persons,))
        person_ids = [row[0] for row in cursor.fetchall()]

        for i, person_id in enumerate(person_ids):
            assigned_comm = distribution_plan[i]
            timestamp = (base_time + datetime.timedelta(minutes=i * 2)).strftime("%Y-%m-%d %H:%M:%S")
            inscriptions_data.append((timestamp, 0, person_id, assigned_comm))

        cursor.executemany(
            """
            INSERT OR IGNORE INTO Inscripcion 
            (fecha_hora, estado, id_persona, id_comision)
            VALUES (?, ?, ?, ?)
            """,
            inscriptions_data
        )

        conn.commit()
        print(f"Seeding completado con exito: {len(person_ids)} registros cargados.")

    except Exception as err:
        conn.rollback()
        print(f"Error durante la carga: {err}")
    finally:
        database.disconnect_db(conn)

if __name__ == "__main__":
    seed_database()