"""
Vista de Panel de Control (Dashboard) con Métricas y Accesos Rápidos.
Gimnasio Municipal - Versión 3.0.0
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import tkinter as tk
from tkinter import ttk
import operations
from gui.theme import (
    BG_MAIN, BG_CARD, TEXT_MAIN, TEXT_MUTED, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, FONT_TITLE,
    FONT_SUBTITLE, FONT_SECTION, FONT_BODY, FONT_BODY_BOLD,
    FONT_SMALL, FONT_KPI_VAL, FONT_KPI_LBL
)
from gui.components.dialogs import RegisterApplicantDialog, CourseDialog, CommissionDialog

class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller

        # Contenedor con scroll si fuera necesario, o layout elástico
        self.pack(fill="both", expand=True, padx=20, pady=15)

        self.create_header()
        self.create_kpi_cards()
        self.create_quick_actions()
        self.create_occupation_table()

    def create_header(self):
        head_frame = tk.Frame(self, bg=BG_MAIN)
        head_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            head_frame,
            text="📊 Panel de Control y Estadísticas en Tiempo Real",
            font=FONT_TITLE,
            bg=BG_MAIN,
            fg=TEXT_MAIN
        ).pack(side="left")

        ttk.Button(
            head_frame,
            text="🔄 Actualizar Datos",
            command=self.refresh
        ).pack(side="right")

    def create_kpi_cards(self):
        self.cards_frame = tk.Frame(self, bg=BG_MAIN)
        self.cards_frame.pack(fill="x", pady=(0, 15))

        # Crear 5 tarjetas métricas
        self.kpi_labels = {}
        metrics = [
            ("cursos", "CURSOS ACTIVOS", COLOR_PRIMARY, "📚"),
            ("comisiones", "COMISIONES", "#4F46E5", "👥"),
            ("inscriptos", "INSCRIPTOS TOTALES", "#0891B2", "📋"),
            ("admitidos", "TITULARES ADMITIDOS", COLOR_SUCCESS, "✅"),
            ("en_espera", "EN LISTA DE ESPERA", COLOR_WARNING, "⏳")
        ]

        for i, (key, title, color, icon) in enumerate(metrics):
            card = tk.Frame(
                self.cards_frame,
                bg=BG_CARD,
                padx=14,
                pady=12,
                relief="solid",
                bd=1
            )
            card.pack(side="left", fill="x", expand=True, padx=4 if i > 0 else (0, 4))

            # Header tarjeta
            h_card = tk.Frame(card, bg=BG_CARD)
            h_card.pack(fill="x")
            tk.Label(h_card, text=icon, font=FONT_SUBTITLE, bg=BG_CARD).pack(side="left")
            tk.Label(
                h_card,
                text=f" {title}",
                font=FONT_KPI_LBL,
                bg=BG_CARD,
                fg=TEXT_MUTED
            ).pack(side="left")

            # Valor numérico
            lbl_val = tk.Label(card, text="0", font=FONT_KPI_VAL, bg=BG_CARD, fg=color)
            lbl_val.pack(anchor="w", pady=(4, 0))
            self.kpi_labels[key] = lbl_val

    def create_quick_actions(self):
        act_frame = tk.LabelFrame(
            self,
            text=" Accesos Rápidos y Operaciones Frecuentes ",
            font=FONT_SECTION,
            bg=BG_CARD,
            fg=TEXT_MAIN,
            padx=14,
            pady=10
        )
        act_frame.pack(fill="x", pady=(0, 15))

        btn_row = tk.Frame(act_frame, bg=BG_CARD)
        btn_row.pack(fill="x")

        ttk.Button(
            btn_row,
            text="➕ Inscribir Postulante",
            style="Primary.TButton",
            command=self.open_registration
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_row,
            text="📚 Nuevo Curso",
            command=self.open_new_course
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_row,
            text="👥 Nueva Comisión",
            command=self.open_new_commission
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_row,
            text="🎲 Ir a Sorteos y Asignación",
            command=lambda: self.controller.show_view("selections")
        ).pack(side="left")

    def create_occupation_table(self):
        occ_frame = tk.LabelFrame(
            self,
            text=" Estado de Ocupación por Comisión en Tiempo Real ",
            font=FONT_SECTION,
            bg=BG_CARD,
            fg=TEXT_MAIN,
            padx=12,
            pady=10
        )
        occ_frame.pack(fill="both", expand=True)

        cols = ("codigo", "curso", "criterio", "inscriptos", "admitidos", "espera", "libres", "estado")
        self.tree = ttk.Treeview(occ_frame, columns=cols, show="headings", height=8)

        self.tree.heading("codigo", text="Código")
        self.tree.heading("curso", text="Curso")
        self.tree.heading("criterio", text="Criterio")
        self.tree.heading("inscriptos", text="Ocupación Total")
        self.tree.heading("admitidos", text="Titulares Admitidos")
        self.tree.heading("espera", text="En Espera")
        self.tree.heading("libres", text="Vacantes Libres")
        self.tree.heading("estado", text="Disponibilidad")

        self.tree.column("codigo", width=80, anchor="center")
        self.tree.column("curso", width=180)
        self.tree.column("criterio", width=120, anchor="center")
        self.tree.column("inscriptos", width=120, anchor="center")
        self.tree.column("admitidos", width=130, anchor="center")
        self.tree.column("espera", width=90, anchor="center")
        self.tree.column("libres", width=100, anchor="center")
        self.tree.column("estado", width=120, anchor="center")
        for column in cols:
            self.tree.column(column, stretch=False)

        self.tree.tag_configure("disponible", foreground=COLOR_SUCCESS)
        self.tree.tag_configure("completo", foreground=COLOR_DANGER)

        scroll = ttk.Scrollbar(occ_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(occ_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll.set, xscrollcommand=scroll_x.set)

        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def refresh(self):
        """Recarga estadísticas y la tabla de comisiones."""
        # 1. Cargar KPI
        stats = operations.get_dashboard_stats()
        for k, lbl in self.kpi_labels.items():
            if k in stats:
                lbl.config(text=str(stats[k]))

        # 2. Cargar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        commissions = operations.get_all_commissions()
        for c in commissions:
            # c: id, codigo, cupo_total, cupo_seleccion, nombre_curso, criterio, inscriptos, admitidos, en_espera
            libres = c[2] - c[6]
            tag = "disponible" if libres > 0 else "completo"
            estado_txt = f"✓ Disponible ({libres})" if libres > 0 else "✕ Completo"
            
            self.tree.insert(
                "",
                "end",
                values=(
                    c[1],
                    c[4],
                    c[5],
                    f"{c[6]} / {c[2]}",
                    f"{c[7]} / {c[3]}",
                    str(c[8]),
                    str(libres),
                    estado_txt
                ),
                tags=(tag,)
            )

    def open_registration(self):
        dlg = RegisterApplicantDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()

    def open_new_course(self):
        dlg = CourseDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()

    def open_new_commission(self):
        dlg = CommissionDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.controller.refresh_all_views()
