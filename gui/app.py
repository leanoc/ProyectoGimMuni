"""
Ventana Principal y Controlador de la GUI en Tkinter.
Gimnasio Municipal - Versión 3.0.0
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import operations
from gui.theme import (
    setup_theme, center_window, BG_MAIN, BG_CARD, BG_SIDEBAR,
    BG_SIDEBAR_HOVER, BG_SIDEBAR_ACTIVE, SIDEBAR_ACCENT,
    TEXT_SIDEBAR, TEXT_SIDEBAR_MUTED, TEXT_MAIN, COLOR_PRIMARY, COLOR_SUCCESS,
    FONT_TITLE, FONT_SUBTITLE, FONT_SECTION, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL
)
from gui.views.dashboard_view import DashboardView
from gui.views.courses_view import CoursesView
from gui.views.commissions_view import CommissionsView
from gui.views.persons_view import PersonsView
from gui.views.selections_view import SelectionsView

class GymApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Inscripción y Sorteo - Gimnasio Municipal | Dev: L. M. OCARIZ ARRIETA")
        self.minsize(1050, 680)
        center_window(self, 1200, 740)

        # Aplicar tema ttk y paleta de colores
        setup_theme(self)

        # Variables de navegación
        self.current_view_name = None
        self.nav_buttons = {}

        # Contenedor principal dividido: Sidebar izquierda + Contenido derecha
        self.create_layout()

        # Instanciar vistas
        self.views = {
            "dashboard": DashboardView(self.content_area, self),
            "courses": CoursesView(self.content_area, self),
            "commissions": CommissionsView(self.content_area, self),
            "persons": PersonsView(self.content_area, self),
            "selections": SelectionsView(self.content_area, self),
        }

        # Iniciar en Dashboard
        self.show_view("dashboard")

    def create_layout(self):
        # 1. Sidebar (Panel de navegación lateral)
        self.sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / Marca institucional
        brand_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR, padx=16, pady=20)
        brand_frame.pack(fill="x")

        tk.Label(
            brand_frame,
            text="🏊‍♂️ 🏋️‍♀️",
            font=("Segoe UI", 22),
            bg=BG_SIDEBAR,
            fg="#FFFFFF"
        ).pack(anchor="w")

        tk.Label(
            brand_frame,
            text="GIMNASIO MUNICIPAL",
            font=("Segoe UI", 12, "bold"),
            bg=BG_SIDEBAR,
            fg="#FFFFFF"
        ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            brand_frame,
            text="Sistema de Inscripción & Sorteos",
            font=FONT_SMALL,
            bg=BG_SIDEBAR,
            fg=TEXT_SIDEBAR_MUTED
        ).pack(anchor="w")

        # Separador visual
        tk.Frame(self.sidebar, bg="#1E293B", height=1).pack(fill="x", padx=14, pady=10)

        # Menú de Botones de Navegación
        self.menu_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        self.menu_frame.pack(fill="x", pady=6)

        nav_items = [
            ("dashboard", "📊  Dashboard / Resumen"),
            ("courses", "📚  Cursos y Deportes"),
            ("commissions", "👥  Comisiones y Cupos"),
            ("persons", "📝  Personas e Inscripción"),
            ("selections", "🎲  Sorteos y Adjudicación"),
        ]

        for view_key, label_text in nav_items:
            btn_container = tk.Frame(self.menu_frame, bg=BG_SIDEBAR, cursor="hand2")
            btn_container.pack(fill="x", pady=2, padx=8)

            indicator = tk.Frame(btn_container, bg=BG_SIDEBAR, width=4)
            indicator.pack(side="left", fill="y")

            lbl = tk.Label(
                btn_container,
                text=label_text,
                font=FONT_BODY_BOLD,
                bg=BG_SIDEBAR,
                fg=TEXT_SIDEBAR,
                padx=10,
                pady=10,
                anchor="w"
            )
            lbl.pack(side="left", fill="x", expand=True)

            # Efectos de hover y click
            for widget in (btn_container, lbl):
                widget.bind("<Button-1>", lambda e, k=view_key: self.show_view(k))
                widget.bind("<Enter>", lambda e, c=btn_container, l=lbl, k=view_key: self.on_nav_hover(c, l, k, True))
                widget.bind("<Leave>", lambda e, c=btn_container, l=lbl, k=view_key: self.on_nav_hover(c, l, k, False))

            self.nav_buttons[view_key] = {
                "container": btn_container,
                "label": lbl,
                "indicator": indicator
            }

        # Footer de la Sidebar: Firma del desarrollador y versión
        footer_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR, padx=16, pady=18)
        footer_frame.pack(side="bottom", fill="x")

        tk.Frame(self.sidebar, bg="#1E293B", height=1).pack(side="bottom", fill="x", padx=14, pady=(0, 6))

        tk.Label(
            footer_frame,
            text="Desarrollado por:",
            font=FONT_SMALL,
            bg=BG_SIDEBAR,
            fg=TEXT_SIDEBAR_MUTED
        ).pack(anchor="w")

        tk.Label(
            footer_frame,
            text="L. M. OCARIZ ARRIETA",
            font=FONT_BODY_BOLD,
            bg=BG_SIDEBAR,
            fg="#38BDF8"
        ).pack(anchor="w", pady=(1, 4))

        tk.Label(
            footer_frame,
            text="Versión 3.0.0 (Tkinter GUI)",
            font=FONT_SMALL,
            bg=BG_SIDEBAR,
            fg=TEXT_SIDEBAR_MUTED
        ).pack(anchor="w")

        # 2. Contenedor de Contenido (Lado derecho)
        self.right_container = tk.Frame(self, bg=BG_MAIN)
        self.right_container.pack(side="right", fill="both", expand=True)

        # Header superior del contenido
        top_bar = tk.Frame(self.right_container, bg=BG_CARD, height=54, padx=20, relief="solid", bd=1)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        self.lbl_top_title = tk.Label(
            top_bar,
            text="Gimnasio Municipal",
            font=FONT_SUBTITLE,
            bg=BG_CARD,
            fg=TEXT_MAIN
        )
        self.lbl_top_title.pack(side="left", pady=12)

        # Badge de estado del sistema
        badge_frame = tk.Frame(top_bar, bg="#ECFDF5", padx=10, pady=4)
        badge_frame.pack(side="right", pady=12)
        tk.Label(
            badge_frame,
            text="● Sistema Operativo y Conectado",
            font=FONT_SMALL,
            bg="#ECFDF5",
            fg=COLOR_SUCCESS
        ).pack()

        # Área dinámica donde se muestran las vistas
        self.content_area = tk.Frame(self.right_container, bg=BG_MAIN)
        self.content_area.pack(fill="both", expand=True)

    def on_nav_hover(self, container, label, view_key, is_hover):
        if self.current_view_name == view_key:
            return  # No alterar el ítem activo
        if is_hover:
            container.config(bg=BG_SIDEBAR_HOVER)
            label.config(bg=BG_SIDEBAR_HOVER)
        else:
            container.config(bg=BG_SIDEBAR)
            label.config(bg=BG_SIDEBAR)

    def show_view(self, view_name):
        """Alterna dinámicamente entre las vistas disponibles."""
        if view_name not in self.views:
            return

        # Ocultar todas las vistas
        for v in self.views.values():
            v.pack_forget()

        # Actualizar estilos de los botones en la sidebar
        for k, widgets in self.nav_buttons.items():
            if k == view_name:
                widgets["container"].config(bg=BG_SIDEBAR_ACTIVE)
                widgets["label"].config(bg=BG_SIDEBAR_ACTIVE, fg="#FFFFFF")
                widgets["indicator"].config(bg=SIDEBAR_ACCENT)
            else:
                widgets["container"].config(bg=BG_SIDEBAR)
                widgets["label"].config(bg=BG_SIDEBAR, fg=TEXT_SIDEBAR)
                widgets["indicator"].config(bg=BG_SIDEBAR)

        # Mostrar la vista elegida y refrescar sus datos
        self.current_view_name = view_name
        active_view = self.views[view_name]
        active_view.pack(fill="both", expand=True)
        if hasattr(active_view, "refresh"):
            active_view.refresh()

        # Actualizar título superior
        titles = {
            "dashboard": "Dashboard / Resumen General",
            "courses": "Gestión y Oferta de Cursos",
            "commissions": "Comisiones, Cupos y Vacantes",
            "persons": "Padrón de Personas e Inscripciones",
            "selections": "Sorteos y Adjudicación de Cupos"
        }
        self.lbl_top_title.config(text=f"Gimnasio Municipal  ›  {titles.get(view_name, '')}")

    def refresh_all_views(self):
        """Actualiza la vista actual y el dashboard si fuera necesario."""
        if self.current_view_name in self.views:
            active_view = self.views[self.current_view_name]
            if hasattr(active_view, "refresh"):
                active_view.refresh()


def launch_app():
    """Inicializa la base de datos y arranca la interfaz gráfica."""
    database.create_tables()
    app = GymApp()
    app.mainloop()

if __name__ == "__main__":
    launch_app()
