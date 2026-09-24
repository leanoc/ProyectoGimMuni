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
            criterio TEXT NOT NULL
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
            email TEXT
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
        """
    ]
    conn = connect_db()
    cursor = conn.cursor()
    try:
        for q in queries:
            cursor.execute(q)
        conn.commit()
    finally:
        disconnect_db(conn)