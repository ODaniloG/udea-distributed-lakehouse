import pandas as pd
import duckdb
import time
from pathlib import Path

DOCS = Path("docs")
DOCS.mkdir(parents=True, exist_ok=True)

# =========================================================
# BENCHMARK 1: PANDAS SOBRE SILVER
# Simula consulta analítica sobre fuente operacional
# =========================================================

print("Ejecutando benchmark con pandas sobre Silver...")

inicio = time.time()

inscripciones = pd.read_parquet("lakehouse/silver/inscripciones_silver.parquet")

resultado_pandas = (
    inscripciones
    .assign(hora=inscripciones["fecha_inscripcion"].dt.hour)
    .groupby("hora")
    .agg(
        total_intentos=("inscripcion_id", "count"),
        latencia_promedio_ms=("latencia_ms", "mean")
    )
    .reset_index()
)

tiempo_pandas_ms = (time.time() - inicio) * 1000

# =========================================================
# BENCHMARK 2: DUCKDB SOBRE GOLD
# Consulta columnar sobre modelo dimensional
# =========================================================

print("Ejecutando benchmark con DuckDB sobre Gold...")

con = duckdb.connect()

con.execute("""
CREATE OR REPLACE VIEW fact_inscripciones AS
SELECT * FROM read_parquet('lakehouse/gold/fact_inscripciones.parquet')
""")

con.execute("""
CREATE OR REPLACE VIEW dim_tiempo AS
SELECT * FROM read_parquet('lakehouse/gold/dim_tiempo.parquet')
""")

query_duckdb = """
SELECT
    t.hora,
    COUNT(*) AS total_intentos,
    AVG(f.duracion_ms) AS latencia_promedio_ms
FROM fact_inscripciones f
JOIN dim_tiempo t ON f.tiempo_sk = t.tiempo_sk
GROUP BY t.hora
ORDER BY t.hora
"""

inicio = time.time()

resultado_duckdb = con.execute(query_duckdb).fetchdf()

tiempo_duckdb_ms = (time.time() - inicio) * 1000

# =========================================================
# RESULTADOS
# =========================================================

if tiempo_duckdb_ms > 0:
    factor = tiempo_pandas_ms / tiempo_duckdb_ms
else:
    factor = 0

reporte = []

reporte.append("BENCHMARK - MINI LAKEHOUSE UDEA")
reporte.append("===============================")
reporte.append("")
reporte.append("Consulta comparada:")
reporte.append("Total de intentos y latencia promedio por hora.")
reporte.append("")
reporte.append("Resultados:")
reporte.append(f"Pandas sobre Silver : {tiempo_pandas_ms:.2f} ms")
reporte.append(f"DuckDB sobre Gold   : {tiempo_duckdb_ms:.2f} ms")
reporte.append(f"Factor de mejora    : {factor:.2f}x")
reporte.append("")
reporte.append("Interpretacion:")
reporte.append(
    "DuckDB ejecuta la consulta sobre archivos Parquet en formato columnar, "
    "lo que reduce el volumen de columnas leidas y mejora el rendimiento "
    "en consultas analiticas agregadas. Pandas representa una lectura mas "
    "operacional y menos optimizada para workloads OLAP."
)

with open(DOCS / "benchmark.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(reporte))

resultado_pandas.to_csv(DOCS / "benchmark_pandas.csv", index=False)
resultado_duckdb.to_csv(DOCS / "benchmark_duckdb.csv", index=False)

print("\n====================================")
print("BENCHMARK COMPLETADO")
print("====================================")
print(f"Pandas sobre Silver : {tiempo_pandas_ms:.2f} ms")
print(f"DuckDB sobre Gold   : {tiempo_duckdb_ms:.2f} ms")
print(f"Factor de mejora    : {factor:.2f}x")
print("")
print("Archivos creados:")
print("docs/benchmark.txt")
print("docs/benchmark_pandas.csv")
print("docs/benchmark_duckdb.csv")