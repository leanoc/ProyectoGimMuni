import os
import submenu

def clear_screen():
    """Limpia la terminal."""
    os.system("cls" if os.name == "nt" else "clear")

def display_main_menu():
    """Menú principal interactivo."""
    while True:
        clear_screen()
        print("================================")
        print("  SISTEMA INSCRIPCIÓN Y SORTEO  ")
        print("================================")
        print("1. Ver Cursos e Inscriptos")
        print("2. Ver Comisiones y Vacantes")
        print("3. Gestión de Personas e Inscripciones")
        print("4. Sorteo y Asignación de Cupos")
        print("0. Salir")
        
        choice = input("\nSeleccione una opción: ").strip()

        if choice == "1":
            submenu.submenu_courses()
        elif choice == "2":
            submenu.submenu_commissions()
        elif choice == "3":
            submenu.submenu_persons()
        elif choice == "4":
            submenu.submenu_selections()
        elif choice == "0":
            clear_screen()
            print("Cerrando sesión del sistema...")
            break
        else:
            input("\nOpción inválida. Presione Enter para volver a intentar...")