"""Vista de indicadores y estadísticas por curso."""

import math
import tkinter as tk
from tkinter import ttk

import operations
from gui.theme import (
    BG_CARD, BG_MAIN, COLOR_DANGER, COLOR_INFO, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_WARNING, FONT_BODY, FONT_KPI_LBL,
    FONT_KPI_VAL, FONT_TITLE,
    TEXT_MAIN, TEXT_MUTED,
)


class StatisticsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.pack(fill="both", expand=True, padx=20, pady=15)
        self.create_header()
        self.create_summary()
        self.create_charts()
        self.create_course_table()

    def create_header(self):
        head = tk.Frame(self, bg=BG_MAIN)
        head.pack(fill="x", pady=(0, 12))
        tk.Label(head, text="📈 Estadísticas Principales", font=FONT_TITLE, bg=BG_MAIN, fg=TEXT_MAIN).pack(side="left")
        ttk.Button(head, text="🔄 Actualizar", command=self.refresh).pack(side="right", padx=8)

    def create_summary(self):
        self.summary_frame = tk.Frame(self, bg=BG_MAIN)
        self.summary_frame.pack(fill="x", pady=(0, 8))
        for column in range(3):
            self.summary_frame.columnconfigure(column, weight=1)
        self.summary_labels = {}
        for index, (key, title, color) in enumerate((
            ("cursos", "CURSOS", COLOR_PRIMARY),
            ("comisiones", "COMISIONES", COLOR_PRIMARY),
            ("inscriptos", "INSCRIPTOS", COLOR_PRIMARY),
            ("admitidos", "TITULARES", COLOR_SUCCESS),
            ("en_espera", "EN ESPERA", COLOR_WARNING),
        )):
            card = tk.Frame(self.summary_frame, bg=BG_CARD, padx=12, pady=8, relief="solid", bd=1)
            card.grid(row=index // 3, column=index % 3, sticky="ew", padx=(0, 6), pady=(0, 4))
            tk.Label(card, text=title, font=FONT_KPI_LBL, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
            value = tk.Label(card, text="0", font=FONT_KPI_VAL, bg=BG_CARD, fg=color)
            value.pack(anchor="w", pady=(4, 0))
            self.summary_labels[key] = value

    def create_course_table(self):
        section = tk.LabelFrame(
            self, text=" Ocupación por curso ", font=FONT_BODY,
            bg=BG_CARD, fg=TEXT_MAIN, padx=12, pady=10,
        )
        section.pack(fill="x", expand=True)
        columns = ("curso", "comisiones", "inscriptos", "capacidad", "ocupacion", "admitidos", "espera")
        self.tree = ttk.Treeview(section, columns=columns, show="headings", height=6)
        for column, title, width in (
            ("curso", "Curso", 170),
            ("comisiones", "Comisiones", 85),
            ("inscriptos", "Inscriptos", 85),
            ("capacidad", "Cupo disponible", 110),
            ("ocupacion", "Ocupación", 100),
            ("admitidos", "Titulares", 85),
            ("espera", "En espera", 85),
        ):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, anchor="w" if column == "curso" else "center")
        self.tree.pack(fill="both", expand=True)

    def create_charts(self):
        charts = tk.Frame(self, bg=BG_MAIN)
        charts.pack(fill="x", pady=(0, 8))

        course_card = tk.LabelFrame(
            charts, text=" Ocupación de cupos ", font=FONT_BODY,
            bg=BG_CARD, fg=TEXT_MAIN, padx=8, pady=6,
        )
        course_card.pack(side="left", fill="both", expand=True, padx=(0, 6))
        gender_card = tk.LabelFrame(
            charts, text=" Distribución de inscriptos por sexo ", font=FONT_BODY,
            bg=BG_CARD, fg=TEXT_MAIN, padx=8, pady=6,
        )
        gender_card.pack(side="left", fill="both", expand=True, padx=(6, 0))

        self.occupancy_chart = tk.Canvas(
            course_card, width=440, height=165, bg=BG_CARD,
            highlightthickness=0,
        )
        self.occupancy_chart.pack(fill="both", expand=True)
        self.gender_chart = tk.Canvas(
            gender_card, width=440, height=165, bg=BG_CARD,
            highlightthickness=0,
        )
        self.gender_chart.pack(fill="both", expand=True)

    @staticmethod
    def draw_pie(canvas, entries, total, denominator_label):
        canvas.delete("all")
        if total <= 0:
            canvas.create_text(
                220, 82, text="Sin datos para mostrar",
                fill=TEXT_MUTED, font=FONT_BODY,
            )
            return

        center_x, center_y, radius = 96, 80, 68
        start = 90
        legend_y = 32
        palette = (COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_INFO)
        for index, (label, count) in enumerate(entries):
            if count <= 0:
                continue
            extent = count * 360 / total
            color = palette[index % len(palette)]
            canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start, extent=extent, fill=color,
                outline=BG_CARD, width=2, style=tk.PIESLICE,
            )
            if extent >= 18:
                midpoint = math.radians(start + extent / 2)
                label_x = center_x + math.cos(midpoint) * radius * 0.62
                label_y = center_y - math.sin(midpoint) * radius * 0.62
                canvas.create_text(
                    label_x, label_y,
                    text=f"{count * 100 / total:.0f}%",
                    fill="#FFFFFF", font=("Segoe UI", 9, "bold"),
                )
            percent = count * 100 / total
            canvas.create_rectangle(
                190, legend_y - 6, 202, legend_y + 6,
                fill=color, outline=color,
            )
            canvas.create_text(
                210, legend_y, anchor="w",
                text=f"{label}: {count} ({percent:.1f}%)",
                fill=TEXT_MAIN, font=FONT_BODY,
            )
            legend_y += 27
            start += extent
        canvas.create_text(
            190, 145, anchor="w", text=denominator_label,
            fill=TEXT_MUTED, font=("Segoe UI", 8),
        )

    def refresh(self):
        summary = operations.get_dashboard_stats()
        for key, label in self.summary_labels.items():
            label.config(text=str(summary[key]))

        for item in self.tree.get_children():
            self.tree.delete(item)
        occupied = 0
        capacity_total = 0
        for row in operations.get_course_statistics():
            name, enrolled, admitted, waiting, commissions, seats, course_limit, commission_limit = row
            admitted = admitted or 0
            enrolled = enrolled or 0
            capacities = [value for value in (course_limit, commission_limit) if value and value > 0]
            capacity = min(capacities) if capacities else 0
            occupancy = min(enrolled, capacity) if capacity else 0
            percentage = occupancy * 100 / capacity if capacity else 0
            occupied += occupancy
            capacity_total += capacity
            self.tree.insert(
                "", "end",
                values=(
                    name, commissions, enrolled,
                    capacity if capacity else "Sin cupo",
                    f"{percentage:.1f}%" if capacity else "N/D",
                    admitted, waiting or 0,
                ),
            )

        available = max(0, capacity_total - occupied)
        self.draw_pie(
            self.occupancy_chart,
            (("Ocupados", occupied), ("Disponibles", available)),
            capacity_total,
            f"Ocupación total: {occupied * 100 / capacity_total:.1f}%"
            if capacity_total else "No hay cupos configurados",
        )

        gender_counts = operations.get_gender_statistics()
        gender_total = sum(count for _, count in gender_counts)
        self.draw_pie(
            self.gender_chart,
            gender_counts,
            gender_total,
            f"Total de personas: {gender_total}",
        )
