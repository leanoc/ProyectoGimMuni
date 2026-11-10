"""Vista del historial de movimientos y sus exportaciones."""

import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import operations
import reports
from gui.theme import (
    BG_CARD, BG_MAIN, FONT_BODY_BOLD, FONT_SMALL, FONT_TITLE,
    TEXT_MAIN, TEXT_MUTED,
)


class HistoryView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.pack(fill="both", expand=True, padx=20, pady=15)
        self.rows = []
        self.create_header()
        self.create_toolbar()
        self.create_table()

    def create_header(self):
        head = tk.Frame(self, bg=BG_MAIN)
        head.pack(fill="x", pady=(0, 6))
        tk.Label(
            head, text="🕘 Historial de Movimientos", font=FONT_TITLE,
            bg=BG_MAIN, fg=TEXT_MAIN,
        ).pack(side="left")
        tk.Label(
            self, text="Registro cronológico de cambios en cursos, comisiones, personas e inscripciones.",
            font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_MUTED,
        ).pack(anchor="w", pady=(0, 12))

    def create_toolbar(self):
        bar = tk.Frame(self, bg=BG_CARD, padx=12, pady=10, relief="solid", bd=1)
        bar.pack(fill="x", pady=(0, 12))
        ttk.Button(bar, text="📄 Exportar CSV", command=self.export_csv).pack(side="left", padx=(0, 6))
        ttk.Button(
            bar, text="📕 Exportar PDF", style="Primary.TButton",
            command=self.export_pdf,
        ).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="🔄 Actualizar", command=self.refresh).pack(side="right")
        self.count_label = tk.Label(bar, text="", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_MUTED)
        self.count_label.pack(side="right", padx=12)

    def create_table(self):
        container = tk.Frame(self, bg=BG_MAIN)
        container.pack(fill="both", expand=True)
        columns = ("fecha", "entidad", "accion", "detalle")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", height=16)
        for column, title, width in (
            ("fecha", "Fecha y hora", 160),
            ("entidad", "Sección", 130),
            ("accion", "Movimiento", 130),
            ("detalle", "Detalle", 550),
        ):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, stretch=column == "detalle")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh(self):
        self.rows = operations.get_movement_history()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, row in enumerate(self.rows):
            self.tree.insert("", "end", iid=str(index), values=row)
        self.count_label.config(text=f"{len(self.rows)} movimientos")

    def _export(self, extension, exporter):
        path = filedialog.asksaveasfilename(
            parent=self,
            title=f"Exportar historial a {extension.upper()}",
            defaultextension=f".{extension}",
            filetypes=[(f"Archivo {extension.upper()}", f"*.{extension}")],
            initialfile=f"historial_movimientos.{extension}",
        )
        if not path:
            return
        try:
            exporter(path, self.rows)
        except (OSError, sqlite3.Error, ValueError) as error:
            messagebox.showerror("Error de exportación", str(error), parent=self)
            return
        messagebox.showinfo("Exportación completada", f"Historial exportado a:\n{path}", parent=self)

    def export_csv(self):
        self._export("csv", reports.export_history_csv)

    def export_pdf(self):
        self._export("pdf", reports.export_history_pdf)
