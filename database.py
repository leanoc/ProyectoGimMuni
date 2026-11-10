import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system.db")

def connect_db():
    """Conecta con SQLite y fuerza la activación de claves foráneas."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def disconnect_db(conn):
    """Cierra la conexión activa si existe."""
    if conn:
        conn.close()

def execute_query(query, params=(), fetch=False):
    """Ejecuta consultas parametrizadas de lectura o escritura de forma segura."""
    conn = connect_db()
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
    finally:
        disconnect_db(conn)
    return result

def create_tables():
    """Crea la estructura relacional de tablas."""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS Curso (
            id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            criterio TEXT NOT NULL,
            edad_minima INTEGER DEFAULT 16,
            cupo_maximo INTEGER DEFAULT 50
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Comision (
            id_comision INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            cupo_total INTEGER NOT NULL,
            cupo_seleccion INTEGER NOT NULL,
            id_curso INTEGER NOT NULL,
            FOREIGN KEY (id_curso) REFERENCES Curso(id_curso) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Persona (
            id_persona INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            fecha_nac DATE NOT NULL,
            direccion TEXT,
            localidad TEXT,
            telefono TEXT,
            email TEXT,
            sexo TEXT NOT NULL DEFAULT 'Sin especificar'
                CHECK (sexo IN ('Hombre', 'Mujer', 'Sin especificar'))
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Inscripcion (
            id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
            estado INTEGER DEFAULT 0,
            id_persona INTEGER UNIQUE NOT NULL,
            id_comision INTEGER NOT NULL,
            FOREIGN KEY (id_persona) REFERENCES Persona(id_persona) ON DELETE CASCADE,
            FOREIGN KEY (id_comision) REFERENCES Comision(id_comision) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Movimiento (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
            entidad TEXT NOT NULL,
            accion TEXT NOT NULL,
            detalle TEXT NOT NULL
        );
        """,
        """
        CREATE TRIGGER IF NOT EXISTS curso_movimiento_insert
        AFTER INSERT ON Curso BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Curso', 'Alta', 'Curso creado: ' || NEW.nombre);
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS curso_movimiento_update
        AFTER UPDATE ON Curso BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Curso', 'Modificación', 'Curso actualizado: ' || NEW.nombre);
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS curso_movimiento_delete
        AFTER DELETE ON Curso BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Curso', 'Baja', 'Curso eliminado: ' || OLD.nombre);
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS comision_movimiento_insert
        AFTER INSERT ON Comision BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Comisión', 'Alta', 'Comisión creada: ' || NEW.codigo);
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS comision_movimiento_update
        AFTER UPDATE ON Comision BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Comisión', 'Modificación', 'Comisión actualizada: ' || NEW.codigo);
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS comision_movimiento_delete
        AFTER DELETE ON Comision BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Comisión', 'Baja', 'Comisión eliminada: ' || OLD.codigo);
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS persona_movimiento_insert
        AFTER INSERT ON Persona BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Persona', 'Alta', 'Ficha de persona creada (ID ' || NEW.id_persona || ').');
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS persona_movimiento_update
        AFTER UPDATE ON Persona BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Persona', 'Modificación', 'Ficha de persona actualizada (ID ' || NEW.id_persona || ').');
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS persona_movimiento_delete
        AFTER DELETE ON Persona BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Persona', 'Baja', 'Ficha de persona eliminada (ID ' || OLD.id_persona || ').');
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS inscripcion_movimiento_insert
        AFTER INSERT ON Inscripcion BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Inscripción', 'Alta', 'Inscripción creada (ID ' || NEW.id_inscripcion || ', comisión ' || NEW.id_comision || ').');
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS inscripcion_movimiento_update
        AFTER UPDATE ON Inscripcion BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES (
                'Inscripción',
                CASE WHEN OLD.estado != NEW.estado AND NEW.estado = 1 THEN 'Adjudicación'
                     WHEN OLD.id_comision != NEW.id_comision THEN 'Reasignación'
                     ELSE 'Modificación' END,
                'Inscripción ' || NEW.id_inscripcion || ': comisión ' || OLD.id_comision || ' a ' || NEW.id_comision ||
                ', estado ' || OLD.estado || ' a ' || NEW.estado || '.'
            );
        END;
        """,
        """
        CREATE TRIGGER IF NOT EXISTS inscripcion_movimiento_delete
        AFTER DELETE ON Inscripcion BEGIN
            INSERT INTO Movimiento (entidad, accion, detalle)
            VALUES ('Inscripción', 'Baja', 'Inscripción eliminada (ID ' || OLD.id_inscripcion || ', comisión ' || OLD.id_comision || ').');
        END;
        """
    ]
    conn = connect_db()
    cursor = conn.cursor()
    try:
        for q in queries:
            cursor.execute(q)
        person_columns = {
            row[1] for row in cursor.execute("PRAGMA table_info(Persona)").fetchall()
        }
        if "sexo" not in person_columns:
            cursor.execute(
                "ALTER TABLE Persona ADD COLUMN sexo TEXT NOT NULL DEFAULT 'Sin especificar'"
            )
        conn.commit()
    finally:
        disconnect_db(conn)