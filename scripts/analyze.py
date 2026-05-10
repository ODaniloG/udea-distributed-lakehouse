import duckdb
from pathlib import Path

# =========================================================
# CONFIGURACION
# =========================================================

DOCS = Path("docs")
DOCS.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()

# =========================================================
# CREAR VISTAS SOBRE GOLD
# DuckDB lee Parquet directamente
# =========================================================

print("Registrando tablas Gold en DuckDB...")

con.execute("""
CREATE OR REPLACE VIEW fact_inscripciones AS
SELECT * FROM read_parquet('lakehouse/gold/fact_inscripciones.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_tiempo AS
SELECT * FROM read_parquet('lakehouse/gold/dim_tiempo.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_estudiante AS
SELECT * FROM read_parquet('lakehouse/gold/dim_estudiante.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_curso AS
SELECT * FROM read_parquet('lakehouse/gold/dim_curso.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_sede AS
SELECT * FROM read_parquet('lakehouse/gold/dim_sede.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_resultado AS
SELECT * FROM read_parquet('lakehouse/gold/dim_resultado.parquet')
""")

# =========================================================
# CONSULTAS ANALITICAS
# =========================================================

consultas = {}

# Consulta 1
consultas["01_inscripciones_por_hora"] = """
SELECT
    t.fecha_completa::DATE AS fecha,
    t.hora,
    COUNT(*) AS total_intentos,
    SUM(CASE WHEN f.inscripcion_exitosa THEN 1 ELSE 0 END) AS exitosas,
    SUM(CASE WHEN f.fue_rechazada THEN 1 ELSE 0 END) AS rechazadas,
    SUM(CASE WHEN f.hubo_retry THEN 1 ELSE 0 END) AS retries,
    SUM(CASE WHEN f.hubo_timeout THEN 1 ELSE 0 END) AS timeouts
FROM fact_inscripciones f
JOIN dim_tiempo t ON f.tiempo_sk = t.tiempo_sk
GROUP BY fecha, t.hora
ORDER BY total_intentos DESC
LIMIT 10
"""

# Consulta 2
consultas["02_cursos_con_mayor_contencion"] = """
SELECT
    c.codigo_curso,
    c.nombre_curso,
    c.facultad,
    COUNT(*) AS total_intentos,
    SUM(CASE WHEN f.fue_rechazada THEN 1 ELSE 0 END) AS rechazos_cupo,
    SUM(CASE WHEN f.hubo_retry THEN 1 ELSE 0 END) AS retries,
    SUM(CASE WHEN f.hubo_timeout THEN 1 ELSE 0 END) AS timeouts,
    ROUND(AVG(f.duracion_ms), 2) AS latencia_promedio_ms
FROM fact_inscripciones f
JOIN dim_curso c ON f.curso_sk = c.curso_sk
GROUP BY c.codigo_curso, c.nombre_curso, c.facultad
ORDER BY total_intentos DESC
LIMIT 10
"""

# Consulta 3
consultas["03_latencia_por_sede"] = """
SELECT
    s.sede,
    COUNT(*) AS total_intentos,
    ROUND(AVG(f.duracion_ms), 2) AS latencia_promedio_ms,
    MIN(f.duracion_ms) AS latencia_minima_ms,
    MAX(f.duracion_ms) AS latencia_maxima_ms,
    SUM(CASE WHEN f.hubo_timeout THEN 1 ELSE 0 END) AS total_timeouts
FROM fact_inscripciones f
JOIN dim_sede s ON f.sede_sk = s.sede_sk
GROUP BY s.sede
ORDER BY latencia_promedio_ms DESC
"""

# Consulta 4
consultas["04_tasa_exito_por_facultad"] = """
SELECT
    c.facultad,
    COUNT(*) AS total_intentos,
    SUM(CASE WHEN f.inscripcion_exitosa THEN 1 ELSE 0 END) AS exitosas,
    ROUND(
        SUM(CASE WHEN f.inscripcion_exitosa THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS tasa_exito_pct,
    ROUND(AVG(f.duracion_ms), 2) AS latencia_promedio_ms
FROM fact_inscripciones f
JOIN dim_curso c ON f.curso_sk = c.curso_sk
GROUP BY c.facultad
ORDER BY tasa_exito_pct ASC
"""

# Consulta 5
consultas["05_resultados_operacionales"] = """
SELECT
    r.resultado,
    COUNT(*) AS total_eventos,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS porcentaje
FROM fact_inscripciones f
JOIN dim_resultado r ON f.resultado_sk = r.resultado_sk
GROUP BY r.resultado
ORDER BY total_eventos DESC
"""

# =========================================================
# EJECUTAR CONSULTAS Y GUARDAR RESULTADOS
# =========================================================

salida = []

salida.append("RESULTADOS ANALITICOS - MINI LAKEHOUSE UDEA")
salida.append("============================================")
salida.append("")

for nombre, sql in consultas.items():
    print(f"Ejecutando {nombre}...")

    df = con.execute(sql).fetchdf()

    salida.append("")
    salida.append(nombre.upper())
    salida.append("-" * len(nombre))
    salida.append(df.to_string(index=False))
    salida.append("")

    df.to_csv(DOCS / f"{nombre}.csv", index=False, encoding="utf-8")

with open(DOCS / "resultados_analiticos.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(salida))

print("\n====================================")
print("ANALISIS COMPLETADO")
print("====================================")
print("Resultados guardados en:")
print("docs/resultados_analiticos.txt")
print("docs/*.csv")