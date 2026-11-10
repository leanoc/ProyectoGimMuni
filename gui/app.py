"""
Ventana Principal y Controlador de la GUI en Tkinter.
Gimnasio Municipal - Versión 3.1.0
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import tkinter as tk
import sqlite3
from datetime import datetime
from tkinter import filedialog, ttk, messagebox
import database
import operations
from config import APP_TITLE, APP_VERSION, APP_DEVELOPER
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
from gui.views.history_view import HistoryView
from gui.views.statistics_view import StatisticsView
from gui.components.dialogs import ExportCsvDialog

class GymApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Inscripción y Sorteo - Gimnasio Municipal | Dev: L. M. OCARIZ ARRIETA")
        window_width, window_height = center_window(self, 1200, 740)
        self.minsize(min(800, window_width), min(500, window_height))

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
            "history": HistoryView(self.content_area, self),
            "statistics": StatisticsView(self.content_area, self),
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
            text="  ",
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
            ("history", "🕘  Historial de Movimientos"),
            ("statistics", "📈  Estadísticas"),
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
            text=f"Versión {APP_VERSION} (Tkinter GUI)",
            font=FONT_SMALL,
            bg=BG_SIDEBAR,
            fg=TEXT_SIDEBAR_MUTED
        ).pack(anchor="w")
        ttk.Button(
            footer_frame,
            text="Acerca de...",
            command=self.show_about,
        ).pack(anchor="w", pady=(8, 0))

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

        ttk.Button(
            top_bar,
            text="Exportar CSV",
            command=self.open_export_dialog,
        ).pack(side="right", padx=(8, 0), pady=10)
        ttk.Button(
            top_bar,
            text="❔ Consultar",
            command=self.show_current_help,
        ).pack(side="right", padx=(8, 0), pady=10)
        ttk.Button(
            top_bar,
            text="Crear copia de seguridad",
            command=self.create_backup,
        ).pack(side="right", padx=(8, 0), pady=10)

        # Badge de estado del sistema
        badge_frame = tk.Frame(top_bar, bg="#ECFDF5", padx=10, pady=4)
        badge_frame.pack(side="right", pady=12)
        tk.Label(
            badge_frame,
            text="● Sistema activo",
            font=FONT_SMALL,
            bg="#ECFDF5",
            fg=COLOR_SUCCESS
        ).pack()

        # Área dinámica desplazable para pantallas de menor resolución.
        self.content_canvas = tk.Canvas(
            self.right_container,
            bg=BG_MAIN,
            highlightthickness=0
        )
        content_scroll = ttk.Scrollbar(
            self.right_container,
            orient="vertical",
            command=self.content_canvas.yview
        )
        content_scroll_x = ttk.Scrollbar(
            self.right_container,
            orient="horizontal",
            command=self.content_canvas.xview
        )
        self.content_canvas.configure(
            xscrollcommand=content_scroll_x.set,
            yscrollcommand=content_scroll.set
        )
        content_scroll.pack(side="right", fill="y")
        content_scroll_x.pack(side="bottom", fill="x")
        self.content_canvas.pack(side="left", fill="both", expand=True)

        self.content_area = tk.Frame(self.content_canvas, bg=BG_MAIN)
        self._content_window = self.content_canvas.create_window(
            (0, 0),
            window=self.content_area,
            anchor="nw"
        )
        self.content_area.bind("<Configure>", self._configure_content_area)
        self.content_canvas.bind("<Configure>", self._configure_content_area)

    def open_export_dialog(self) -> None:
        """Abre el selector de tablas y campos para exportación CSV."""
        ExportCsvDialog(self)

    def show_about(self) -> None:
        """Muestra los datos conocidos del proyecto y su contexto educativo."""
        messagebox.showinfo(
            "Acerca de...",
            (
                f"{APP_TITLE}\n"
                f"Versión {APP_VERSION}\n\n"
                "Proyecto grupal/de curso desarrollado en el marco del Curso de "
                "Programación dictado durante 2026 en el CFP N.º 402 de Berisso.\n\n"
                "Aplicación académica para gestionar cursos, inscripciones, "
                "comisiones y adjudicación de vacantes.\n\n"
                f"Desarrollo: {APP_DEVELOPER}"
            ),
            parent=self,
        )

    def _configure_content_area(self, event: tk.Event) -> None:
        content_width = max(event.width, self.content_area.winfo_reqwidth())
        self.content_canvas.itemconfigure(self._content_window, width=content_width)
        self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))

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
            "selections": "Sorteos y Adjudicación de Cupos",
            "history": "Historial de Movimientos",
            "statistics": "Estadísticas Principales",
        }
        self.lbl_top_title.config(text=f"Gimnasio Municipal  ›  {titles.get(view_name, '')}")

    def show_help(self, view_name: str) -> None:
        """Muestra instrucciones breves para la pantalla seleccionada."""
        instructions = {
            "dashboard": "Consulte los indicadores y la ocupación por comisión. Use Actualizar Datos para recargar.",
            "courses": "Busque cursos por nombre o criterio. Seleccione una fila para modificarla, eliminarla o consultar sus inscriptos; use Nuevo Curso para crear uno.",
            "commissions": "Busque por código o curso. Seleccione una comisión para cambiar cupos, eliminarla o revisar su lista de espera.",
            "persons": "Busque por DNI, nombre o apellido. Seleccione una persona para modificar sus datos, cambiarla de comisión o darla de baja.",
            "selections": "Ejecute sorteo para cursos con ese criterio o asignación FIFO para los de orden de llegada. Filtre los resultados por curso y estado.",
            "history": "Consulte los movimientos registrados automáticamente. Use Exportar CSV o Exportar PDF para guardar una copia del historial.",
            "statistics": "Consulte la ocupación porcentual por curso y los gráficos de ocupación y distribución por sexo. Las fichas anteriores sin ese dato se cuentan como Sin especificar.",
        }
        messagebox.showinfo(
            f"Consulta - {self.lbl_top_title.cget('text')}",
            instructions[view_name],
            parent=self,
        )

    def show_current_help(self) -> None:
        """Abre la consulta correspondiente a la vista activa."""
        if self.current_view_name is None:
            raise RuntimeError("No hay una vista activa para consultar.")
        self.show_help(self.current_view_name)

    def create_backup(self) -> None:
        """Guarda una copia consistente de la base de datos en la ruta elegida."""
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar copia de seguridad",
            defaultextension=".db",
            filetypes=[("Base de datos SQLite", "*.db"), ("Todos los archivos", "*.*")],
            initialfile=f"respaldo_gimnasio_{datetime.now():%Y%m%d_%H%M%S}.db",
        )
        if not path:
            return
        try:
            operations.backup_database(path)
        except (OSError, sqlite3.Error, ValueError) as error:
            messagebox.showerror("Error al crear la copia", str(error), parent=self)
            return
        messagebox.showinfo("Copia creada", f"La copia de seguridad se guardó en:\n{path}", parent=self)

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
