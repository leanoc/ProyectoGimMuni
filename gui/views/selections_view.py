"""
Vista de Sorteos, Asignación de Cupos y Adjudicación para Tkinter.
Gimnasio Municipal - Versión 3.0.0
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import tkinter as tk
from tkinter import ttk, messagebox
import operations
from gui.theme import (
    BG_MAIN, BG_CARD, TEXT_MAIN, TEXT_MUTED, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, FONT_TITLE,
    FONT_SUBTITLE, FONT_SECTION, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)

class SelectionsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.pack(fill="both", expand=True, padx=20, pady=15)

        self.courses_data = []
        self.create_header()
        self.create_action_panels()
        self.create_results_inspector()

    def create_header(self):
        head = tk.Frame(self, bg=BG_MAIN)
        head.pack(fill="x", pady=(0, 6))

        tk.Label(
            head,
            text="🎲 Sorteo y Adjudicación de Cupos",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=TEXT_MAIN
        ).pack(side="left")

        lbl_desc = tk.Label(
            self,
            text="Adjudicación de titulares por sorteo aleatorio o por orden cronológico estricto (FIFO), y supervisión de listas de admitidos y en espera.",
            font=FONT_SMALL,
            bg=BG_MAIN,
            fg=TEXT_MUTED
        )
        lbl_desc.pack(anchor="w", pady=(0, 12))

    def create_action_panels(self):
        panels_container = tk.Frame(self, bg=BG_MAIN)
        panels_container.pack(fill="x", pady=(0, 15))

        # Panel 1: Sorteo Aleatorio
        card_lottery = tk.Frame(panels_container, bg=BG_CARD, padx=14, pady=12, relief="solid", bd=1)
        card_lottery.pack(side="left", fill="both", expand=True, padx=(0, 6))

        tk.Label(card_lottery, text="🎲 Sorteo Aleatorio Automatizado", font=FONT_SECTION, bg=BG_CARD, fg=COLOR_PRIMARY).pack(anchor="w", pady=(0, 4))
        tk.Label(
            card_lottery,
            text="Aplica para cursos con criterio 'Sorteo' (ej. Natación u otros).\n"
                 "Selecciona al azar entre los inscriptos en espera hasta cubrir las vacantes titulares.",
            font=FONT_SMALL,
            bg=BG_CARD,
            fg=TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        ttk.Button(
            card_lottery,
            text="Ejecutar Sorteo Aleatorio",
            style="Primary.TButton",
            command=self.run_lottery
        ).pack(anchor="w")

        # Panel 2: Orden de llegada (FIFO)
        card_fifo = tk.Frame(panels_container, bg=BG_CARD, padx=14, pady=12, relief="solid", bd=1)
        card_fifo.pack(side="right", fill="both", expand=True, padx=(6, 0))

        tk.Label(card_fifo, text="⏱️ Adjudicación por Orden de Llegada (FIFO)", font=FONT_SECTION, bg=BG_CARD, fg=COLOR_SUCCESS).pack(anchor="w", pady=(0, 4))
        tk.Label(
            card_fifo,
            text="Aplica para cursos con criterio 'Orden de llegada' (ej. Gimnasia Acuática).\n"
                 "Asigna a los primeros inscriptos por orden cronológico exacto hasta completar el cupo.",
            font=FONT_SMALL,
            bg=BG_CARD,
            fg=TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        ttk.Button(
            card_fifo,
            text="Ejecutar Asignación FIFO",
            style="Success.TButton",
            command=self.run_fifo
        ).pack(anchor="w")

    def create_results_inspector(self):
        f_insp = tk.LabelFrame(
            self,
            text=" Inspector de Resultados y Titulares por Curso ",
            font=FONT_SECTION,
            bg=BG_CARD,
            fg=TEXT_MAIN,
            padx=12,
            pady=10
        )
        f_insp.pack(fill="both", expand=True)

        # Barra de selección de curso y filtro de condición
        bar = tk.Frame(f_insp, bg=BG_CARD)
        bar.pack(fill="x", pady=(0, 10))

        tk.Label(bar, text="Curso a consultar:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(side="left", padx=(0, 6))
        self.cb_course = ttk.Combobox(bar, state="readonly", width=30)
        self.cb_course.pack(side="left", padx=(0, 15))
        self.cb_course.bind("<<ComboboxSelected>>", self.on_course_selected)

        tk.Label(bar, text="Filtrar por Condición:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(side="left", padx=(0, 6))
        self.cb_filter = ttk.Combobox(bar, values=["Todos", "Solo Titulares Admitidos", "Solo en Lista de Espera"], state="readonly", width=25)
        self.cb_filter.set("Todos")
        self.cb_filter.pack(side="left", padx=(0, 10))
        self.cb_filter.bind("<<ComboboxSelected>>", self.on_course_selected)

        self.lbl_stats = tk.Label(bar, text="", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MUTED)
        self.lbl_stats.pack(side="right")

        # Tabla de resultados
        cols = ("dni", "nombre", "apellido", "comision", "fecha_hora", "condicion")
        self.tree = ttk.Treeview(f_insp, columns=cols, show="headings", height=10)

        self.tree.heading("dni", text="DNI")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido", text="Apellido")
        self.tree.heading("comision", text="Comisión")
        self.tree.heading("fecha_hora", text="Fecha / Hora Inscripción")
        self.tree.heading("condicion", text="Estado de Adjudicación")

        self.tree.column("dni", width=100, anchor="center")
        self.tree.column("nombre", width=160)
        self.tree.column("apellido", width=160)
        self.tree.column("comision", width=100, anchor="center")
        self.tree.column("fecha_hora", width=180, anchor="center")
        self.tree.column("condicion", width=150, anchor="center")
        for column in cols:
            self.tree.column(column, stretch=False)

        self.tree.tag_configure("admitido", foreground=COLOR_SUCCESS)
        self.tree.tag_configure("espera", foreground=COLOR_WARNING)

        scroll = ttk.Scrollbar(f_insp, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(f_insp, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll.set, xscrollcommand=scroll_x.set)

        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def refresh(self):
        """Carga cursos disponibles para el inspector."""
        self.courses_data = operations.get_all_courses()
        self.course_map = {f"[{c[0]}] {c[1]} (Criterio: {c[2]})": c[0] for c in self.courses_data}

        current_val = self.cb_course.get()
        options = list(self.course_map.keys())
        self.cb_course.config(values=options)

        if options:
            if current_val in options:
                self.cb_course.set(current_val)
            else:
                self.cb_course.set(options[0])
            self.on_course_selected()
        else:
            self.cb_course.set("")
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.lbl_stats.config(text="No hay cursos creados")

    def on_course_selected(self, event=None):
        selected_label = self.cb_course.get()
        if not selected_label or selected_label not in self.course_map:
            return

        course_id = self.course_map[selected_label]
        records = operations.get_enrolled_by_course(course_id)
        # records: dni, nombre, apellido, com.codigo, i.fecha_hora, i.estado

        filter_mode = self.cb_filter.get()
        for item in self.tree.get_children():
            self.tree.delete(item)

        admitted_cnt = 0
        waiting_cnt = 0

        for r in records:
            dni, nom, ape, cod, f_hora, est = r
            if est == 1:
                admitted_cnt += 1
                cond_str = "TITULAR ADMITIDO"
                tag = "admitido"
            else:
                waiting_cnt += 1
                cond_str = "EN ESPERA"
                tag = "espera"

            if filter_mode == "Solo Titulares Admitidos" and est != 1:
                continue
            if filter_mode == "Solo en Lista de Espera" and est != 0:
                continue

            self.tree.insert(
                "",
                "end",
                values=(dni, nom, ape, cod, f_hora, cond_str),
                tags=(tag,)
            )

        self.lbl_stats.config(
            text=f"Total: {len(records)} | Titulares: {admitted_cnt} | En Espera: {waiting_cnt}"
        )

    def run_lottery(self):
        conf = messagebox.askyesno(
            "Confirmar Sorteo",
            "¿Desea ejecutar el proceso de sorteo aleatorio para todas las comisiones con criterio 'Sorteo'?\n\n"
            "Se seleccionarán postulantes de las listas de espera hasta cubrir las vacantes titulares.",
            parent=self
        )
        if not conf:
            return

        total_assigned, details = operations.run_lottery_assignment()
        self.controller.refresh_all_views()

        if total_assigned > 0:
            msg = f"Se asignaron exitosamente {total_assigned} nuevo(s) titular(es) por sorteo aleatorio:\n\n"
            msg += "\n".join(details)
            messagebox.showinfo("Sorteo Finalizado", msg, parent=self)
        else:
            messagebox.showinfo(
                "Sorteo Finalizado",
                "No había vacantes libres o postulantes en lista de espera pendientes de sorteo.",
                parent=self
            )

    def run_fifo(self):
        conf = messagebox.askyesno(
            "Confirmar Asignación FIFO",
            "¿Desea ejecutar la asignación por orden de llegada (FIFO) para todos los cursos con criterio 'Orden de llegada'?\n\n"
            "Se asignarán titulares a los primeros inscriptos por fecha y hora hasta agotar vacantes.",
            parent=self
        )
        if not conf:
            return

        total_assigned, details = operations.run_fifo_assignment()
        self.controller.refresh_all_views()

        if total_assigned > 0:
            msg = f"Se asignaron exitosamente {total_assigned} titular(es) por orden de llegada (FIFO):\n\n"
            msg += "\n".join(details)
            messagebox.showinfo("Asignación FIFO Finalizada", msg, parent=self)
        else:
            messagebox.showinfo(
                "Asignación FIFO Finalizada",
                "No había vacantes libres o postulantes en lista de espera para procesar.",
                parent=self
            )
