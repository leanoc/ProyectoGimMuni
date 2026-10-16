"""
Vista de Gestión de Comisiones (CRUD, cupos y listas de espera) para Tkinter.
Gimnasio Municipal - Versión 3.0.0
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import tkinter as tk
from tkinter import ttk, messagebox
import operations
from gui.theme import (
    BG_MAIN, BG_CARD, TEXT_MAIN, TEXT_MUTED, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, FONT_TITLE,
    FONT_SECTION, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)
from gui.components.dialogs import CommissionDialog, WaitlistViewerDialog

class CommissionsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.pack(fill="both", expand=True, padx=20, pady=15)

        self.commissions_data = []
        self.create_header()
        self.create_toolbar()
        self.create_table()

    def create_header(self):
        head = tk.Frame(self, bg=BG_MAIN)
        head.pack(fill="x", pady=(0, 6))

        tk.Label(
            head,
            text="👥 Comisiones, Cupos y Vacantes",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=TEXT_MAIN
        ).pack(side="left")

        lbl_desc = tk.Label(
            self,
            text="Control de límites máximos, cupos de selección (titulares), inscriptos y consulta cronológica de lista de espera.",
            font=FONT_SMALL,
            bg=BG_MAIN,
            fg=TEXT_MUTED
        )
        lbl_desc.pack(anchor="w", pady=(0, 12))

    def create_toolbar(self):
        bar = tk.Frame(self, bg=BG_CARD, padx=12, pady=10, relief="solid", bd=1)
        bar.pack(fill="x", pady=(0, 12))

        # Buscador
        tk.Label(bar, text="🔍 Buscar comisión/curso:", font=FONT_BODY_BOLD, bg=BG_CARD).pack(side="left", padx=(0, 6))
        self.ent_search = ttk.Entry(bar, width=22)
        self.ent_search.pack(side="left", padx=(0, 15))
        self.ent_search.bind("<KeyRelease>", self.filter_commissions)

        # Botones de Acción
        ttk.Button(
            bar,
            text="➕ Nueva Comisión",
            style="Primary.TButton",
            command=self.new_commission
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            bar,
            text="✏️ Modificar Cupos",
            command=self.edit_selected_commission
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            bar,
            text="🗑️ Eliminar Comisión",
            style="Danger.TButton",
            command=self.delete_selected_commission
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            bar,
            text="📋 Ver Lista de Espera",
            command=self.view_waitlist
        ).pack(side="left")

        ttk.Button(
            bar,
            text="🔄 Actualizar",
            command=self.refresh
        ).pack(side="right")

    def create_table(self):
        table_frame = tk.Frame(self, bg=BG_MAIN)
        table_frame.pack(fill="both", expand=True)

        cols = ("id", "codigo", "curso", "criterio", "cupo_total", "cupo_seleccion", "inscriptos", "admitidos", "espera", "libres", "estado")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)

        self.tree.heading("id", text="ID")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("curso", text="Curso Asociado")
        self.tree.heading("criterio", text="Criterio")
        self.tree.heading("cupo_total", text="Cupo Total")
        self.tree.heading("cupo_seleccion", text="Cupo Selección")
        self.tree.heading("inscriptos", text="Ocupación Total")
        self.tree.heading("admitidos", text="Titulares")
        self.tree.heading("espera", text="En Espera")
        self.tree.heading("libres", text="Vacantes Libres")
        self.tree.heading("estado", text="Disponibilidad")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("codigo", width=80, anchor="center")
        self.tree.column("curso", width=180)
        self.tree.column("criterio", width=120, anchor="center")
        self.tree.column("cupo_total", width=90, anchor="center")
        self.tree.column("cupo_seleccion", width=110, anchor="center")
        self.tree.column("inscriptos", width=110, anchor="center")
        self.tree.column("admitidos", width=90, anchor="center")
        self.tree.column("espera", width=90, anchor="center")
        self.tree.column("libres", width=100, anchor="center")
        self.tree.column("estado", width=120, anchor="center")

        self.tree.tag_configure("disponible", foreground=COLOR_SUCCESS)
        self.tree.tag_configure("completo", foreground=COLOR_DANGER)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self.edit_selected_commission())

    def refresh(self):
        """Carga y actualiza los datos de comisiones."""
        self.commissions_data = operations.get_all_commissions()
        self.filter_commissions()

    def filter_commissions(self, event=None):
        query = self.ent_search.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for c in self.commissions_data:
            # c: id, codigo, cupo_total, cupo_seleccion, nombre_curso, criterio, inscriptos, admitidos, en_espera, id_curso
            cid, cod, c_tot, c_sel, nom_c, crit, insc, adm, esp = c[:9]
            if query and query not in cod.lower() and query not in nom_c.lower():
                continue

            libres = c_tot - insc
            tag = "disponible" if libres > 0 else "completo"
            estado_txt = f"✓ Disponible ({libres})" if libres > 0 else "✕ Completo"

            self.tree.insert(
                "",
                "end",
                iid=str(cid),
                values=(
                    str(cid),
                    cod,
                    nom_c,
                    crit,
                    str(c_tot),
                    str(c_sel),
                    f"{insc} / {c_tot}",
                    f"{adm} / {c_sel}",
                    str(esp),
                    str(libres),
                    estado_txt
                ),
                tags=(tag,)
            )

    def get_selected_commission(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selección requerida", "Por favor seleccione una comisión de la tabla.", parent=self)
            return None
        comm_id = int(sel[0])
        matches = [c for c in self.commissions_data if c[0] == comm_id]
        return matches[0] if matches else None

    def new_commission(self):
        dlg = CommissionDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()

    def edit_selected_commission(self):
        comm = self.get_selected_commission()
        if not comm:
            return
        dlg = CommissionDialog(self, comm_data=comm)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()

    def delete_selected_commission(self):
        comm = self.get_selected_commission()
        if not comm:
            return

        conf = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la comisión '{comm[1]}' ({comm[4]})?\n\n"
            f"Esta acción cancelará las inscripciones activas vinculadas a esta comisión.",
            icon="warning",
            parent=self
        )
        if conf:
            ok, msg = operations.delete_commission(comm[0])
            if ok:
                messagebox.showinfo("Éxito", msg, parent=self)
                self.controller.refresh_all_views()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def view_waitlist(self):
        comm = self.get_selected_commission()
        if not comm:
            return
        WaitlistViewerDialog(self, comm[0], comm[1], comm[4])
