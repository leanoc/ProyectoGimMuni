import os
import operations
import validators
from config import MINIMUM_AGE

def clear_screen():
    """Limpia la terminal según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")

def prompt_input(label: str, validator_fn, error_msg: str, default: str = None) -> str:
    """
    Solicita un valor por consola hasta que cumpla la función validadora.
    Si se proporciona default y el usuario presiona Enter, se conserva el valor default.
    """
    while True:
        prompt_text = f"{label} [{default}]: " if default is not None else label
        val = input(prompt_text).strip()
        if default is not None and val == "":
            return default
        if validator_fn(val):
            return val
        print(f"  -> Error: {error_msg}")

# ==============================================================================
# SUBMENÚ 1: GESTIÓN Y CONSULTA DE CURSOS (CRUD)
# ==============================================================================

def submenu_courses():
    """Manejo integral de Cursos: lectura, creación, modificación y baja."""
    while True:
        clear_screen()
        print("========================================")
        print("     GESTIÓN Y CONSULTA DE CURSOS       ")
        print("========================================")
        print("1. Ver cursos e inscriptos")
        print("2. Crear nuevo curso")
        print("3. Modificar curso existente")
        print("4. Eliminar curso")
        print("0. Volver al menú principal")
        opt = input("\nSeleccione una opción: ").strip()

        if opt == "1":
            clear_screen()
            courses = operations.get_all_courses()
            if not courses:
                print("No hay cursos registrados en el sistema.")
                input("\nPresione Enter para continuar...")
                continue

            print("--- Cursos Disponibles ---")
            for c in courses:
                print(f"[{c[0]}] {c[1]} (Criterio: {c[2]})")
            
            c_id = input("\nIngrese el ID de un curso para ver inscriptos (o 0 para volver): ").strip()
            if c_id == "0" or not c_id.isdigit():
                continue

            records = operations.get_enrolled_by_course(int(c_id))
            clear_screen()
            if not records:
                print("No hay inscriptos registrados para este curso.")
            else:
                print(f"Listado de inscriptos para el curso seleccionado:\n")
                for r in records:
                    estado_txt = "ADMITIDO" if r[5] == 1 else "EN ESPERA"
                    print(f"DNI: {r[0]} | {r[1]} {r[2]} | Comisión: {r[3]} | Fecha: {r[4]} | Estado: {estado_txt}")
            input("\nPresione Enter para volver...")

        elif opt == "2":
            clear_screen()
            print("--- CREAR NUEVO CURSO ---")
            nombre = prompt_input("Nombre del curso: ", validators.validate_not_empty, "El nombre no puede estar vacío.")
            print("\nCriterios disponibles: 1. Sorteo | 2. Orden de llegada")
            crit_choice = input("Seleccione el criterio (1 o 2): ").strip()
            criterio = "Sorteo" if crit_choice == "1" else "Orden de llegada"

            ok, msg = operations.create_course(nombre, criterio)
            print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            input("\nPresione Enter para continuar...")

        elif opt == "3":
            clear_screen()
            print("--- MODIFICAR CURSO ---")
            courses = operations.get_all_courses()
            for c in courses:
                print(f"[{c[0]}] {c[1]} (Criterio actual: {c[2]})")

            c_id = input("\nIngrese el ID del curso a modificar (o 0 para cancelar): ").strip()
            if c_id == "0" or not c_id.isdigit():
                continue

            course_data = operations.get_course_by_id(int(c_id))
            if not course_data:
                print("\nCurso no encontrado.")
                input("\nPresione Enter para continuar...")
                continue

            current_c = course_data[0]
            nuevo_nombre = prompt_input("Nuevo nombre", validators.validate_not_empty, "El nombre no puede estar vacío.", default=current_c[1])
            print(f"Criterio actual: {current_c[2]}. Ingrese 1 para 'Sorteo', 2 para 'Orden de llegada' o Enter para conservar:")
            c_in = input("Opción: ").strip()
            if c_in == "1":
                nuevo_criterio = "Sorteo"
            elif c_in == "2":
                nuevo_criterio = "Orden de llegada"
            else:
                nuevo_criterio = current_c[2]

            ok, msg = operations.update_course(int(c_id), nuevo_nombre, nuevo_criterio)
            print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            input("\nPresione Enter para continuar...")

        elif opt == "4":
            clear_screen()
            print("--- ELIMINAR CURSO ---")
            courses = operations.get_all_courses()
            for c in courses:
                print(f"[{c[0]}] {c[1]} ({c[2]})")

            c_id = input("\nIngrese el ID del curso a eliminar (o 0 para cancelar): ").strip()
            if c_id == "0" or not c_id.isdigit():
                continue

            conf = input(f"ADVERTENCIA: Se eliminarán las comisiones e inscripciones del curso {c_id}. ¿Confirma? (SI/no): ").strip().lower()
            if conf == "si":
                ok, msg = operations.delete_course(int(c_id))
                print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            else:
                print("\nOperación cancelada.")
            input("\nPresione Enter para continuar...")

        elif opt == "0":
            break

# ==============================================================================
# SUBMENÚ 2: COMISIONES Y VACANTES (CRUD Y LISTA DE ESPERA)
# ==============================================================================

def submenu_commissions():
    """Manejo integral de Comisiones: visualización, listas de espera y CRUD."""
    while True:
        clear_screen()
        print("========================================")
        print("        COMISIONES Y VACANTES           ")
        print("========================================")
        print("1. Listar comisiones y vacantes")
        print("2. Ver lista de espera de una comisión")
        print("3. Crear nueva comisión")
        print("4. Modificar comisión (código / cupos)")
        print("5. Eliminar comisión")
        print("0. Volver al menú principal")
        opt = input("\nSeleccione una opción: ").strip()

        if opt == "1":
            clear_screen()
            print("--- COMISIONES Y VACANTES ACTUALES ---")
            commissions = operations.get_all_commissions()
            if not commissions:
                print("No hay comisiones cargadas.")
            else:
                for c in commissions:
                    libres = c[2] - c[6]
                    print(
                        f"ID: {c[0]} | Código: {c[1]} | Curso: {c[4]} | "
                        f"Inscriptos: {c[6]}/{c[2]} (Libres: {libres}) | "
                        f"Admitidos: {c[7]}/{c[3]} | En espera: {c[8]}"
                    )
            input("\nPresione Enter para volver...")

        elif opt == "2":
            clear_screen()
            print("--- LISTA DE ESPERA POR COMISIÓN ---")
            commissions = operations.get_all_commissions()
            for c in commissions:
                print(f"[{c[0]}] {c[1]} - Curso: {c[4]} (En espera: {c[8]})")

            comm_id = input("\nIngrese el ID de la comisión a consultar (o 0 para volver): ").strip()
            if comm_id == "0" or not comm_id.isdigit():
                continue

            waitlist = operations.get_waiting_list_by_commission(int(comm_id))
            clear_screen()
            if not waitlist:
                print(f"No hay postulantes en lista de espera para la comisión {comm_id}.")
            else:
                print(f"Lista de espera - Comisión {waitlist[0][3]} ({waitlist[0][5]}):\n")
                for index, item in enumerate(waitlist, start=1):
                    print(f"#{index} | DNI: {item[0]} | {item[1]} {item[2]} | Inscripción: {item[4]}")
            input("\nPresione Enter para continuar...")

        elif opt == "3":
            clear_screen()
            print("--- CREAR NUEVA COMISIÓN ---")
            courses = operations.get_all_courses()
            if not courses:
                print("Primero debe existir al menos un curso registrado.")
                input("\nPresione Enter para continuar...")
                continue

            for cur in courses:
                print(f"[{cur[0]}] {cur[1]}")

            c_id = prompt_input("ID del Curso: ", lambda x: x.isdigit() and any(c[0] == int(x) for c in courses), "ID de curso no válido.")
            codigo = prompt_input("Código de Comisión (ej. C3-NAT): ", validators.validate_not_empty, "El código no puede estar vacío.")
            
            while True:
                cupo_tot = input("Cupo total permitido: ").strip()
                if cupo_tot.isdigit() and int(cupo_tot) > 0:
                    cupo_total = int(cupo_tot)
                    break
                print("  -> Ingrese un número entero mayor a 0.")

            while True:
                cupo_sel = input(f"Cupo de selección / titulares (1 a {cupo_total}): ").strip()
                if cupo_sel.isdigit() and 1 <= int(cupo_sel) <= cupo_total:
                    cupo_seleccion = int(cupo_sel)
                    break
                print(f"  -> El cupo de selección debe ser un número entre 1 y {cupo_total}.")

            ok, msg = operations.create_commission(codigo, cupo_total, cupo_seleccion, int(c_id))
            print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            input("\nPresione Enter para continuar...")

        elif opt == "4":
            clear_screen()
            print("--- MODIFICAR COMISIÓN ---")
            commissions = operations.get_all_commissions()
            for c in commissions:
                print(f"[{c[0]}] {c[1]} - Curso: {c[4]} (Cupo total: {c[2]}, Cupo titulares: {c[3]})")

            comm_id = input("\nIngrese el ID de la comisión a modificar (o 0 para cancelar): ").strip()
            if comm_id == "0" or not comm_id.isdigit():
                continue

            comm_info = operations.get_commission_by_id(int(comm_id))
            if not comm_info:
                print("\nComisión no encontrada.")
                input("\nPresione Enter para continuar...")
                continue

            current_c = comm_info[0]
            nuevo_codigo = prompt_input("Nuevo código", validators.validate_not_empty, "El código no puede estar vacío.", default=current_c[1])
            nuevo_tot_str = prompt_input("Nuevo cupo total", lambda x: x.isdigit() and int(x) > 0, "Debe ser número positivo.", default=str(current_c[2]))
            nuevo_cupo_tot = int(nuevo_tot_str)
            nuevo_sel_str = prompt_input(
                f"Nuevo cupo de selección (1 a {nuevo_cupo_tot})",
                lambda x: x.isdigit() and 1 <= int(x) <= nuevo_cupo_tot,
                f"Debe estar entre 1 y {nuevo_cupo_tot}.",
                default=str(min(current_c[3], nuevo_cupo_tot))
            )
            nuevo_cupo_sel = int(nuevo_sel_str)

            ok, msg = operations.update_commission(int(comm_id), nuevo_codigo, nuevo_cupo_tot, nuevo_cupo_sel, current_c[4])
            print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            input("\nPresione Enter para continuar...")

        elif opt == "5":
            clear_screen()
            print("--- ELIMINAR COMISIÓN ---")
            commissions = operations.get_all_commissions()
            for c in commissions:
                print(f"[{c[0]}] {c[1]} - Curso: {c[4]} (Inscriptos: {c[6]})")

            comm_id = input("\nIngrese el ID de la comisión a eliminar (o 0 para cancelar): ").strip()
            if comm_id == "0" or not comm_id.isdigit():
                continue

            conf = input(f"ADVERTENCIA: Se eliminarán las inscripciones asociadas a la comisión {comm_id}. ¿Confirma? (SI/no): ").strip().lower()
            if conf == "si":
                ok, msg = operations.delete_commission(int(comm_id))
                print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            else:
                print("\nOperación cancelada.")
            input("\nPresione Enter para continuar...")

        elif opt == "0":
            break

# ==============================================================================
# SUBMENÚ 3: GESTIÓN DE PERSONAS E INSCRIPCIONES
# ==============================================================================

def submenu_persons():
    """Manejo de Personas e Inscripciones: altas con verificación previa de cupo, edición y bajas."""
    while True:
        clear_screen()
        print("========================================")
        print("  GESTIÓN DE PERSONAS E INSCRIPCIONES   ")
        print("========================================")
        print("1. Listar personas registradas")
        print("2. Registrar nueva inscripción (Verifica cupos primero)")
        print("3. Actualizar información de una persona guardada")
        print("4. Cambiar de comisión a un inscripto")
        print("5. Dar de baja inscripción o persona")
        print("0. Volver al menú principal")
        opt = input("\nSeleccione una opción: ").strip()

        if opt == "1":
            clear_screen()
            persons = operations.get_all_persons()
            if not persons:
                print("No hay personas cargadas en el sistema.")
            else:
                print(f"Total de personas registradas: {len(persons)}\n")
                for p in persons:
                    print(f"ID: {p[0]} | DNI: {p[1]} | {p[2]} {p[3]} | Fecha Nac: {p[4]}")
            input("\nPresione Enter para volver...")

        elif opt == "2":
            clear_screen()
            print("--- REGISTRO DE NUEVA INSCRIPCIÓN ---")
            comms = operations.get_all_commissions()
            if not comms:
                print("No existen comisiones configuradas en el sistema.")
                input("\nPresione Enter para continuar...")
                continue

            # PASO 1 OBLIGATORIO: VERIFICAR CUPOS PRIMERO
            print("Comisiones y estado de cupos en tiempo real:")
            available_commissions = []
            for c in comms:
                cupo_max = c[2]
                inscriptos = c[6]
                libres = cupo_max - inscriptos
                estado_cupo = f"DISPONIBLE ({libres} vacantes)" if libres > 0 else "SIN CUPO (COMPLETO)"
                print(f"[{c[0]}] {c[1]} - {c[4]} | Ocupación: {inscriptos}/{cupo_max} -> {estado_cupo}")
                if libres > 0:
                    available_commissions.append(str(c[0]))

            if not available_commissions:
                print("\n[AVISO] Todas las comisiones se encuentran con sus cupos al máximo.")
                print("Para poder registrar, aumente los cupos de una comisión o dé de baja algún inscripto.")
                input("\nPresione Enter para volver al menú...")
                continue

            choice = input("\nSeleccione el ID de la comisión a la que desea inscribir (o 0 para cancelar): ").strip()
            if choice == "0":
                continue

            # Verificar cupo en BD antes de solicitar cualquier dato personal
            if not choice.isdigit():
                print("  -> Error: Ingrese un ID numérico válido.")
                input("\nPresione Enter para continuar...")
                continue

            has_quota, quota_msg = operations.check_commission_availability(int(choice))
            if not has_quota:
                print(f"\n[RECHAZADO] {quota_msg}")
                print("Por favor elija una comisión con cupos libres.")
                input("\nPresione Enter para continuar...")
                continue

            # PASO 2: SOLICITAR DNI Y VERIFICAR DUPLICADOS
            print(f"\nComisión seleccionada válida con cupos disponibles. Ingrese los datos de la persona:")
            dni = prompt_input("DNI (7 u 8 dígitos): ", validators.validate_dni, "DNI inválido.")

            # Chequeo preventivo de duplicado
            existing = operations.get_person_by_dni(dni)
            if existing:
                admitted = operations.get_admitted_registration_by_dni(dni)
                print(f"\n[AVISO] El DNI {dni} ya pertenece a {existing[0][2]} {existing[0][3]}.")
                print("Comprobando si ya tiene inscripción activa...")
                enrolled_records = operations.execute_query(
                    "SELECT id_inscripcion FROM Inscripcion WHERE id_persona = ?",
                    (existing[0][0],),
                    fetch=True
                )
                if enrolled_records:
                    print("La persona ya posee una inscripción en un curso. No se permite duplicar cursos.")
                    input("\nPresione Enter para continuar...")
                    continue

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

            ok, msg = operations.register_new_applicant(
                dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email, int(choice)
            )
            print(f"\n[{'EXITO' if ok else 'RECHAZADO'}] {msg}")
            input("\nPresione Enter para continuar...")

        elif opt == "3":
            clear_screen()
            print("--- ACTUALIZAR INFORMACIÓN DE REGISTROS GUARDADOS ---")
            dni_busqueda = prompt_input("Ingrese el DNI de la persona a actualizar: ", validators.validate_dni, "DNI inválido.")
            person = operations.get_person_by_dni(dni_busqueda)
            if not person:
                print(f"\nNo se encontró a ninguna persona registrada con el DNI {dni_busqueda}.")
                input("\nPresione Enter para continuar...")
                continue

            person_id = person[0][0]
            full_data = operations.get_person_by_id(person_id)[0]
            # full_data: (id, dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email)
            print("\nDatos actuales (presione Enter para conservar el valor actual):")
            nuevo_dni = prompt_input("DNI", validators.validate_dni, "DNI inválido (7 u 8 dígitos).", default=full_data[1])
            nuevo_nombre = prompt_input("Nombre", validators.validate_not_empty, "No puede estar vacío.", default=full_data[2])
            nuevo_apellido = prompt_input("Apellido", validators.validate_not_empty, "No puede estar vacío.", default=full_data[3])
            
            while True:
                fn_input = input(f"Fecha Nacimiento [{full_data[4]}]: ").strip()
                if fn_input == "":
                    nueva_fecha_nac = full_data[4]
                    break
                if not validators.validate_date(fn_input):
                    print("  -> Error: Fecha inválida en calendario o futura.")
                    continue
                if not validators.validate_minimum_age(fn_input, MINIMUM_AGE):
                    print(f"  -> Error: La persona debe tener al menos {MINIMUM_AGE} años cumplidos.")
                    continue
                nueva_fecha_nac = fn_input
                break

            nueva_direccion = prompt_input("Dirección", validators.validate_not_empty, "No puede estar vacía.", default=full_data[5] or "S/D")
            nueva_localidad = prompt_input("Localidad", validators.validate_not_empty, "No puede estar vacía.", default=full_data[6] or "S/D")
            nuevo_telefono = prompt_input("Teléfono", validators.validate_not_empty, "No puede estar vacío.", default=full_data[7] or "S/D")
            nuevo_email = prompt_input("Email", validators.validate_email, "Email inválido.", default=full_data[8] or "test@test.com")

            ok, msg = operations.update_person(
                person_id, nuevo_dni, nuevo_nombre, nuevo_apellido, nueva_fecha_nac,
                nueva_direccion, nueva_localidad, nuevo_telefono, nuevo_email
            )
            print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            input("\nPresione Enter para continuar...")

        elif opt == "4":
            clear_screen()
            print("--- CAMBIAR COMISIÓN A UN INSCRIPTO ---")
            dni = prompt_input("Ingrese el DNI del inscripto: ", validators.validate_dni, "DNI inválido.")
            
            # Consultar comisiones
            comms = operations.get_all_commissions()
            print("\nComisiones disponibles:")
            for c in comms:
                libres = c[2] - c[6]
                print(f"[{c[0]}] {c[1]} - {c[4]} (Ocupación: {c[6]}/{c[2]} - Vacantes: {libres})")

            new_comm_id = input("\nIngrese el ID de la nueva comisión de destino: ").strip()
            if not new_comm_id.isdigit():
                print("ID inválido.")
                input("\nPresione Enter para continuar...")
                continue

            ok, msg = operations.change_commission_registration(dni, int(new_comm_id))
            print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            input("\nPresione Enter para continuar...")

        elif opt == "5":
            clear_screen()
            print("--- DAR DE BAJA INSCRIPCIÓN O PERSONA ---")
            dni = prompt_input("Ingrese el DNI: ", validators.validate_dni, "DNI inválido.")
            person = operations.get_person_by_dni(dni)
            if not person:
                print(f"\nNo se encontró a ninguna persona con el DNI {dni}.")
                input("\nPresione Enter para continuar...")
                continue

            print(f"\nPersona encontrada: {person[0][2]} {person[0][3]} (DNI {person[0][1]})")
            print("Opciones de baja:")
            print("1. Cancelar solo la inscripción (conserva datos de la persona)")
            print("2. Eliminar completamente a la persona y su inscripción")
            print("0. Cancelar operación")
            baja_opt = input("\nSeleccione una opción: ").strip()

            if baja_opt == "1":
                ok, msg = operations.cancel_registration_by_dni(dni)
                print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            elif baja_opt == "2":
                ok, msg = operations.delete_person(person[0][0])
                print(f"\n[{'EXITO' if ok else 'ERROR'}] {msg}")
            else:
                print("\nOperación de baja cancelada.")

            input("\nPresione Enter para continuar...")

        elif opt == "0":
            break

# ==============================================================================
# SUBMENÚ 4: SORTEO, ASIGNACIONES Y RESULTADOS
# ==============================================================================

def submenu_selections():
    """Adjudicaciones de cupos, titulares y visualización de listas de espera."""
    while True:
        clear_screen()
        print("========================================")
        print("  ADJUDICACIÓN DE CUPOS Y RESULTADOS    ")
        print("========================================")
        print("1. Ejecutar SORTEO de Natación (Aleatorio)")
        print("2. Aplicar ORDEN DE LLEGADA en Gimnasia Acuática (Sin sorteo)")
        print("3. Ver titulares admitidos de Natación")
        print("4. Ver titulares admitidos de Gimnasia Acuática")
        print("5. Ver listas de espera de las comisiones")
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
        elif opt == "5":
            print("--- LISTAS DE ESPERA POR COMISIÓN ---\n")
            commissions = operations.get_all_commissions()
            for comm in commissions:
                c_id, c_code, c_nombre = comm[0], comm[1], comm[4]
                waitlist = operations.get_waiting_list_by_commission(c_id)
                print(f"=== Comisión {c_code} ({c_nombre}) - En espera: {len(waitlist)} ===")
                if not waitlist:
                    print("  (Sin postulantes en espera)")
                else:
                    for idx, w in enumerate(waitlist, start=1):
                        print(f"  #{idx:02d} | DNI: {w[0]} | {w[1]} {w[2]} | Inscripto: {w[4]}")
                print()
        elif opt == "0":
            break
        else:
            print("Opción inválida.")

        input("\nPresione Enter para continuar...")