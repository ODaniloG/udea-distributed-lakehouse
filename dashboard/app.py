import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Mini-Lakehouse UdeA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# ESTILOS
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #e5e7eb;
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #334155;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc;
        font-size: 30px;
    }

    .block-container {
        padding-top: 2rem;
    }

    .section-card {
        background-color: #111827;
        border: 1px solid #334155;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 18px;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 16px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CARGA DE DATOS
# =========================================================

@st.cache_data
def cargar_datos():
    con = duckdb.connect()

    fact = con.execute("""
    SELECT *
    FROM read_parquet('lakehouse/gold/fact_inscripciones.parquet')
    """).df()

    dim_curso = con.execute("""
    SELECT *
    FROM read_parquet('lakehouse/gold/dim_curso.parquet')
    """).df()

    dim_tiempo = con.execute("""
    SELECT *
    FROM read_parquet('lakehouse/gold/dim_tiempo.parquet')
    """).df()

    dim_sede = con.execute("""
    SELECT *
    FROM read_parquet('lakehouse/gold/dim_sede.parquet')
    """).df()

    dim_resultado = con.execute("""
    SELECT *
    FROM read_parquet('lakehouse/gold/dim_resultado.parquet')
    """).df()

    df = fact.merge(dim_curso, on="curso_sk", how="left")
    df = df.merge(dim_tiempo, on="tiempo_sk", how="left")
    df = df.merge(dim_sede, on="sede_sk", how="left")
    df = df.merge(dim_resultado, on="resultado_sk", how="left")

    return df


df = cargar_datos()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎓 UdeA Lakehouse")
st.sidebar.caption("Panel analítico de matrículas")

facultades = sorted(df["facultad"].dropna().unique())
sedes = sorted(df["sede"].dropna().unique())
resultados = sorted(df["resultado"].dropna().unique())

facultad_sel = st.sidebar.multiselect(
    "Facultad",
    facultades,
    default=facultades
)

sede_sel = st.sidebar.multiselect(
    "Sede",
    sedes,
    default=sedes
)

resultado_sel = st.sidebar.multiselect(
    "Resultado",
    resultados,
    default=resultados
)

df_filtrado = df[
    df["facultad"].isin(facultad_sel) &
    df["sede"].isin(sede_sel) &
    df["resultado"].isin(resultado_sel)
]

st.sidebar.divider()
st.sidebar.markdown("### Capas Lakehouse")
st.sidebar.success("Bronze: datos crudos")
st.sidebar.info("Silver: datos limpios")
st.sidebar.warning("Gold: modelo dimensional")

# =========================================================
# ENCABEZADO
# =========================================================

st.title("🎓 Mini-Lakehouse UdeA")
st.markdown(
    "<div class='subtitle'>Analítica de matrículas distribuidas, hotspots de cursos, retries, timeouts y latencia regional.</div>",
    unsafe_allow_html=True
)

# =========================================================
# KPIS
# =========================================================

total = len(df_filtrado)
exitosas = int(df_filtrado["inscripcion_exitosa"].sum())
retries = int(df_filtrado["hubo_retry"].sum())
timeouts = int(df_filtrado["hubo_timeout"].sum())
rechazadas = int(df_filtrado["fue_rechazada"].sum())
latencia = round(df_filtrado["duracion_ms"].mean(), 2) if total > 0 else 0

tasa_exito = round((exitosas / total) * 100, 2) if total > 0 else 0
tasa_fallo = round(((retries + timeouts + rechazadas) / total) * 100, 2) if total > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Intentos", f"{total:,}")
col2.metric("Exitosas", f"{exitosas:,}", f"{tasa_exito}%")
col3.metric("Retries", f"{retries:,}")
col4.metric("Timeouts", f"{timeouts:,}")
col5.metric("Rechazos", f"{rechazadas:,}")
col6.metric("Latencia", f"{latencia} ms")

st.divider()

# =========================================================
# TEMA PLOTLY
# =========================================================

def aplicar_layout(fig, titulo):
    fig.update_layout(
        title=titulo,
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#e5e7eb"),
        title_font=dict(size=18, color="#f8fafc"),
        margin=dict(l=30, r=30, t=60, b=30),
        xaxis=dict(gridcolor="#334155"),
        yaxis=dict(gridcolor="#334155"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb")
        )
    )
    return fig


# =========================================================
# GRÁFICAS PRINCIPALES
# =========================================================

top_cursos = (
    df_filtrado.groupby(["codigo_curso", "nombre_curso"])
    .size()
    .reset_index(name="intentos")
    .sort_values("intentos", ascending=False)
    .head(10)
)

fig_cursos = px.bar(
    top_cursos,
    x="intentos",
    y="codigo_curso",
    orientation="h",
    text="intentos",
    color="intentos",
    color_continuous_scale="Blues"
)
fig_cursos.update_traces(textposition="outside")
fig_cursos.update_yaxes(autorange="reversed")
fig_cursos = aplicar_layout(fig_cursos, "Top 10 cursos con mayor demanda")


por_hora = (
    df_filtrado.groupby("hora")
    .agg(
        intentos=("inscripcion_id", "count"),
        retries=("hubo_retry", "sum"),
        timeouts=("hubo_timeout", "sum")
    )
    .reset_index()
)

fig_hora = go.Figure()
fig_hora.add_trace(go.Scatter(
    x=por_hora["hora"],
    y=por_hora["intentos"],
    mode="lines+markers",
    name="Intentos",
    line=dict(width=3)
))
fig_hora.add_trace(go.Scatter(
    x=por_hora["hora"],
    y=por_hora["retries"],
    mode="lines+markers",
    name="Retries",
    line=dict(width=2, dash="dot")
))
fig_hora.add_trace(go.Scatter(
    x=por_hora["hora"],
    y=por_hora["timeouts"],
    mode="lines+markers",
    name="Timeouts",
    line=dict(width=2, dash="dash")
))
fig_hora = aplicar_layout(fig_hora, "Comportamiento por hora")


latencia_sede = (
    df_filtrado.groupby("sede")
    .agg(
        latencia_promedio=("duracion_ms", "mean"),
        intentos=("inscripcion_id", "count")
    )
    .reset_index()
)

fig_sede = px.bar(
    latencia_sede,
    x="sede",
    y="latencia_promedio",
    text=latencia_sede["latencia_promedio"].round(2),
    color="latencia_promedio",
    color_continuous_scale="Oranges"
)
fig_sede.update_traces(textposition="outside")
fig_sede = aplicar_layout(fig_sede, "Latencia promedio por sede")


resultado_dist = (
    df_filtrado.groupby("resultado")
    .size()
    .reset_index(name="eventos")
)

fig_resultado = px.pie(
    resultado_dist,
    names="resultado",
    values="eventos",
    hole=0.55
)
fig_resultado = aplicar_layout(fig_resultado, "Distribución de resultados operacionales")


facultad = (
    df_filtrado.groupby("facultad")
    .agg(
        intentos=("inscripcion_id", "count"),
        exitosas=("inscripcion_exitosa", "sum"),
        retries=("hubo_retry", "sum"),
        timeouts=("hubo_timeout", "sum"),
        rechazos=("fue_rechazada", "sum"),
        latencia_promedio=("duracion_ms", "mean")
    )
    .reset_index()
)

facultad["tasa_exito"] = round(facultad["exitosas"] * 100 / facultad["intentos"], 2)

fig_facultad = px.bar(
    facultad.sort_values("intentos", ascending=False),
    x="facultad",
    y=["exitosas", "retries", "timeouts", "rechazos"],
    barmode="stack"
)
fig_facultad = aplicar_layout(fig_facultad, "Resultado operacional por facultad")

# =========================================================
# LAYOUT VISUAL
# =========================================================

c1, c2 = st.columns([1.05, 1])

with c1:
    st.plotly_chart(fig_cursos, use_container_width=True)

with c2:
    st.plotly_chart(fig_hora, use_container_width=True)

c3, c4 = st.columns([1, 1])

with c3:
    st.plotly_chart(fig_sede, use_container_width=True)

with c4:
    st.plotly_chart(fig_resultado, use_container_width=True)

st.plotly_chart(fig_facultad, use_container_width=True)

# =========================================================
# ANÁLISIS EJECUTIVO
# =========================================================

st.subheader("📌 Lectura ejecutiva")

colA, colB, colC = st.columns(3)

with colA:
    st.markdown("""
    **Hotspots académicos**  
    Los cursos con mayor número de intentos representan puntos de alta contención durante matrícula.
    """)

with colB:
    st.markdown("""
    **Riesgo operacional**  
    Retries y timeouts permiten identificar presión transaccional, posibles bloqueos y degradación del servicio.
    """)

with colC:
    st.markdown("""
    **Impacto regional**  
    La latencia por sede permite comparar Medellín frente a sedes regionales con conectividad más variable.
    """)

# =========================================================
# TABLA DE DETALLE
# =========================================================

with st.expander("Ver datos analíticos Gold"):
    st.dataframe(
        df_filtrado.head(300),
        use_container_width=True
    )