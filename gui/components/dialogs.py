"""
Diálogos modales y formularios interactivos para la GUI de Tkinter.
Gimnasio Municipal - Versión 3.0.0
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import tkinter as tk
from tkinter import ttk, messagebox
import operations
import validators
from config import MINIMUM_AGE
from gui.theme import (
    BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_DANGER, FONT_TITLE, FONT_SUBTITLE,
    FONT_SECTION, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)

def center_window(window, width, height):
    """Centra una ventana respecto a la pantalla o ventana padre."""
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


class BaseDialog(tk.Toplevel):
    """Ventana modal base con estilo consistente y manejo de foco."""
    def __init__(self, parent, title, width=500, height=450):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)
        center_window(self, width, height)
        self.result = False

        # Contenedor principal con padding
        self.main_container = tk.Frame(self, bg=BG_MAIN, padx=20, pady=18)
        self.main_container.pack(fill="both", expand=True)

        self.bind("<Escape>", lambda e: self.destroy())


class CourseDialog(BaseDialog):
    """Diálogo para creación o edición de Cursos."""
    def __init__(self, parent, course_data=None):
        title = "Editar Curso" if course_data else "Nuevo Curso"
        super().__init__(parent, title, width=460, height=420)
        self.course_data = course_data  # (id_curso, nombre, criterio, edad_minima, cupo_maximo)

        # Header
        lbl_head = tk.Label(
            self.main_container,
            text=f"📚 {title}",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=COLOR_PRIMARY
        )
        lbl_head.pack(anchor="w", pady=(0, 15))

        # Formulario
        form_frame = tk.Frame(self.main_container, bg=BG_CARD, padx=16, pady=16, relief="solid", bd=1)
        form_frame.pack(fill="both", expand=True)

        # Nombre
        tk.Label(form_frame, text="Nombre del Curso / Deporte:", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w", pady=(4, 2))
        self.ent_nombre = ttk.Entry(form_frame, width=35)
        self.ent_nombre.pack(fill="x", pady=(0, 10))

        # Criterio
        tk.Label(form_frame, text="Criterio de Adjudicación:", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w", pady=(4, 2))
        self.cb_criterio = ttk.Combobox(
            form_frame,
            values=["Sorteo", "Orden de llegada"],
            state="readonly"
        )
        self.cb_criterio.set("Sorteo")
        self.cb_criterio.pack(fill="x", pady=(0, 10))

        # Fila Edad Mínima y Cupo Máximo
        row_frame = tk.Frame(form_frame, bg=BG_CARD)
        row_frame.pack(fill="x", pady=(0, 10))

        f_left = tk.Frame(row_frame, bg=BG_CARD)
        f_left.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f_left, text="Edad Mínima:", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w")
        self.spin_edad = ttk.Spinbox(f_left, from_=1, to=120, width=10)
        self.spin_edad.set(16)
        self.spin_edad.pack(fill="x", pady=2)

        f_right = tk.Frame(row_frame, bg=BG_CARD)
        f_right.pack(side="right", fill="x", expand=True, padx=(5, 0))
        tk.Label(f_right, text="Cupo Máximo:", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w")
        self.spin_cupo = ttk.Spinbox(f_right, from_=1, to=1000, width=10)
        self.spin_cupo.set(50)
        self.spin_cupo.pack(fill="x", pady=2)

        # Cargar valores si es edición
        if course_data:
            self.ent_nombre.insert(0, str(course_data[1]))
            self.cb_criterio.set(str(course_data[2]))
            self.spin_edad.set(course_data[3] if course_data[3] is not None else 16)
            self.spin_cupo.set(course_data[4] if course_data[4] is not None else 50)

        # Botones de acción
        btn_frame = tk.Frame(self.main_container, bg=BG_MAIN)
        btn_frame.pack(fill="x", pady=(15, 0))

        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="right", padx=(5, 0))
        ttk.Button(
            btn_frame,
            text="Guardar Curso",
            style="Primary.TButton",
            command=self.save_course
        ).pack(side="right")

        self.ent_nombre.focus()

    def save_course(self):
        nombre = self.ent_nombre.get().strip()
        criterio = self.cb_criterio.get().strip()

        if not validators.validate_not_empty(nombre):
            messagebox.showwarning("Dato requerido", "El nombre del curso no puede estar vacío.", parent=self)
            self.ent_nombre.focus()
            return

        try:
            edad = int(self.spin_edad.get())
            cupo = int(self.spin_cupo.get())
            if edad < 1 or cupo < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "Edad mínima y Cupo máximo deben ser números enteros positivos.", parent=self)
            return

        if self.course_data:
            ok, msg = operations.update_course(self.course_data[0], nombre, criterio, edad, cupo)
        else:
            ok, msg = operations.create_course(nombre, criterio, edad, cupo)

        if ok:
            messagebox.showinfo("Éxito", msg, parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


class CommissionDialog(BaseDialog):
    """Diálogo para creación o edición de Comisiones."""
    def __init__(self, parent, comm_data=None):
        title = "Editar Comisión" if comm_data else "Nueva Comisión"
        super().__init__(parent, title, width=480, height=450)
        self.comm_data = comm_data  # Si existe: datos de la comisión
        self.courses = operations.get_all_courses()

        if not self.courses and not comm_data:
            messagebox.showwarning("Atención", "Debe existir al menos un curso antes de crear comisiones.", parent=parent)
            self.destroy()
            return

        lbl_head = tk.Label(
            self.main_container,
            text=f"👥 {title}",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=COLOR_PRIMARY
        )
        lbl_head.pack(anchor="w", pady=(0, 15))

        form_frame = tk.Frame(self.main_container, bg=BG_CARD, padx=16, pady=16, relief="solid", bd=1)
        form_frame.pack(fill="both", expand=True)

        # Curso
        tk.Label(form_frame, text="Curso Asociado:", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w", pady=(2, 2))
        self.course_map = {f"[{c[0]}] {c[1]}": c[0] for c in self.courses}
        self.cb_curso = ttk.Combobox(form_frame, values=list(self.course_map.keys()), state="readonly")
        if self.course_map:
            self.cb_curso.set(list(self.course_map.keys())[0])
        self.cb_curso.pack(fill="x", pady=(0, 8))

        # Código
        tk.Label(form_frame, text="Código de Comisión (ej. C1-NAT):", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w", pady=(2, 2))
        self.ent_codigo = ttk.Entry(form_frame)
        self.ent_codigo.pack(fill="x", pady=(0, 8))

        # Cupo Total
        tk.Label(form_frame, text="Cupo Total Permitido (Límite Máximo):", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w", pady=(2, 2))
        self.spin_cupo_tot = ttk.Spinbox(form_frame, from_=1, to=500)
        self.spin_cupo_tot.set(30)
        self.spin_cupo_tot.pack(fill="x", pady=(0, 8))

        # Cupo Selección
        tk.Label(form_frame, text="Cupo de Selección (Titulares Admitidos):", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w", pady=(2, 2))
        self.spin_cupo_sel = ttk.Spinbox(form_frame, from_=1, to=500)
        self.spin_cupo_sel.set(20)
        self.spin_cupo_sel.pack(fill="x", pady=(0, 8))

        if comm_data:
            # comm_data puede ser (id, codigo, cupo_total, cupo_seleccion, nombre_curso, criterio, ..., id_curso)
            self.ent_codigo.insert(0, str(comm_data[1]))
            self.spin_cupo_tot.set(comm_data[2])
            self.spin_cupo_sel.set(comm_data[3])
            # Seleccionar curso correspondiente
            curr_course_id = comm_data[9] if len(comm_data) > 9 else None
            for label, cid in self.course_map.items():
                if cid == curr_course_id:
                    self.cb_curso.set(label)
                    break

        btn_frame = tk.Frame(self.main_container, bg=BG_MAIN)
        btn_frame.pack(fill="x", pady=(15, 0))

        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="right", padx=(5, 0))
        ttk.Button(
            btn_frame,
            text="Guardar Comisión",
            style="Primary.TButton",
            command=self.save_commission
        ).pack(side="right")

    def save_commission(self):
        codigo = self.ent_codigo.get().strip()
        selected_course = self.cb_curso.get()

        if not validators.validate_not_empty(codigo):
            messagebox.showwarning("Dato requerido", "El código de comisión no puede estar vacío.", parent=self)
            return

        if selected_course not in self.course_map:
            messagebox.showwarning("Dato requerido", "Debe seleccionar un curso válido.", parent=self)
            return

        id_curso = self.course_map[selected_course]

        try:
            cupo_tot = int(self.spin_cupo_tot.get())
            cupo_sel = int(self.spin_cupo_sel.get())
            if cupo_tot <= 0 or cupo_sel <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "Los cupos deben ser números enteros mayores a cero.", parent=self)
            return

        if cupo_sel > cupo_tot:
            messagebox.showwarning("Inconsistencia", f"El cupo de selección ({cupo_sel}) no puede ser mayor al cupo total ({cupo_tot}).", parent=self)
            return

        if self.comm_data:
            ok, msg = operations.update_commission(self.comm_data[0], codigo, cupo_tot, cupo_sel, id_curso)
        else:
            ok, msg = operations.create_commission(codigo, cupo_tot, cupo_sel, id_curso)

        if ok:
            messagebox.showinfo("Éxito", msg, parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


class RegisterApplicantDialog(BaseDialog):
    """Diálogo completo de inscripción con verificación previa fail-fast de cupos."""
    def __init__(self, parent):
        super().__init__(parent, "Inscribir Nuevo Postulante", width=620, height=640)
        self.commissions = operations.get_all_commissions()

        lbl_head = tk.Label(
            self.main_container,
            text="📝 Inscribir Postulante",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=COLOR_PRIMARY
        )
        lbl_head.pack(anchor="w", pady=(0, 8))

        # Paso 1: Selección de Comisión y Visualización de Cupos en tiempo real
        f_comm = tk.LabelFrame(
            self.main_container,
            text=" 1. Comisión y Verificación de Vacantes ",
            font=FONT_SECTION,
            bg=BG_CARD,
            fg=TEXT_MAIN,
            padx=12,
            pady=10
        )
        f_comm.pack(fill="x", pady=(0, 10))

        self.comm_map = {}
        comm_options = []
        for c in self.commissions:
            # c: id, codigo, cupo_total, cupo_seleccion, nombre_curso, criterio, inscriptos, admitidos, en_espera, id_curso
            libres = c[2] - c[6]
            status_txt = f"{libres} vacantes libres" if libres > 0 else "SIN CUPO (LLENO)"
            label = f"[{c[1]}] {c[4]} - {c[6]}/{c[2]} ({status_txt})"
            self.comm_map[label] = c
            comm_options.append(label)

        tk.Label(f_comm, text="Seleccione Comisión:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w", pady=(0, 2))
        self.cb_comm = ttk.Combobox(f_comm, values=comm_options, state="readonly", width=55)
        if comm_options:
            self.cb_comm.set(comm_options[0])
        self.cb_comm.pack(fill="x", pady=(0, 4))
        self.cb_comm.bind("<<ComboboxSelected>>", self.on_commission_change)

        self.lbl_vacancy_alert = tk.Label(f_comm, text="", font=FONT_BODY_BOLD, bg=BG_CARD)
        self.lbl_vacancy_alert.pack(anchor="w")

        # Paso 2: Datos Personales
        f_pers = tk.LabelFrame(
            self.main_container,
            text=" 2. Datos Personales del Postulante ",
            font=FONT_SECTION,
            bg=BG_CARD,
            fg=TEXT_MAIN,
            padx=12,
            pady=10
        )
        f_pers.pack(fill="both", expand=True, pady=(0, 10))

        # Fila DNI con botón de auto-comprobación
        f_dni = tk.Frame(f_pers, bg=BG_CARD)
        f_dni.pack(fill="x", pady=(0, 6))

        tk.Label(f_dni, text="DNI (7 u 8 dígitos):", font=FONT_BODY_BOLD, bg=BG_CARD).pack(side="left")
        self.ent_dni = ttk.Entry(f_dni, width=15)
        self.ent_dni.pack(side="left", padx=8)
        ttk.Button(f_dni, text="🔍 Verificar DNI", command=self.check_existing_dni).pack(side="left")
        self.lbl_dni_status = tk.Label(f_dni, text="", font=FONT_SMALL, bg=BG_CARD)
        self.lbl_dni_status.pack(side="left", padx=8)

        # Fila Nombre y Apellido
        f_name = tk.Frame(f_pers, bg=BG_CARD)
        f_name.pack(fill="x", pady=(0, 6))

        f_nom = tk.Frame(f_name, bg=BG_CARD)
        f_nom.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f_nom, text="Nombre:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_nom = ttk.Entry(f_nom)
        self.ent_nom.pack(fill="x")

        f_ape = tk.Frame(f_name, bg=BG_CARD)
        f_ape.pack(side="right", fill="x", expand=True, padx=(5, 0))
        tk.Label(f_ape, text="Apellido:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_ape = ttk.Entry(f_ape)
        self.ent_ape.pack(fill="x")

        # Fila Fecha Nacimiento y Teléfono
        f_date_tel = tk.Frame(f_pers, bg=BG_CARD)
        f_date_tel.pack(fill="x", pady=(0, 6))

        f_date = tk.Frame(f_date_tel, bg=BG_CARD)
        f_date.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f_date, text="Fecha Nacimiento (AAAA-MM-DD):", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_fecha = ttk.Entry(f_date)
        self.ent_fecha.insert(0, "1995-05-15")
        self.ent_fecha.pack(fill="x")

        f_tel = tk.Frame(f_date_tel, bg=BG_CARD)
        f_tel.pack(side="right", fill="x", expand=True, padx=(5, 0))
        tk.Label(f_tel, text="Teléfono de Contacto:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_tel = ttk.Entry(f_tel)
        self.ent_tel.pack(fill="x")

        # Fila Dirección y Localidad
        f_dir_loc = tk.Frame(f_pers, bg=BG_CARD)
        f_dir_loc.pack(fill="x", pady=(0, 6))

        f_dir = tk.Frame(f_dir_loc, bg=BG_CARD)
        f_dir.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f_dir, text="Dirección:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_dir = ttk.Entry(f_dir)
        self.ent_dir.pack(fill="x")

        f_loc = tk.Frame(f_dir_loc, bg=BG_CARD)
        f_loc.pack(side="right", fill="x", expand=True, padx=(5, 0))
        tk.Label(f_loc, text="Localidad:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_loc = ttk.Entry(f_loc)
        self.ent_loc.pack(fill="x")

        # Fila Email
        tk.Label(f_pers, text="Correo Electrónico:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_email = ttk.Entry(f_pers)
        self.ent_email.pack(fill="x", pady=(0, 4))

        # Botones de pie
        btn_frame = tk.Frame(self.main_container, bg=BG_MAIN)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="right", padx=(5, 0))
        ttk.Button(
            btn_frame,
            text="Confirmar Inscripción",
            style="Primary.TButton",
            command=self.confirm_registration
        ).pack(side="right")

        self.on_commission_change()
        self.ent_dni.focus()

    def on_commission_change(self, event=None):
        selected = self.cb_comm.get()
        if not selected or selected not in self.comm_map:
            return
        c = self.comm_map[selected]
        libres = c[2] - c[6]
        if libres > 0:
            self.lbl_vacancy_alert.config(
                text=f"✓ Cupo disponible: {libres} vacantes en {c[1]} (Ocupación: {c[6]}/{c[2]}).",
                fg=COLOR_SUCCESS
            )
        else:
            self.lbl_vacancy_alert.config(
                text=f"⚠ Comisión completa ({c[6]}/{c[2]}). No se pueden admitir más inscripciones.",
                fg=COLOR_DANGER
            )

    def check_existing_dni(self):
        dni = self.ent_dni.get().strip()
        if not validators.validate_dni(dni):
            messagebox.showwarning("DNI Inválido", "Ingrese un DNI numérico válido de 7 u 8 dígitos.", parent=self)
            return

        person = operations.get_person_by_dni(dni)
        if person:
            p = operations.get_person_by_id(person[0][0])[0]
            self.ent_nom.delete(0, tk.END)
            self.ent_nom.insert(0, p[2])
            self.ent_ape.delete(0, tk.END)
            self.ent_ape.insert(0, p[3])
            self.ent_fecha.delete(0, tk.END)
            self.ent_fecha.insert(0, p[4])
            self.ent_dir.delete(0, tk.END)
            self.ent_dir.insert(0, p[5])
            self.ent_loc.delete(0, tk.END)
            self.ent_loc.insert(0, p[6])
            self.ent_tel.delete(0, tk.END)
            self.ent_tel.insert(0, p[7])
            self.ent_email.delete(0, tk.END)
            self.ent_email.insert(0, p[8])
            self.lbl_dni_status.config(text="✓ Persona encontrada en padrón.", fg=COLOR_SUCCESS)
        else:
            self.lbl_dni_status.config(text="Nuevo postulante (no registrado).", fg=TEXT_MUTED)

    def confirm_registration(self):
        selected_comm = self.cb_comm.get()
        if not selected_comm or selected_comm not in self.comm_map:
            messagebox.showwarning("Dato requerido", "Seleccione una comisión válida.", parent=self)
            return

        c = self.comm_map[selected_comm]
        id_comision = c[0]

        # Verificación fail-fast previa en la comisión
        has_quota, quota_msg = operations.check_commission_availability(id_comision)
        if not has_quota:
            messagebox.showerror("Cupo Agotado", quota_msg, parent=self)
            return

        dni = self.ent_dni.get().strip()
        nombre = self.ent_nom.get().strip()
        apellido = self.ent_ape.get().strip()
        fecha_nac = self.ent_fecha.get().strip()
        direccion = self.ent_dir.get().strip()
        localidad = self.ent_loc.get().strip()
        telefono = self.ent_tel.get().strip()
        email = self.ent_email.get().strip()

        # Validaciones de formato
        if not validators.validate_dni(dni):
            messagebox.showwarning("DNI Inválido", "El DNI debe contener entre 7 y 8 números.", parent=self)
            self.ent_dni.focus()
            return

        if not (validators.validate_not_empty(nombre) and validators.validate_not_empty(apellido)):
            messagebox.showwarning("Campo Vacío", "Nombre y Apellido son obligatorios.", parent=self)
            return

        if not validators.validate_date(fecha_nac):
            messagebox.showwarning("Fecha Inválida", "La fecha de nacimiento debe tener formato AAAA-MM-DD y ser válida.", parent=self)
            return

        if not validators.validate_email(email):
            messagebox.showwarning("Email Inválido", "Ingrese un correo electrónico con formato válido.", parent=self)
            return

        if not (validators.validate_not_empty(direccion) and validators.validate_not_empty(localidad) and validators.validate_not_empty(telefono)):
            messagebox.showwarning("Campos Requeridos", "Dirección, localidad y teléfono no pueden estar vacíos.", parent=self)
            return

        ok, msg = operations.register_new_applicant(
            dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email, id_comision
        )

        if ok:
            messagebox.showinfo("Inscripción Exitosa", msg, parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Inscripción Rechazada", msg, parent=self)


class EditPersonDialog(BaseDialog):
    """Diálogo para modificar datos de una persona registrada."""
    def __init__(self, parent, person_tuple):
        super().__init__(parent, "Modificar Datos de Persona", width=520, height=500)
        self.person = person_tuple  # id_persona, dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email...

        lbl_head = tk.Label(
            self.main_container,
            text=f"✏️ Editar: {person_tuple[2]} {person_tuple[3]}",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=COLOR_PRIMARY
        )
        lbl_head.pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(self.main_container, bg=BG_CARD, padx=14, pady=14, relief="solid", bd=1)
        form_frame.pack(fill="both", expand=True)

        tk.Label(form_frame, text="DNI:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w", pady=(2, 2))
        self.ent_dni = ttk.Entry(form_frame)
        self.ent_dni.insert(0, str(person_tuple[1]))
        self.ent_dni.pack(fill="x", pady=(0, 6))

        f_names = tk.Frame(form_frame, bg=BG_CARD)
        f_names.pack(fill="x", pady=(0, 6))
        f_nom = tk.Frame(f_names, bg=BG_CARD)
        f_nom.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Label(f_nom, text="Nombre:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_nom = ttk.Entry(f_nom)
        self.ent_nom.insert(0, str(person_tuple[2]))
        self.ent_nom.pack(fill="x")

        f_ape = tk.Frame(f_names, bg=BG_CARD)
        f_ape.pack(side="right", fill="x", expand=True, padx=(4, 0))
        tk.Label(f_ape, text="Apellido:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_ape = ttk.Entry(f_ape)
        self.ent_ape.insert(0, str(person_tuple[3]))
        self.ent_ape.pack(fill="x")

        tk.Label(form_frame, text="Fecha Nacimiento (AAAA-MM-DD):", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w", pady=(2, 2))
        self.ent_fecha = ttk.Entry(form_frame)
        self.ent_fecha.insert(0, str(person_tuple[4]))
        self.ent_fecha.pack(fill="x", pady=(0, 6))

        tk.Label(form_frame, text="Dirección:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w", pady=(2, 2))
        self.ent_dir = ttk.Entry(form_frame)
        self.ent_dir.insert(0, str(person_tuple[5]) if person_tuple[5] else "")
        self.ent_dir.pack(fill="x", pady=(0, 6))

        f_loc_tel = tk.Frame(form_frame, bg=BG_CARD)
        f_loc_tel.pack(fill="x", pady=(0, 6))
        f_loc = tk.Frame(f_loc_tel, bg=BG_CARD)
        f_loc.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Label(f_loc, text="Localidad:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_loc = ttk.Entry(f_loc)
        self.ent_loc.insert(0, str(person_tuple[6]) if person_tuple[6] else "")
        self.ent_loc.pack(fill="x")

        f_tel = tk.Frame(f_loc_tel, bg=BG_CARD)
        f_tel.pack(side="right", fill="x", expand=True, padx=(4, 0))
        tk.Label(f_tel, text="Teléfono:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w")
        self.ent_tel = ttk.Entry(f_tel)
        self.ent_tel.insert(0, str(person_tuple[7]) if person_tuple[7] else "")
        self.ent_tel.pack(fill="x")

        tk.Label(form_frame, text="Correo Electrónico:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w", pady=(2, 2))
        self.ent_email = ttk.Entry(form_frame)
        self.ent_email.insert(0, str(person_tuple[8]) if person_tuple[8] else "")
        self.ent_email.pack(fill="x", pady=(0, 6))

        btn_frame = tk.Frame(self.main_container, bg=BG_MAIN)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="right", padx=(5, 0))
        ttk.Button(
            btn_frame,
            text="Actualizar Información",
            style="Primary.TButton",
            command=self.save_person
        ).pack(side="right")

    def save_person(self):
        dni = self.ent_dni.get().strip()
        nombre = self.ent_nom.get().strip()
        apellido = self.ent_ape.get().strip()
        fecha_nac = self.ent_fecha.get().strip()
        direccion = self.ent_dir.get().strip()
        localidad = self.ent_loc.get().strip()
        telefono = self.ent_tel.get().strip()
        email = self.ent_email.get().strip()

        ok, msg = operations.update_person(
            self.person[0], dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email
        )
        if ok:
            messagebox.showinfo("Éxito", msg, parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error al Actualizar", msg, parent=self)


class ChangeCommissionDialog(BaseDialog):
    """Diálogo para reasignar a una persona a otra comisión con verificación previa."""
    def __init__(self, parent, dni, nombre, comision_actual):
        super().__init__(parent, "Cambiar Comisión", width=500, height=350)
        self.dni = dni
        self.comms = operations.get_all_commissions()

        lbl_head = tk.Label(
            self.main_container,
            text=f"🔄 Cambiar Comisión: {nombre}",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=COLOR_PRIMARY
        )
        lbl_head.pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(self.main_container, bg=BG_CARD, padx=14, pady=14, relief="solid", bd=1)
        form_frame.pack(fill="both", expand=True)

        tk.Label(
            form_frame,
            text=f"Postulante: {nombre} (DNI {dni})\nComisión Actual: {comision_actual}",
            font=FONT_BODY_BOLD,
            bg=BG_CARD,
            fg=TEXT_MAIN,
            justify="left"
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(form_frame, text="Seleccione la nueva comisión de destino:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(anchor="w", pady=(0, 2))

        self.comm_map = {}
        options = []
        for c in self.commms_filter(comision_actual):
            libres = c[2] - c[6]
            status = f"{libres} vacantes" if libres > 0 else "COMPLETA"
            label = f"[{c[1]}] {c[4]} ({status})"
            self.comm_map[label] = c[0]
            options.append(label)

        self.cb_dest = ttk.Combobox(form_frame, values=options, state="readonly", width=45)
        if options:
            self.cb_dest.set(options[0])
        self.cb_dest.pack(fill="x", pady=(0, 8))

        btn_frame = tk.Frame(self.main_container, bg=BG_MAIN)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="right", padx=(5, 0))
        ttk.Button(
            btn_frame,
            text="Confirmar Cambio",
            style="Primary.TButton",
            command=self.confirm_change
        ).pack(side="right")

    def commms_filter(self, current_code):
        return [c for c in self.comms if c[1] != current_code]

    def confirm_change(self):
        dest_label = self.cb_dest.get()
        if not dest_label or dest_label not in self.comm_map:
            messagebox.showwarning("Atención", "Debe seleccionar una comisión de destino.", parent=self)
            return

        new_comm_id = self.comm_map[dest_label]
        ok, msg = operations.change_commission_registration(self.dni, new_comm_id)
        if ok:
            messagebox.showinfo("Reasignación Exitosa", msg, parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error al Reasignar", msg, parent=self)


class DeregisterDialog(BaseDialog):
    """Diálogo modal con opciones claras de baja y aviso de reemplazo de lista de espera."""
    def __init__(self, parent, person_tuple):
        # person_tuple: id_persona, dni, nombre, apellido, ..., estado
        super().__init__(parent, "Gestión de Baja de Postulante", width=520, height=360)
        self.person = person_tuple
        dni = person_tuple[1]
        nombre = f"{person_tuple[2]} {person_tuple[3]}"
        curso = person_tuple[13] if len(person_tuple) > 13 and person_tuple[13] else "Sin curso"
        comm = person_tuple[11] if len(person_tuple) > 11 and person_tuple[11] else "-"
        estado = "TITULAR ADMITIDO" if (len(person_tuple) > 14 and person_tuple[14] == 1) else "EN ESPERA"

        lbl_head = tk.Label(
            self.main_container,
            text="❌ Dar de Baja Postulante",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=COLOR_DANGER
        )
        lbl_head.pack(anchor="w", pady=(0, 10))

        info_frame = tk.Frame(self.main_container, bg=BG_CARD, padx=14, pady=12, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=(0, 12))

        info_text = (
            f"Postulante: {nombre} | DNI: {dni}\n"
            f"Curso: {curso} | Comisión: {comm}\n"
            f"Condición Actual: {estado}\n\n"
            f"ℹ Nota: Si el postulante es Titular Admitido, el primer inscripto de la\n"
            f"lista de espera de su comisión ocupará su vacante de forma automática."
        )
        tk.Label(info_frame, text=info_text, font=FONT_BODY, bg=BG_CARD, fg=TEXT_MAIN, justify="left").pack(anchor="w")

        # Botones de las dos modalidades de baja
        btn_frame = tk.Frame(self.main_container, bg=BG_MAIN)
        btn_frame.pack(fill="x", pady=(6, 0))

        ttk.Button(
            btn_frame,
            text="1. Cancelar solo Inscripción (Conserva Persona)",
            command=self.cancel_registration_only
        ).pack(fill="x", pady=(0, 6))

        ttk.Button(
            btn_frame,
            text="2. Eliminar completamente Persona y Registro",
            style="Danger.TButton",
            command=self.delete_person_completely
        ).pack(fill="x", pady=(0, 6))

        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="right", pady=(4, 0))

    def cancel_registration_only(self):
        dni = self.person[1]
        conf = messagebox.askyesno(
            "Confirmar Cancelación",
            f"¿Desea cancelar la inscripción activa del DNI {dni}?\nSe mantendrán sus datos personales en el padrón.",
            parent=self
        )
        if conf:
            ok, msg = operations.cancel_registration_by_dni(dni)
            if ok:
                messagebox.showinfo("Baja Exitosa", msg, parent=self)
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def delete_person_completely(self):
        dni = self.person[1]
        conf = messagebox.askyesno(
            "Confirmar Eliminación Total",
            f"¿Está seguro de eliminar COMPLETAMENTE a {self.person[2]} {self.person[3]} (DNI {dni}) del sistema?\nEsta acción es irreversible.",
            parent=self
        )
        if conf:
            ok, msg = operations.delete_person(self.person[0])
            if ok:
                messagebox.showinfo("Eliminación Exitosa", msg, parent=self)
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Error", msg, parent=self)


class WaitlistViewerDialog(BaseDialog):
    """Visualizador ordenado de la lista de espera para una comisión."""
    def __init__(self, parent, id_comision, codigo_comision, nombre_curso):
        super().__init__(parent, f"Lista de Espera - {codigo_comision}", width=640, height=450)
        self.waitlist = operations.get_waiting_list_by_commission(id_comision)

        lbl_head = tk.Label(
            self.main_container,
            text=f"📋 Lista de Espera: {codigo_comision} ({nombre_curso})",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=COLOR_PRIMARY
        )
        lbl_head.pack(anchor="w", pady=(0, 6))

        lbl_count = tk.Label(
            self.main_container,
            text=f"Total de postulantes en espera: {len(self.waitlist)} (Ordenados cronológicamente por fecha/hora de registro)",
            font=FONT_SMALL,
            bg=BG_MAIN,
            fg=TEXT_MUTED
        )
        lbl_count.pack(anchor="w", pady=(0, 10))

        # Tabla
        columns = ("pos", "dni", "nombre", "apellido", "fecha_hora")
        self.tree = ttk.Treeview(self.main_container, columns=columns, show="headings", height=12)

        self.tree.heading("pos", text="Orden")
        self.tree.heading("dni", text="DNI")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("fecha_hora", text="Fecha de Inscripción")

        self.tree.column("pos", width=60, anchor="center")
        self.tree.column("dni", width=100, anchor="center")
        self.tree.column("nombre", width=130)
        self.tree.column("apellido", width=130)
        self.tree.column("fecha_hora", width=170, anchor="center")

        scroll = ttk.Scrollbar(self.main_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Cargar datos
        for idx, row in enumerate(self.waitlist, start=1):
            # row: dni, nombre, apellido, com_codigo, fecha_hora, curso_nombre, id_insc
            self.tree.insert("", "end", values=(f"#{idx:02d}", row[0], row[1], row[2], row[4]))
