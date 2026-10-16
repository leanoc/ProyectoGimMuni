"""
Módulo de Estilos y Paleta de Colores para la GUI de Tkinter.
Gimnasio Municipal - Versión 3.0.0
Desarrollado por: L. M. OCARIZ ARRIETA
"""

import tkinter as tk
from tkinter import ttk

# Paleta de Colores Moderna (Slate & Royal Blue)
BG_MAIN = "#F8FAFC"             # Fondo general gris muy claro
BG_CARD = "#FFFFFF"             # Fondo tarjetas y contenedores
BG_SIDEBAR = "#0F172A"          # Azul marino oscuro profundo
BG_SIDEBAR_HOVER = "#1E293B"    # Azul pizarra oscuro para hover
BG_SIDEBAR_ACTIVE = "#1E293B"   # Fondo ítem activo sidebar
SIDEBAR_ACCENT = "#38BDF8"      # Celeste cian para destacar ítem activo
TEXT_SIDEBAR = "#F8FAFC"        # Texto sidebar blanco suave
TEXT_SIDEBAR_MUTED = "#94A3B8"  # Texto secundario sidebar

COLOR_PRIMARY = "#2563EB"       # Azul principal
COLOR_PRIMARY_HOVER = "#1D4ED8" # Azul oscuro hover
COLOR_SUCCESS = "#059669"       # Verde esmeralda (admitidos / ok)
COLOR_SUCCESS_BG = "#ECFDF5"
COLOR_WARNING = "#D97706"       # Ámbar / naranja (en espera)
COLOR_WARNING_BG = "#FFFBEB"
COLOR_DANGER = "#DC2626"        # Rojo carmesí (bajas / errores)
COLOR_DANGER_BG = "#FEF2F2"
COLOR_INFO = "#0284C7"          # Azul información

TEXT_MAIN = "#0F172A"           # Texto primario
TEXT_MUTED = "#64748B"          # Texto atenuado / secundario
BORDER_COLOR = "#E2E8F0"        # Bordes suaves
BORDER_DARK = "#CBD5E1"

# Tipografías recomendadas en Windows / multiplataforma
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 12, "bold")
FONT_SECTION = (FONT_FAMILY, 11, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 9)
FONT_KPI_VAL = (FONT_FAMILY, 22, "bold")
FONT_KPI_LBL = (FONT_FAMILY, 9, "bold")

def center_window(window, width, height):
    """Centra una ventana respecto a la pantalla."""
    window.update_idletasks()
    x = max(0, (window.winfo_screenwidth() // 2) - (width // 2))
    y = max(0, (window.winfo_screenheight() // 2) - (height // 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

def setup_theme(root: tk.Tk):
    """Aplica configuraciones visuales globales y estilos ttk."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=BG_MAIN)

    # Configuración de frames
    style.configure("TFrame", background=BG_MAIN)
    style.configure("Card.TFrame", background=BG_CARD, relief="flat")
    style.configure("Sidebar.TFrame", background=BG_SIDEBAR)

    # Configuración de labels
    style.configure("TLabel", background=BG_MAIN, foreground=TEXT_MAIN, font=FONT_BODY)
    style.configure("Card.TLabel", background=BG_CARD, foreground=TEXT_MAIN, font=FONT_BODY)
    style.configure("CardTitle.TLabel", background=BG_CARD, foreground=TEXT_MAIN, font=FONT_SUBTITLE)
    style.configure("Muted.TLabel", background=BG_MAIN, foreground=TEXT_MUTED, font=FONT_SMALL)
    style.configure("CardMuted.TLabel", background=BG_CARD, foreground=TEXT_MUTED, font=FONT_SMALL)
    style.configure("Header.TLabel", background=BG_MAIN, foreground=TEXT_MAIN, font=FONT_TITLE)

    # Configuración de botones estándar
    style.configure(
        "TButton",
        font=FONT_BODY_BOLD,
        background="#E2E8F0",
        foreground=TEXT_MAIN,
        borderwidth=0,
        focusthickness=0,
        padding=(12, 6)
    )
    style.map(
        "TButton",
        background=[("active", "#CBD5E1"), ("pressed", "#94A3B8")]
    )

    # Botón Primario
    style.configure(
        "Primary.TButton",
        font=FONT_BODY_BOLD,
        background=COLOR_PRIMARY,
        foreground="#FFFFFF",
        borderwidth=0,
        padding=(12, 6)
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLOR_PRIMARY_HOVER), ("pressed", "#1E40AF")]
    )

    # Botón Éxito / Confirmación
    style.configure(
        "Success.TButton",
        font=FONT_BODY_BOLD,
        background=COLOR_SUCCESS,
        foreground="#FFFFFF",
        borderwidth=0,
        padding=(12, 6)
    )
    style.map(
        "Success.TButton",
        background=[("active", "#047857"), ("pressed", "#065F46")]
    )

    # Botón Peligro / Baja
    style.configure(
        "Danger.TButton",
        font=FONT_BODY_BOLD,
        background=COLOR_DANGER,
        foreground="#FFFFFF",
        borderwidth=0,
        padding=(12, 6)
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#B91C1C"), ("pressed", "#991B1B")]
    )

    # Configuración de Treeview (Tablas de datos)
    style.configure(
        "Treeview",
        background=BG_CARD,
        foreground=TEXT_MAIN,
        fieldbackground=BG_CARD,
        rowheight=28,
        font=FONT_BODY,
        borderwidth=1,
        relief="solid"
    )
    style.map(
        "Treeview",
        background=[("selected", "#DBEAFE")],
        foreground=[("selected", "#1E3A8A")]
    )
    style.configure(
        "Treeview.Heading",
        background="#F1F5F9",
        foreground="#334155",
        font=FONT_BODY_BOLD,
        relief="flat",
        padding=(6, 6)
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#E2E8F0")]
    )

    # Scrollbars modernas
    style.configure(
        "Vertical.TScrollbar",
        background="#CBD5E1",
        troughcolor=BG_MAIN,
        borderwidth=0,
        arrowsize=12
    )

    # Entries y Comboboxes
    style.configure("TEntry", fieldbackground="#FFFFFF", foreground=TEXT_MAIN, padding=5)
    style.configure("TCombobox", fieldbackground="#FFFFFF", foreground=TEXT_MAIN, padding=5)

    # Separator
    style.configure("TSeparator", background=BORDER_COLOR)
