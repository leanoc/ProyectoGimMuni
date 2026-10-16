"""
Vista de Gestión de Personas e Inscripciones para Tkinter.
Gimnasio Municipal - Versión 3.0.0
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import operations
from gui.theme import (
    BG_MAIN, BG_CARD, TEXT_MAIN, TEXT_MUTED, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, FONT_TITLE,
    FONT_SECTION, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)
from gui.components.dialogs import (
    RegisterApplicantDialog, EditPersonDialog,
    ChangeCommissionDialog, DeregisterDialog
)

def calculate_age(birthdate_str):
    try:
        bdate = datetime.datetime.strptime(str(birthdate_str).strip(), "%Y-%m-%d").date()
        today = datetime.date.today()
        return today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
    except Exception:
        return "-"

class PersonsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.pack(fill="both", expand=True, padx=20, pady=15)

        self.persons_data = []
        self.create_header()
        self.create_toolbar()
        self.create_table()

    def create_header(self):
        head = tk.Frame(self, bg=BG_MAIN)
        head.pack(fill="x", pady=(0, 6))

        tk.Label(
            head,
            text="📝 Padrón de Personas e Inscripciones",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=TEXT_MAIN
        ).pack(side="left")

        lbl_desc = tk.Label(
            self,
            text="Altas con control previo de cupos, edición de datos personales, reasignación de comisiones y bajas con reemplazo automático.",
            font=FONT_SMALL,
            bg=BG_MAIN,
            fg=TEXT_MUTED
        )
        lbl_desc.pack(anchor="w", pady=(0, 12))

    def create_toolbar(self):
        bar = tk.Frame(self, bg=BG_CARD, padx=12, pady=10, relief="solid", bd=1)
        bar.pack(fill="x", pady=(0, 12))

        # Buscador
        tk.Label(bar, text="🔍 Buscar (DNI / Nombre / Apellido):", font=FONT_BODY_BOLD, bg=BG_CARD).pack(side="left", padx=(0, 6))
        self.ent_search = ttk.Entry(bar, width=25)
        self.ent_search.pack(side="left", padx=(0, 15))
        self.ent_search.bind("<KeyRelease>", self.filter_persons)

        # Botones de Acción
        ttk.Button(
            bar,
            text="➕ Inscribir Postulante",
            style="Primary.TButton",
            command=self.new_applicant
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            bar,
            text="✏️ Modificar Datos",
            command=self.edit_selected_person
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            bar,
            text="🔄 Cambiar Comisión",
            command=self.change_commission
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            bar,
            text="❌ Dar de Baja",
            style="Danger.TButton",
            command=self.deregister_person
        ).pack(side="left")

        ttk.Button(
            bar,
            text="🔄 Actualizar",
            command=self.refresh
        ).pack(side="right")

    def create_table(self):
        table_frame = tk.Frame(self, bg=BG_MAIN)
        table_frame.pack(fill="both", expand=True)

        cols = ("dni", "nombre_completo", "fecha_nac", "edad", "telefono", "email", "localidad", "curso", "comision", "condicion")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)

        self.tree.heading("dni", text="DNI")
        self.tree.heading("nombre_completo", text="Apellido y Nombre")
        self.tree.heading("fecha_nac", text="Fecha Nac.")
        self.tree.heading("edad", text="Edad")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("email", text="Email")
        self.tree.heading("localidad", text="Localidad")
        self.tree.heading("curso", text="Curso Asignado")
        self.tree.heading("comision", text="Comisión")
        self.tree.heading("condicion", text="Condición")

        self.tree.column("dni", width=95, anchor="center")
        self.tree.column("nombre_completo", width=180)
        self.tree.column("fecha_nac", width=100, anchor="center")
        self.tree.column("edad", width=65, anchor="center")
        self.tree.column("telefono", width=110, anchor="center")
        self.tree.column("email", width=160)
        self.tree.column("localidad", width=110)
        self.tree.column("curso", width=150)
        self.tree.column("comision", width=85, anchor="center")
        self.tree.column("condicion", width=120, anchor="center")

        self.tree.tag_configure("admitido", foreground=COLOR_SUCCESS)
        self.tree.tag_configure("espera", foreground=COLOR_WARNING)
        self.tree.tag_configure("sin_curso", foreground=TEXT_MUTED)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self.edit_selected_person())

    def refresh(self):
        """Carga y actualiza el listado completo de personas."""
        self.persons_data = operations.get_all_persons_with_enrollment()
        self.filter_persons()

    def filter_persons(self, event=None):
        query = self.ent_search.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in self.persons_data:
            # p: id_persona, dni, nombre, apellido, fecha_nac, direccion, localidad, telefono, email,
            #    id_inscripcion, id_comision, codigo_comision, id_curso, nombre_curso, estado, fecha_inscripcion
            pid, dni, nom, ape, fnac, dir_, loc, tel, em, i_id, c_id, c_cod, cur_id, cur_nom, est, f_insc = p
            full_name = f"{ape}, {nom}"

            if query:
                match = (query in dni.lower() or query in nom.lower() or query in ape.lower() or query in (cur_nom or "").lower())
                if not match:
                    continue

            edad = calculate_age(fnac)
            curso_txt = cur_nom if cur_nom else "Sin inscripción"
            comm_txt = c_cod if c_cod else "-"
            
            if est == 1:
                cond_txt = "ADMITIDO"
                tag = "admitido"
            elif est == 0:
                cond_txt = "EN ESPERA"
                tag = "espera"
            else:
                cond_txt = "SIN CURSO"
                tag = "sin_curso"

            self.tree.insert(
                "",
                "end",
                iid=str(pid),
                values=(
                    dni,
                    full_name,
                    fnac,
                    f"{edad} años" if isinstance(edad, int) else "-",
                    tel or "-",
                    em or "-",
                    loc or "-",
                    curso_txt,
                    comm_txt,
                    cond_txt
                ),
                tags=(tag,)
            )

    def get_selected_person(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selección requerida", "Por favor seleccione una persona de la tabla.", parent=self)
            return None
        pid = int(sel[0])
        matches = [p for p in self.persons_data if p[0] == pid]
        return matches[0] if matches else None

    def new_applicant(self):
        dlg = RegisterApplicantDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()

    def edit_selected_person(self):
        person = self.get_selected_person()
        if not person:
            return
        dlg = EditPersonDialog(self, person)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()

    def change_commission(self):
        person = self.get_selected_person()
        if not person:
            return

        # Verificar si tiene curso asignado
        if not person[11]:
            messagebox.showinfo("Sin Comisión", "La persona seleccionada no posee una comisión asignada actualmente.", parent=self)
            return

        dlg = ChangeCommissionDialog(self, person[1], f"{person[2]} {person[3]}", person[11])
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()

    def deregister_person(self):
        person = self.get_selected_person()
        if not person:
            return
        dlg = DeregisterDialog(self, person)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()
