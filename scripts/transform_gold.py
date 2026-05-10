import pandas as pd
from pathlib import Path

# =========================================================
# RUTAS
# =========================================================

SILVER = Path("lakehouse/silver")
GOLD = Path("lakehouse/gold")

GOLD.mkdir(parents=True, exist_ok=True)

# =========================================================
# LEER DATOS SILVER
# =========================================================

print("Leyendo Silver...")

estudiantes = pd.read_parquet(
    SILVER / "estudiantes_silver.parquet"
)

cursos = pd.read_parquet(
    SILVER / "cursos_silver.parquet"
)

inscripciones = pd.read_parquet(
    SILVER / "inscripciones_silver.parquet"
)

# =========================================================
# DIMENSION TIEMPO
# =========================================================

print("Construyendo dim_tiempo...")

dim_tiempo = pd.DataFrame()

dim_tiempo["fecha_completa"] = pd.to_datetime(
    inscripciones["fecha_inscripcion"]
)

dim_tiempo = dim_tiempo.drop_duplicates()

dim_tiempo["tiempo_sk"] = range(1, len(dim_tiempo) + 1)

dim_tiempo["anio"] = dim_tiempo["fecha_completa"].dt.year
dim_tiempo["mes"] = dim_tiempo["fecha_completa"].dt.month
dim_tiempo["dia"] = dim_tiempo["fecha_completa"].dt.day
dim_tiempo["hora"] = dim_tiempo["fecha_completa"].dt.hour
dim_tiempo["minuto"] = dim_tiempo["fecha_completa"].dt.minute
dim_tiempo["dia_semana"] = dim_tiempo["fecha_completa"].dt.day_name()

# =========================================================
# FRANJA HORARIA
# =========================================================

def clasificar_franja(hora):

    if 6 <= hora < 12:
        return "MANANA"

    elif 12 <= hora < 18:
        return "TARDE"

    else:
        return "NOCHE"

dim_tiempo["franja_horaria"] = dim_tiempo["hora"].apply(
    clasificar_franja
)

# =========================================================
# DIMENSION ESTUDIANTE
# SCD TIPO 2 SIMPLIFICADO
# =========================================================

print("Construyendo dim_estudiante...")

dim_estudiante = estudiantes.copy()

dim_estudiante["estudiante_sk"] = range(
    1,
    len(dim_estudiante) + 1
)

# SCD Tipo 2
dim_estudiante["valido_desde"] = "2026-01-01"
dim_estudiante["valido_hasta"] = "9999-12-31"
dim_estudiante["registro_activo"] = True

# =========================================================
# DIMENSION CURSO
# =========================================================

print("Construyendo dim_curso...")

dim_curso = cursos.copy()

dim_curso["curso_sk"] = range(
    1,
    len(dim_curso) + 1
)

# =========================================================
# DIMENSION SEDE
# =========================================================

print("Construyendo dim_sede...")

sedes = inscripciones[["sede"]].drop_duplicates()

sedes = sedes.reset_index(drop=True)

sedes["sede_sk"] = range(1, len(sedes) + 1)

# Latencia promedio estimada
latencias = {
    "Medellin": 120,
    "Uraba": 340,
    "Oriente": 280,
    "Bajo Cauca": 390
}

sedes["latencia_promedio"] = sedes["sede"].map(latencias)

# =========================================================
# DIMENSION RESULTADO
# =========================================================

print("Construyendo dim_resultado...")

resultados = inscripciones[["resultado"]].drop_duplicates()

resultados = resultados.reset_index(drop=True)

resultados["resultado_sk"] = range(
    1,
    len(resultados) + 1
)

# =========================================================
# TABLA DE HECHOS
# =========================================================

print("Construyendo fact_inscripciones...")

fact = inscripciones.copy()

# =========================================================
# JOIN TIEMPO
# =========================================================

fact = fact.merge(
    dim_tiempo[
        ["tiempo_sk", "fecha_completa"]
    ],
    left_on="fecha_inscripcion",
    right_on="fecha_completa",
    how="left"
)

# =========================================================
# JOIN ESTUDIANTE
# =========================================================

fact = fact.merge(
    dim_estudiante[
        ["student_id", "estudiante_sk"]
    ],
    on="student_id",
    how="left"
)

# =========================================================
# JOIN CURSO
# =========================================================

fact = fact.merge(
    dim_curso[
        ["codigo_curso", "curso_sk"]
    ],
    on="codigo_curso",
    how="left"
)

# =========================================================
# JOIN SEDE
# =========================================================

fact = fact.merge(
    sedes[
        ["sede", "sede_sk"]
    ],
    on="sede",
    how="left"
)

# =========================================================
# JOIN RESULTADO
# =========================================================

fact = fact.merge(
    resultados[
        ["resultado", "resultado_sk"]
    ],
    on="resultado",
    how="left"
)

# =========================================================
# MEDIDAS ANALITICAS
# =========================================================

fact["inscripcion_exitosa"] = (
    fact["resultado"] == "EXITOSA"
)

fact["fue_rechazada"] = (
    fact["resultado"] == "CUPO_AGOTADO"
)

fact["duracion_ms"] = fact["latencia_ms"]

# =========================================================
# COLUMNAS FINALES FACT
# =========================================================

fact_inscripciones = fact[
    [
        "inscripcion_id",
        "tiempo_sk",
        "estudiante_sk",
        "curso_sk",
        "sede_sk",
        "resultado_sk",
        "duracion_ms",
        "hubo_retry",
        "hubo_timeout",
        "inscripcion_exitosa",
        "fue_rechazada"
    ]
]

# =========================================================
# GUARDAR GOLD
# =========================================================

print("Guardando tablas Gold...")

dim_tiempo.to_parquet(
    GOLD / "dim_tiempo.parquet",
    index=False
)

dim_estudiante.to_parquet(
    GOLD / "dim_estudiante.parquet",
    index=False
)

dim_curso.to_parquet(
    GOLD / "dim_curso.parquet",
    index=False
)

sedes.to_parquet(
    GOLD / "dim_sede.parquet",
    index=False
)

resultados.to_parquet(
    GOLD / "dim_resultado.parquet",
    index=False
)

fact_inscripciones.to_parquet(
    GOLD / "fact_inscripciones.parquet",
    index=False
)

# =========================================================
# RESUMEN
# =========================================================

print("\n====================================")
print("ZONA GOLD GENERADA")
print("====================================")

print(f"dim_tiempo          : {len(dim_tiempo):,}")
print(f"dim_estudiante      : {len(dim_estudiante):,}")
print(f"dim_curso           : {len(dim_curso):,}")
print(f"dim_sede            : {len(sedes):,}")
print(f"dim_resultado       : {len(resultados):,}")
print(f"fact_inscripciones  : {len(fact_inscripciones):,}")

print("\nArchivos creados en:")
print("lakehouse/gold/")