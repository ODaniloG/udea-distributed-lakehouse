from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, ConnectionPatch

DOCS = Path("docs")
DOCS.mkdir(parents=True, exist_ok=True)


# =========================================================
# DIAGRAMA ARQUITECTURA SIMPLE
# =========================================================

def generar_arquitectura():
    fig, ax = plt.subplots(figsize=(18, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.95,
        "Arquitectura Mini-Lakehouse UdeA",
        ha="center",
        va="top",
        fontsize=22,
        fontweight="bold",
        color="#0F172A"
    )

    ax.text(
        0.5,
        0.90,
        "Pipeline analítico local basado en zonas Bronze, Silver y Gold con Parquet y DuckDB",
        ha="center",
        va="top",
        fontsize=11,
        color="#475569"
    )

    etapas = [
        {
            "titulo": "Fuentes OLTP",
            "sub": "CockroachDB / MongoDB",
            "detalle": "Inscripciones, cursos,\nestudiantes y sedes",
            "color": "#DBEAFE",
            "borde": "#2563EB",
            "x": 0.05,
            "y": 0.55,
        },
        {
            "titulo": "Extract",
            "sub": "generate_data.py",
            "detalle": "Carga inicial y simulación\nde datos operacionales",
            "color": "#E0F2FE",
            "borde": "#0284C7",
            "x": 0.20,
            "y": 0.55,
        },
        {
            "titulo": "Bronze",
            "sub": "RAW Parquet",
            "detalle": "Datos crudos\nsin transformación",
            "color": "#FED7AA",
            "borde": "#EA580C",
            "x": 0.35,
            "y": 0.55,
        },
        {
            "titulo": "Silver",
            "sub": "Clean + Validated",
            "detalle": "Tipificación, nulos,\nduplicados y calidad",
            "color": "#E5E7EB",
            "borde": "#64748B",
            "x": 0.50,
            "y": 0.55,
        },
        {
            "titulo": "Gold",
            "sub": "Star Schema",
            "detalle": "fact_inscripciones\n+ dimensiones",
            "color": "#FEF3C7",
            "borde": "#CA8A04",
            "x": 0.65,
            "y": 0.55,
        },
        {
            "titulo": "DuckDB",
            "sub": "Motor OLAP",
            "detalle": "Consulta columnar\nsobre Parquet",
            "color": "#DCFCE7",
            "borde": "#16A34A",
            "x": 0.80,
            "y": 0.55,
        },
    ]

    box_w = 0.12
    box_h = 0.23

    for i, etapa in enumerate(etapas):
        x = etapa["x"]
        y = etapa["y"]

        shadow = FancyBboxPatch(
            (x + 0.008, y - 0.008),
            box_w,
            box_h,
            boxstyle="round,pad=0.018,rounding_size=0.025",
            linewidth=0,
            facecolor="#CBD5E1",
            alpha=0.45
        )
        ax.add_patch(shadow)

        box = FancyBboxPatch(
            (x, y),
            box_w,
            box_h,
            boxstyle="round,pad=0.018,rounding_size=0.025",
            linewidth=1.8,
            edgecolor=etapa["borde"],
            facecolor=etapa["color"]
        )
        ax.add_patch(box)

        ax.text(
            x + box_w / 2,
            y + box_h - 0.045,
            etapa["titulo"],
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color="#0F172A"
        )

        ax.text(
            x + box_w / 2,
            y + box_h - 0.090,
            etapa["sub"],
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color=etapa["borde"]
        )

        ax.text(
            x + box_w / 2,
            y + 0.065,
            etapa["detalle"],
            ha="center",
            va="center",
            fontsize=8.8,
            color="#334155"
        )

        if i < len(etapas) - 1:
            start_x = x + box_w + 0.018
            end_x = etapas[i + 1]["x"] - 0.018
            arrow_y = y + box_h / 2

            ax.annotate(
                "",
                xy=(end_x, arrow_y),
                xytext=(start_x, arrow_y),
                arrowprops=dict(
                    arrowstyle="->",
                    lw=2.2,
                    color="#334155"
                )
            )

    # Bloque inferior de salidas analíticas
    output_x = 0.35
    output_y = 0.18
    output_w = 0.42
    output_h = 0.16

    output = FancyBboxPatch(
        (output_x, output_y),
        output_w,
        output_h,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.8,
        edgecolor="#7C3AED",
        facecolor="#EDE9FE"
    )
    ax.add_patch(output)

    ax.text(
        output_x + output_w / 2,
        output_y + output_h - 0.045,
        "Capa de Consumo Analítico",
        ha="center",
        va="center",
        fontsize=13,
        fontweight="bold",
        color="#4C1D95"
    )

    ax.text(
        output_x + output_w / 2,
        output_y + 0.060,
        "Consultas analíticas · CSV · Benchmark · Reporte de calidad · Insights operacionales",
        ha="center",
        va="center",
        fontsize=10,
        color="#334155"
    )

    # Flecha DuckDB hacia consumo
    ax.annotate(
        "",
        xy=(output_x + output_w / 2, output_y + output_h),
        xytext=(0.86, 0.55),
        arrowprops=dict(
            arrowstyle="->",
            lw=2.0,
            color="#7C3AED",
            connectionstyle="arc3,rad=-0.25"
        )
    )

    # Nota técnica
    ax.text(
        0.5,
        0.08,
        "Separación OLTP/OLAP: el sistema operacional conserva transacciones; el Lakehouse optimiza análisis histórico y agregaciones.",
        ha="center",
        va="center",
        fontsize=10,
        color="#64748B",
        style="italic"
    )

    plt.savefig(DOCS / "arquitectura.png", dpi=220, bbox_inches="tight")
    plt.close()


# =========================================================
# MODELO ESTRELLA TIPO POWER BI / SQL
# =========================================================

def draw_table(ax, name, fields, x, y, w, row_h, header_color):
    total_h = row_h * (len(fields) + 1)

    outer = FancyBboxPatch(
        (x, y - total_h),
        w,
        total_h,
        boxstyle="round,pad=0.005,rounding_size=0.008",
        linewidth=1.2,
        edgecolor="#94A3B8",
        facecolor="white"
    )
    ax.add_patch(outer)

    header = Rectangle(
        (x, y - row_h),
        w,
        row_h,
        linewidth=0,
        facecolor=header_color
    )
    ax.add_patch(header)

    ax.text(
        x + w / 2,
        y - row_h / 2,
        name,
        ha="center",
        va="center",
        fontsize=10.5,
        fontweight="bold",
        color="white"
    )

    ports = {}

    for i, (kind, field) in enumerate(fields):
        row_y = y - row_h * (i + 2)

        bg = "#F8FAFC" if i % 2 == 0 else "#FFFFFF"

        rect = Rectangle(
            (x, row_y),
            w,
            row_h,
            linewidth=0.6,
            edgecolor="#CBD5E1",
            facecolor=bg
        )
        ax.add_patch(rect)

        key_color = "#DC2626" if kind == "PK" else "#2563EB" if kind == "FK" else "#64748B"

        ax.text(
            x + 0.018,
            row_y + row_h / 2,
            kind,
            ha="left",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            color=key_color
        )

        ax.text(
            x + 0.075,
            row_y + row_h / 2,
            field,
            ha="left",
            va="center",
            fontsize=8.5,
            color="#0F172A"
        )

        ports[field] = {
            "left": (x, row_y + row_h / 2),
            "right": (x + w, row_y + row_h / 2),
            "center": (x + w / 2, row_y + row_h / 2),
        }

    return ports


def connect(ax, p1, p2, label=None):
    con = ConnectionPatch(
        xyA=p1,
        xyB=p2,
        coordsA="data",
        coordsB="data",
        arrowstyle="-",
        linewidth=1.5,
        color="#334155",
        connectionstyle="angle3,angleA=0,angleB=90"
    )
    ax.add_artist(con)

    if label:
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        ax.text(
            mx,
            my + 0.015,
            label,
            fontsize=8,
            color="#475569",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none")
        )


def generar_modelo_estrella():
    fig, ax = plt.subplots(figsize=(17, 10))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    row_h = 0.035

    fact_fields = [
        ("PK", "inscripcion_id"),
        ("FK", "tiempo_sk"),
        ("FK", "estudiante_sk"),
        ("FK", "curso_sk"),
        ("FK", "sede_sk"),
        ("FK", "resultado_sk"),
        ("", "duracion_ms"),
        ("", "hubo_retry"),
        ("", "hubo_timeout"),
        ("", "inscripcion_exitosa"),
        ("", "fue_rechazada"),
    ]

    tiempo_fields = [
        ("PK", "tiempo_sk"),
        ("", "fecha_completa"),
        ("", "anio"),
        ("", "mes"),
        ("", "dia"),
        ("", "hora"),
        ("", "franja_horaria"),
    ]

    estudiante_fields = [
        ("PK", "estudiante_sk"),
        ("", "student_id"),
        ("", "nombre"),
        ("", "facultad"),
        ("", "semestre"),
        ("", "sede"),
        ("", "valido_desde"),
        ("", "valido_hasta"),
        ("", "registro_activo"),
    ]

    curso_fields = [
        ("PK", "curso_sk"),
        ("", "codigo_curso"),
        ("", "nombre_curso"),
        ("", "facultad"),
        ("", "cupos_totales"),
    ]

    sede_fields = [
        ("PK", "sede_sk"),
        ("", "sede"),
        ("", "latencia_promedio"),
    ]

    resultado_fields = [
        ("PK", "resultado_sk"),
        ("", "resultado"),
    ]

    # Posiciones tipo Power BI
    fact = draw_table(ax, "fact_inscripciones", fact_fields, 0.39, 0.78, 0.23, row_h, "#DC2626")

    tiempo = draw_table(ax, "dim_tiempo", tiempo_fields, 0.07, 0.88, 0.23, row_h, "#2563EB")
    sede = draw_table(ax, "dim_sede", sede_fields, 0.07, 0.38, 0.23, row_h, "#2563EB")

    estudiante = draw_table(ax, "dim_estudiante", estudiante_fields, 0.72, 0.92, 0.23, row_h, "#2563EB")
    curso = draw_table(ax, "dim_curso", curso_fields, 0.72, 0.55, 0.23, row_h, "#2563EB")
    resultado = draw_table(ax, "dim_resultado", resultado_fields, 0.72, 0.25, 0.23, row_h, "#2563EB")

    # Conexiones FK -> PK exactas
    connect(ax, fact["tiempo_sk"]["left"], tiempo["tiempo_sk"]["right"], "N:1")
    connect(ax, fact["sede_sk"]["left"], sede["sede_sk"]["right"], "N:1")

    connect(ax, fact["estudiante_sk"]["right"], estudiante["estudiante_sk"]["left"], "N:1")
    connect(ax, fact["curso_sk"]["right"], curso["curso_sk"]["left"], "N:1")
    connect(ax, fact["resultado_sk"]["right"], resultado["resultado_sk"]["left"], "N:1")

    ax.text(
        0.5,
        0.98,
        "Modelo Estrella - Inscripciones UdeA",
        ha="center",
        va="top",
        fontsize=18,
        fontweight="bold",
        color="#0F172A"
    )

    ax.text(
        0.5,
        0.94,
        "Relaciones campo a campo entre claves foráneas de la tabla de hechos y claves primarias de dimensiones",
        ha="center",
        va="top",
        fontsize=10.5,
        color="#475569"
    )

    # Leyenda
    legend_x = 0.39
    legend_y = 0.08
    ax.text(legend_x, legend_y, "PK", color="#DC2626", fontsize=10, fontweight="bold")
    ax.text(legend_x + 0.035, legend_y, "Primary Key", color="#0F172A", fontsize=10)
    ax.text(legend_x + 0.17, legend_y, "FK", color="#2563EB", fontsize=10, fontweight="bold")
    ax.text(legend_x + 0.205, legend_y, "Foreign Key", color="#0F172A", fontsize=10)

    plt.savefig(DOCS / "modelo_estrella.png", dpi=220, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    generar_arquitectura()
    generar_modelo_estrella()

    print("====================================")
    print("DIAGRAMAS GENERADOS CORRECTAMENTE")
    print("====================================")
    print("docs/arquitectura.png")
    print("docs/modelo_estrella.png")