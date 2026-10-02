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
        print(
            f"ID: {c[0]} | Código: {c[1]} | Inscriptos: {c[6]}/{c[2]} "
            f"| Admitidos: {c[7]}/{c[3]} | En espera: {c[8]} | Curso: {c[4]}"
        )
    input("\nPresione Enter para volver...")

def submenu_persons():
    """Permite listar, crear personas (validando edad mínima) e inscribirlas."""
    while True:
        clear_screen()
        print("--- GESTIÓN DE PERSONAS ---")
        print("1. Listar personas")
        print("2. Registrar nueva persona e inscribir")
        print("3. Dar de baja a una persona admitida")
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
            comms = operations.get_all_commissions()
            if not comms:
                print("No hay comisiones disponibles para realizar una inscripción.")
                input("\nPresione Enter para continuar...")
                continue

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

            print("\n--- Comisiones Disponibles ---")
            for c in comms:
                print(
                    f"[{c[0]}] {c[1]} - Curso: {c[4]} "
                    f"(Inscriptos: {c[6]}/{c[2]}, admitidos: {c[7]}/{c[3]}, "
                    f"en espera: {c[8]})"
                )

            commission_ids = {str(c[0]) for c in comms}
            choice = input("\nIngrese el ID de la comisión para inscribir: ").strip()
            while choice not in commission_ids:
                print("  -> Error: Seleccione una comisión disponible.")
                choice = input("Ingrese el ID de la comisión para inscribir: ").strip()

            ok, msg = operations.register_new_applicant(
                dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email, int(choice)
            )
            print(f"\n[{'EXITO' if ok else 'RECHAZADO'}] {msg}")

            input("\nPresione Enter para continuar...")

        elif opt == "3":
            clear_screen()
            dni = prompt_input("DNI de la persona admitida: ", validators.validate_dni, "DNI inválido.")
            admitted = operations.get_admitted_registration_by_dni(dni)
            if not admitted:
                print("\nNo se encontró una inscripción admitida para ese DNI.")
            else:
                record = admitted[0]
                print(
                    f"\nPersona: {record[1]} {record[2]} | Curso: {record[3]} "
                    f"| Comisión: {record[4]} | Inscripción: {record[5]}"
                )
                confirmation = input(
                    "\nLa baja eliminará también los datos de la persona. "
                    "¿Confirma la operación? (SI/no): "
                ).strip().lower()
                if confirmation == "si":
                    ok, msg = operations.deregister_admitted_applicant(dni)
                    print(f"\n[{'EXITO' if ok else 'RECHAZADO'}] {msg}")
                else:
                    print("\nBaja cancelada.")

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