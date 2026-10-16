"""
Punto de Entrada Principal - Sistema de Inscripción y Sorteo
Gimnasio Municipal - Versión 3.0.0 (Interfaz Gráfica Tkinter)
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import database
import gui

def main():
    """Punto de entrada principal: genera estructura de base de datos e inicia la GUI."""
    database.create_tables()
    gui.launch_app()

if __name__ == "__main__":
    main()