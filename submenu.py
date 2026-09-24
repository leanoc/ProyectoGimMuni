import os
import operations
import validators
from config import MINIMUM_AGE

def clear_screen():
    """Limpia la terminal según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")

def prompt_input(label: str, validator_fn, error_msg: str) -> str:
    """Solicita un valor por consola hasta que cumpla la función validadora."""
    while True:
        val = input(label).strip()
        if validator_fn(val):
            return val
        print(f"  -> Error: {error_msg}")

def submenu_courses():
    """Consulta cursos e inscriptos."""
    while True:
        clear_screen()
        print("--- GESTIÓN Y CONSULTA DE CURSOS ---")
        courses = operations.get_all_courses()
        for c in courses:
            print(f"[{c[0]}] {c[1]} (Criterio: {c[2]})")
        print("[0] Volver al menú principal")

        opt = input("\nSeleccione el ID de un curso para ver inscriptos o 0: ").strip()
        if opt == "0":
            break

        if not opt.isdigit():
            input("\nEntrada inválida. Presione Enter para continuar...")
            continue

        records = operations.get_enrolled_by_course(int(opt))
        clear_screen()
        if not records:
            print("No hay inscriptos registrados para este curso.")
        else:
            print(f"Listado de inscriptos para el curso seleccionado:\n")
            for r in records:
                estado_txt = "ADMITIDO" if r[5] == 1 else "EN ESPERA"
                print(f"DNI: {r[0]} | {r[1]} {r[2]} | Comisión: {r[3]} | Fecha: {r[4]} | Estado: {estado_txt}")

        input("\nPresione Enter para volver a consultar...")

def submenu_commissions():
    """Muestra comisiones, cupos y ocupación actual."""
    clear_screen()
    print("--- COMISIONES Y VACANTES ---")
    commissions = operations.get_all_commissions()
    for c in commissions:
        print(f"ID: {c[0]} | Código: {c[1]} | Ocupación: {c[6]}/{c[2]} | Cupo Titulares: {c[3]} | Curso: {c[4]}")
    input("\nPresione Enter para volver...")

def submenu_persons():
    """Permite listar, crear personas (validando edad mínima) e inscribirlas."""
    while True:
        clear_screen()
        print("--- GESTIÓN DE PERSONAS ---")
        print("1. Listar personas")
        print("2. Registrar nueva persona e inscribir")
        print("0. Volver al menú principal")
        opt = input("\nSeleccione una opción: ").strip()

        if opt == "1":
            clear_screen()
            persons = operations.get_all_persons()
            if not persons:
                print("No hay personas cargadas.")
            else:
                for p in persons:
                    print(f"ID: {p[0]} | DNI: {p[1]} | {p[2]} {p[3]} | F.Nac: {p[4]}")
            input("\nPresione Enter para volver...")

        elif opt == "2":
            clear_screen()
            print("--- ALTA DE PERSONA ---")
            dni = prompt_input("DNI (7 u 8 dígitos): ", validators.validate_dni, "DNI inválido.")
            nombre = prompt_input("Nombre: ", validators.validate_not_empty, "El nombre no puede estar vacío.")
            apellido = prompt_input("Apellido: ", validators.validate_not_empty, "El apellido no puede estar vacío.")
            
            while True:
                fecha_nac = input("Fecha Nacimiento (AAAA-MM-DD): ").strip()
                if not validators.validate_date(fecha_nac):
                    print("  -> Error: Fecha inválida en calendario o futura.")
                    continue
                if not validators.validate_minimum_age(fecha_nac, MINIMUM_AGE):
                    print(f"  -> Error: La persona debe tener al menos {MINIMUM_AGE} años cumplidos.")
                    continue
                break

            direccion = prompt_input("Dirección: ", validators.validate_not_empty, "La dirección no puede estar vacía.")
            localidad = prompt_input("Localidad: ", validators.validate_not_empty, "La localidad no puede estar vacía.")
            telefono = prompt_input("Teléfono: ", validators.validate_not_empty, "El teléfono no puede estar vacío.")
            email = prompt_input("Email: ", validators.validate_email, "Email no válido.")

            try:
                operations.insert_person(dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email)
                print("\nPersona registrada en el padrón con éxito.")

                person = operations.get_person_by_dni(dni)
                if person:
                    p_id = person[0][0]
                    print("\n--- Comisiones Disponibles ---")
                    comms = operations.get_all_commissions()
                    for c in comms:
                        print(f"[{c[0]}] {c[1]} - Curso: {c[4]} (Ocupación: {c[6]}/{c[2]})")
                    
                    choice = input("\nIngrese ID de comisión para inscribir (o 0 para omitir): ").strip()
                    if choice.isdigit() and int(choice) > 0:
                        ok, msg = operations.register_applicant(p_id, int(choice))
                        print(f"\n[{'EXITO' if ok else 'RECHAZADO'}] {msg}")

            except Exception as e:
                print(f"\nError durante la operación: {e}")

            input("\nPresione Enter para continuar...")

        elif opt == "0":
            break

def submenu_selections():
    """Asignación de cupos y visualización de admitidos."""
    while True:
        clear_screen()
        print("--- ADJUDICACIÓN DE CUPOS Y RESULTADOS ---")
        print("1. Ejecutar SORTEO de Natación (Aleatorio)")
        print("2. Aplicar ORDEN DE LLEGADA en Gimnasia Acuática (Sin sorteo)")
        print("3. Ver titulares admitidos de Natación")
        print("4. Ver titulares admitidos de Gimnasia Acuática")
        print("0. Volver al menú principal")
        opt = input("\nSeleccione una opción: ").strip()

        clear_screen()
        if opt == "1":
            operations.run_swimming_lottery()
            print("Sorteo de Natación finalizado correctamente.")
        elif opt == "2":
            operations.run_water_gym_assignment()
            print("Asignación de Gimnasia Acuática completada por orden de llegada.")
        elif opt == "3":
            admitted = operations.get_admitted_by_course(1)
            if not admitted:
                print("No hay titulares confirmados para Natación.")
            else:
                print("Titulares admitidos - Natación:\n")
                for a in admitted:
                    print(f"DNI: {a[0]} | {a[1]} {a[2]} | Comisión: {a[3]} | Fecha: {a[4]}")
        elif opt == "4":
            admitted = operations.get_admitted_by_course(2)
            if not admitted:
                print("No hay titulares confirmados para Gimnasia Acuática.")
            else:
                print("Titulares admitidos - Gimnasia Acuática:\n")
                for a in admitted:
                    print(f"DNI: {a[0]} | {a[1]} {a[2]} | Comisión: {a[3]} | Fecha: {a[4]}")
        elif opt == "0":
            break
        else:
            print("Opción inválida.")

        input("\nPresione Enter para continuar...")