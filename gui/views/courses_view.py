"""
Vista de Gestión de Cursos (CRUD) para la GUI de Tkinter.
Gimnasio Municipal - Versión 3.0.0
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import tkinter as tk
from tkinter import ttk, messagebox
import operations
from gui.theme import (
    BG_MAIN, BG_CARD, TEXT_MAIN, TEXT_MUTED, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_DANGER, FONT_TITLE, FONT_SUBTITLE,
    FONT_SECTION, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)
from gui.components.dialogs import CourseDialog, BaseDialog

class CourseEnrolledModal(BaseDialog):
    """Muestra los inscriptos de un curso específico."""
    def __init__(self, parent, course_id, course_name):
        super().__init__(parent, f"Inscriptos: {course_name}", width=700, height=450)
        
        lbl_head = tk.Label(
            self.main_container,
            text=f"👥 Inscriptos en {course_name}",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=COLOR_PRIMARY
        )
        lbl_head.pack(anchor="w", pady=(0, 10))

        records = operations.get_enrolled_by_course(course_id)
        
        lbl_info = tk.Label(
            self.main_container,
            text=f"Total de registros: {len(records)}",
            font=FONT_BODY_BOLD,
            bg=BG_MAIN,
            fg=TEXT_MUTED
        )
        lbl_info.pack(anchor="w", pady=(0, 8))

        cols = ("dni", "nombre", "apellido", "comision", "fecha", "estado")
        tree = ttk.Treeview(self.main_container, columns=cols, show="headings", height=12)
        tree.heading("dni", text="DNI")
        tree.heading("nombre", text="Nombre")
        tree.heading("apellido", text="Apellido")
        tree.heading("comision", text="Comisión")
        tree.heading("fecha", text="Fecha Inscripción")
        tree.heading("estado", text="Condición")

        tree.column("dni", width=100, anchor="center")
        tree.column("nombre", width=130)
        tree.column("apellido", width=130)
        tree.column("comision", width=90, anchor="center")
        tree.column("fecha", width=140, anchor="center")
        tree.column("estado", width=110, anchor="center")

        tree.tag_configure("admitido", foreground=COLOR_SUCCESS)
        tree.tag_configure("espera", foreground="#D97706")

        scroll = ttk.Scrollbar(self.main_container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)

        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for r in records:
            # r: dni, nombre, apellido, codigo, fecha_hora, estado
            est_txt = "ADMITIDO" if r[5] == 1 else "EN ESPERA"
            tag = "admitido" if r[5] == 1 else "espera"
            tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], est_txt), tags=(tag,))


class CoursesView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.pack(fill="both", expand=True, padx=20, pady=15)

        self.courses_data = []
        self.create_header()
        self.create_toolbar()
        self.create_table()

    def create_header(self):
        head = tk.Frame(self, bg=BG_MAIN)
        head.pack(fill="x", pady=(0, 10))

        tk.Label(
            head,
            text="📚 Gestión de Cursos y Oferta Deportiva",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=TEXT_MAIN
        ).pack(side="left")

        lbl_desc = tk.Label(
            self,
            text="Administración de actividades, criterios de adjudicación (Sorteo / Orden de llegada), edad mínima y cupos máximos.",
            font=FONT_SMALL,
            bg=BG_MAIN,
            fg=TEXT_MUTED
        )
        lbl_desc.pack(anchor="w", pady=(0, 12))

    def create_toolbar(self):
        bar = tk.Frame(self, bg=BG_CARD, padx=12, pady=10, relief="solid", bd=1)
        bar.pack(fill="x", pady=(0, 12))

        # Buscador
        tk.Label(bar, text="🔍 Buscar curso:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(side="left", padx=(0, 6))
        self.ent_search = ttk.Entry(bar, width=22)
        self.ent_search.pack(side="left", padx=(0, 15))
        self.ent_search.bind("<KeyRelease>", self.filter_courses)

        # Botones de Acción
        ttk.Button(
            bar,
            text="➕ Nuevo Curso",
            style="Primary.TButton",
            command=self.new_course
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            bar,
            text="✏️ Modificar",
            command=self.edit_selected_course
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            bar,
            text="🗑️ Eliminar",
            style="Danger.TButton",
            command=self.delete_selected_course
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            bar,
            text="👥 Ver Inscriptos",
            command=self.view_enrolled
        ).pack(side="left")

        ttk.Button(
            bar,
            text="🔄 Actualizar",
            command=self.refresh
        ).pack(side="right")

    def create_table(self):
        table_frame = tk.Frame(self, bg=BG_MAIN)
        table_frame.pack(fill="both", expand=True)

        cols = ("id", "nombre", "criterio", "edad_minima", "cupo_maximo", "inscriptos")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre del Curso / Deporte")
        self.tree.heading("criterio", text="Criterio de Selección")
        self.tree.heading("edad_minima", text="Edad Mínima Requerida")
        self.tree.heading("cupo_maximo", text="Cupo Máximo Global")
        self.tree.heading("inscriptos", text="Total Inscriptos")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nombre", width=240)
        self.tree.column("criterio", width=160, anchor="center")
        self.tree.column("edad_minima", width=150, anchor="center")
        self.tree.column("cupo_maximo", width=150, anchor="center")
        self.tree.column("inscriptos", width=120, anchor="center")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self.edit_selected_course())

    def refresh(self):
        """Carga y actualiza los cursos de la base de datos."""
        self.courses_data = operations.get_all_courses()
        self.filter_courses()

    def filter_courses(self, event=None):
        query = self.ent_search.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for c in self.courses_data:
            # c: id_curso, nombre, criterio, edad_minima, cupo_maximo
            cid, nom, crit, edad, cupo = c
            if query and query not in nom.lower() and query not in crit.lower():
                continue

            # Obtener inscriptos totales del curso
            enrolled = operations.get_enrolled_by_course(cid)
            self.tree.insert(
                "",
                "end",
                iid=str(cid),
                values=(
                    str(cid),
                    nom,
                    crit,
                    f"{edad} años" if edad else "Sin límite",
                    str(cupo) if cupo else "Ilimitado",
                    str(len(enrolled))
                )
            )

    def get_selected_course(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selección requerida", "Por favor seleccione un curso de la tabla.", parent=self)
            return None
        course_id = int(sel[0])
        course_match = [c for c in self.courses_data if c[0] == course_id]
        return course_match[0] if course_match else None

    def new_course(self):
        dlg = CourseDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()

    def edit_selected_course(self):
        course = self.get_selected_course()
        if not course:
            return
        dlg = CourseDialog(self, course_data=course)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()

    def delete_selected_course(self):
        course = self.get_selected_course()
        if not course:
            return

        conf = messagebox.askyesno(
            "Confirmar Eliminación",
            f"ADVERTENCIA: ¿Está seguro de eliminar el curso '{course[1]}'?\n\n"
            f"Esta acción eliminará EN CASCADA todas las comisiones e inscripciones vinculadas a este curso.",
            icon="warning",
            parent=self
        )
        if conf:
            ok, msg = operations.delete_course(course[0])
            if ok:
                messagebox.showinfo("Éxito", msg, parent=self)
                self.controller.refresh_all_views()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def view_enrolled(self):
        course = self.get_selected_course()
        if not course:
            return
        CourseEnrolledModal(self, course[0], course[1])
